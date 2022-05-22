#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

"""
The Average Sensor.

For more details about this sensor, please refer to the documentation at
https://github.com/Limych/ha-average/
"""
import datetime
import logging
import math
import numbers
from typing import Any, Mapping, Optional

import homeassistant.util.dt as dt_util
import voluptuous as vol
from _sha1 import sha1
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.group import expand_entity_ids
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT, SensorEntity
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ENTITIES,
    CONF_NAME,
    CONF_UNIQUE_ID,
    DEVICE_CLASS_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback, split_entity_id
from homeassistant.exceptions import TemplateError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.event import async_track_state_change
from homeassistant.util import Throttle
from homeassistant.util.temperature import convert as convert_temperature
from homeassistant.util.unit_system import TEMPERATURE_UNITS

from .const import (
    ATTR_TO_PROPERTY,
    CONF_DURATION,
    CONF_END,
    CONF_PERIOD_KEYS,
    CONF_PRECISION,
    CONF_PROCESS_UNDEF_AS,
    CONF_START,
    DEFAULT_NAME,
    DEFAULT_PRECISION,
    STARTUP_MESSAGE,
    UPDATE_MIN_TIME,
)

try:  # pragma: no cover
    # HA version >=2021.6
    from homeassistant.components.recorder import get_instance, history
    from homeassistant.components.recorder.models import LazyState
except ImportError:  # pragma: no cover
    # HA version <=2021.5
    from homeassistant.components import history
    from homeassistant.components.history import LazyState


_LOGGER = logging.getLogger(__name__)


def check_period_keys(conf):
    """Ensure maximum 2 of CONF_PERIOD_KEYS are provided."""
    count = sum(param in conf for param in CONF_PERIOD_KEYS)
    if (count == 1 and CONF_DURATION not in conf) or count > 2:
        raise vol.Invalid(
            "You must provide none, only "
            + CONF_DURATION
            + " or maximum 2 of the following: "
            ", ".join(CONF_PERIOD_KEYS)
        )
    return conf


PLATFORM_SCHEMA = vol.All(
    PLATFORM_SCHEMA.extend(
        {
            vol.Required(CONF_ENTITIES): cv.entity_ids,
            vol.Optional(CONF_UNIQUE_ID): cv.string,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            vol.Optional(CONF_START): cv.template,
            vol.Optional(CONF_END): cv.template,
            vol.Optional(CONF_DURATION): cv.positive_time_period,
            vol.Optional(CONF_PRECISION, default=DEFAULT_PRECISION): int,
            vol.Optional(CONF_PROCESS_UNDEF_AS): vol.Any(int, float),
        }
    ),
    check_period_keys,
)


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Set up platform."""
    # Print startup message
    _LOGGER.info(STARTUP_MESSAGE)

    start = config.get(CONF_START)
    end = config.get(CONF_END)

    for template in [start, end]:
        if template is not None:
            template.hass = hass

    async_add_entities(
        [
            AverageSensor(
                hass,
                config.get(CONF_UNIQUE_ID),
                config.get(CONF_NAME),
                start,
                end,
                config.get(CONF_DURATION),
                config.get(CONF_ENTITIES),
                config.get(CONF_PRECISION),
                config.get(CONF_PROCESS_UNDEF_AS),
            )
        ]
    )


# pylint: disable=too-many-instance-attributes
class AverageSensor(SensorEntity):
    """Implementation of an Average sensor."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        hass: HomeAssistant,
        unique_id: Optional[str],
        name: str,
        start,
        end,
        duration,
        entity_ids: list,
        precision: int,
        undef,
    ):
        """Initialize the sensor."""
        self._start_template = start
        self._end_template = end
        self._duration = duration
        self._period = self.start = self.end = None
        self._precision = precision
        self._undef = undef
        self._temperature_mode = None

        self.sources = expand_entity_ids(hass, entity_ids)
        self.count_sources = len(self.sources)
        self.available_sources = 0
        self.count = 0
        self.min_value = self.max_value = None

        self._attr_name = name
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = None
        self._attr_icon = None
        self._attr_state_class = STATE_CLASS_MEASUREMENT
        self._attr_device_class = None
        #
        self._attr_unique_id = (
            str(
                sha1(
                    ";".join(
                        [str(start), str(duration), str(end), ",".join(self.sources)]
                    ).encode("utf-8")
                ).hexdigest()
            )
            if unique_id == "__legacy__"
            else unique_id
        )

    @property
    def _has_period(self) -> bool:
        """Return True if sensor has any period setting."""
        return (
            self._start_template is not None
            or self._end_template is not None
            or self._duration is not None
        )

    @property
    def should_poll(self) -> bool:
        """Return the polling state."""
        return self._has_period

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.available_sources > 0 and self._has_state(self._attr_native_value)

    @property
    def extra_state_attributes(self) -> Optional[Mapping[str, Any]]:
        """Return entity specific state attributes."""
        state_attr = {
            attr: getattr(self, attr)
            for attr in ATTR_TO_PROPERTY
            if getattr(self, attr) is not None
        }
        return state_attr

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        # pylint: disable=unused-argument
        @callback
        async def async_sensor_state_listener(entity, old_state, new_state):
            """Handle device state changes."""
            last_state = self._attr_native_value
            await self._async_update_state()
            if last_state != self._attr_native_value:
                self.async_schedule_update_ha_state(True)

        # pylint: disable=unused-argument
        @callback
        async def async_sensor_startup(event):
            """Update template on startup."""
            if self._has_period:
                self.async_schedule_update_ha_state(True)
            else:
                async_track_state_change(
                    self.hass, self.sources, async_sensor_state_listener
                )
                await async_sensor_state_listener(None, None, None)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, async_sensor_startup)

    @staticmethod
    def _has_state(state) -> bool:
        """Return True if state has any value."""
        return state is not None and state not in [
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "None",
            "",
        ]

    def _get_temperature(self, state: LazyState) -> Optional[float]:
        """Get temperature value from entity."""
        ha_unit = self.hass.config.units.temperature_unit
        domain = split_entity_id(state.entity_id)[0]
        if domain == WEATHER_DOMAIN:
            temperature = state.attributes.get("temperature")
            entity_unit = ha_unit
        elif domain in (CLIMATE_DOMAIN, WATER_HEATER_DOMAIN):
            temperature = state.attributes.get("current_temperature")
            entity_unit = ha_unit
        else:
            temperature = state.state
            entity_unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)

        if not self._has_state(temperature):
            return None

        try:
            temperature = convert_temperature(float(temperature), entity_unit, ha_unit)
        except ValueError as exc:
            _LOGGER.error('Could not convert value "%s" to float: %s', state, exc)
            return None

        return temperature

    def _get_state_value(self, state: LazyState) -> Optional[float]:
        """Return value of given entity state and count some sensor attributes."""
        state = self._get_temperature(state) if self._temperature_mode else state.state
        if not self._has_state(state):
            return self._undef

        try:
            state = float(state)
        except ValueError as exc:
            _LOGGER.error('Could not convert value "%s" to float: %s', state, exc)
            return None

        self.count += 1
        rstate = round(state, self._precision)
        if self.min_value is None:
            self.min_value = self.max_value = rstate
        else:
            self.min_value = min(self.min_value, rstate)
            self.max_value = max(self.max_value, rstate)
        return state

    @Throttle(UPDATE_MIN_TIME)
    async def async_update(self):
        """Update the sensor state if it needed."""
        if self._has_period:
            await self._async_update_state()

    @staticmethod
    def handle_template_exception(exc, field):
        """Log an error nicely if the template cannot be interpreted."""
        if exc.args and exc.args[0].startswith(
            "UndefinedError: 'None' has no attribute"
        ):
            # Common during HA startup - so just a warning
            _LOGGER.warning(exc)

        else:
            _LOGGER.error('Error parsing template for field "%s": %s', field, exc)

    async def _async_update_period(self):  # pylint: disable=too-many-branches
        """Parse the templates and calculate a datetime tuples."""
        start = end = None
        now = dt_util.now()

        # Parse start
        if self._start_template is not None:
            _LOGGER.debug("Process start template: %s", self._start_template)
            try:
                start_rendered = self._start_template.async_render()
            except (TemplateError, TypeError) as ex:
                self.handle_template_exception(ex, "start")
                return
            if isinstance(start_rendered, str):
                start = dt_util.parse_datetime(start_rendered)
            if start is None:
                try:
                    start = dt_util.as_local(
                        dt_util.utc_from_timestamp(math.floor(float(start_rendered)))
                    )
                except ValueError:
                    _LOGGER.error(
                        'Parsing error: field "start" must be a datetime or a timestamp'
                    )
                    return

        # Parse end
        if self._end_template is not None:
            _LOGGER.debug("Process end template: %s", self._end_template)
            try:
                end_rendered = self._end_template.async_render()
            except (TemplateError, TypeError) as ex:
                self.handle_template_exception(ex, "end")
                return
            if isinstance(end_rendered, str):
                end = dt_util.parse_datetime(end_rendered)
            if end is None:
                try:
                    end = dt_util.as_local(
                        dt_util.utc_from_timestamp(math.floor(float(end_rendered)))
                    )
                except ValueError:
                    _LOGGER.error(
                        'Parsing error: field "end" must be a datetime or a timestamp'
                    )
                    return

        # Calculate start or end using the duration
        if self._duration is not None:
            _LOGGER.debug("Process duration: %s", self._duration)
            if start is None:
                if end is None:
                    end = now
                start = end - self._duration
            else:
                end = start + self._duration

        _LOGGER.debug("Calculation period: start=%s, end=%s", start, end)
        if start is None or end is None:
            return

        if start > end:
            start, end = end, start

        if start > now:
            # History hasn't been written yet for this period
            return
        if now < end:
            # No point in making stats of the future
            end = now

        self._period = start, end
        self.start = start.replace(microsecond=0).isoformat()
        self.end = end.replace(microsecond=0).isoformat()

    def _init_mode(self, state: LazyState):
        """Initialize sensor mode."""
        if self._temperature_mode is not None:
            return

        domain = split_entity_id(state.entity_id)[0]
        self._attr_device_class = state.attributes.get(ATTR_DEVICE_CLASS)
        self._attr_native_unit_of_measurement = state.attributes.get(
            ATTR_UNIT_OF_MEASUREMENT
        )
        self._temperature_mode = (
            self._attr_device_class == DEVICE_CLASS_TEMPERATURE
            or domain in (WEATHER_DOMAIN, CLIMATE_DOMAIN, WATER_HEATER_DOMAIN)
            or self._attr_native_unit_of_measurement in TEMPERATURE_UNITS
        )
        if self._temperature_mode:
            _LOGGER.debug("%s is a temperature entity.", state.entity_id)
            self._attr_device_class = DEVICE_CLASS_TEMPERATURE
            self._attr_native_unit_of_measurement = (
                self.hass.config.units.temperature_unit
            )
        else:
            _LOGGER.debug("%s is NOT a temperature entity.", state.entity_id)
            self._attr_icon = state.attributes.get(ATTR_ICON)

    async def _async_update_state(
        self,
    ):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """Update the sensor state."""
        _LOGGER.debug('Updating sensor "%s"', self.name)
        start = end = start_ts = end_ts = None
        p_period = self._period

        # Parse templates
        await self._async_update_period()

        if self._period is not None:
            now = datetime.datetime.now()
            start, end = self._period
            if p_period is None:
                p_start = p_end = now
            else:
                p_start, p_end = p_period

            # Convert times to UTC
            start = dt_util.as_utc(start)
            end = dt_util.as_utc(end)
            p_start = dt_util.as_utc(p_start)
            p_end = dt_util.as_utc(p_end)

            # Compute integer timestamps
            now_ts = math.floor(dt_util.as_timestamp(now))
            start_ts = math.floor(dt_util.as_timestamp(start))
            end_ts = math.floor(dt_util.as_timestamp(end))
            p_start_ts = math.floor(dt_util.as_timestamp(p_start))
            p_end_ts = math.floor(dt_util.as_timestamp(p_end))

            # If period has not changed and current time after the period end..
            if start_ts == p_start_ts and end_ts == p_end_ts and end_ts <= now_ts:
                # Don't compute anything as the value cannot have changed
                return

        self.available_sources = 0
        values = []
        self.count = 0
        self.min_value = self.max_value = None

        # pylint: disable=too-many-nested-blocks
        for entity_id in self.sources:
            _LOGGER.debug('Processing entity "%s"', entity_id)

            state = self.hass.states.get(entity_id)  # type: LazyState

            if state is None:
                _LOGGER.error('Unable to find an entity "%s"', entity_id)
                continue

            self._init_mode(state)

            value = 0
            elapsed = 0

            if self._period is None:
                # Get current state
                value = self._get_state_value(state)
                _LOGGER.debug("Current state: %s", value)

            else:
                # Get history between start and now
                history_list = await get_instance(self.hass).async_add_executor_job(
                    history.state_changes_during_period,
                    self.hass,
                    start,
                    end,
                    str(entity_id),
                )

                if (
                    entity_id not in history_list.keys()
                    or history_list[entity_id] is None
                    or len(history_list[entity_id]) == 0
                ):
                    value = self._get_state_value(state)
                    _LOGGER.warning(
                        'Historical data not found for entity "%s". '
                        "Current state used: %s",
                        entity_id,
                        value,
                    )
                else:
                    # Get the first state
                    item = history_list[entity_id][0]
                    _LOGGER.debug("Initial historical state: %s", item)
                    last_state = None
                    last_time = start_ts
                    if item is not None and self._has_state(item.state):
                        last_state = self._get_state_value(item)

                    # Get the other states
                    for item in history_list.get(entity_id):
                        _LOGGER.debug("Historical state: %s", item)
                        current_state = self._get_state_value(item)
                        current_time = item.last_changed.timestamp()

                        if last_state is not None:
                            last_elapsed = current_time - last_time
                            value += last_state * last_elapsed
                            elapsed += last_elapsed

                        last_state = current_state
                        last_time = current_time

                    # Count time elapsed between last history state and now
                    if last_state is not None:
                        last_elapsed = end_ts - last_time
                        value += last_state * last_elapsed
                        elapsed += last_elapsed

                    if elapsed:
                        value /= elapsed
                    _LOGGER.debug("Historical average state: %s", value)

            if isinstance(value, numbers.Number):
                values.append(value)
                self.available_sources += 1

        if values:
            self._attr_native_value = round(sum(values) / len(values), self._precision)
            if self._precision < 1:
                self._attr_native_value = int(self._attr_native_value)
        else:
            self._attr_native_value = None
        _LOGGER.debug("Total average state: %s", self._attr_native_value)
