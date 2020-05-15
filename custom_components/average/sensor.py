#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
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

import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.components import history
from homeassistant.components.climate import ClimateDevice
from homeassistant.components.water_heater import WaterHeaterDevice
from homeassistant.components.weather import WeatherEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_ENTITIES,
    EVENT_HOMEASSISTANT_START,
    ATTR_UNIT_OF_MEASUREMENT,
    UNIT_NOT_RECOGNIZED_TEMPLATE,
    TEMPERATURE,
    STATE_UNKNOWN,
    STATE_UNAVAILABLE,
    ATTR_ICON,
)
from homeassistant.core import callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.util import Throttle
from homeassistant.util.temperature import convert as convert_temperature
from homeassistant.util.unit_system import TEMPERATURE_UNITS

from .const import (
    CONF_PERIOD_KEYS,
    CONF_DURATION,
    DEFAULT_NAME,
    CONF_START,
    CONF_END,
    CONF_PRECISION,
    VERSION,
    ISSUE_URL,
    ATTR_TO_PROPERTY,
    UPDATE_MIN_TIME,
)

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
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            vol.Optional(CONF_START): cv.template,
            vol.Optional(CONF_END): cv.template,
            vol.Optional(CONF_DURATION): cv.time_period,
            vol.Optional(CONF_PRECISION, default=2): int,
        }
    ),
    check_period_keys,
)


# pylint: disable=unused-argument
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up platform."""
    # Print startup message
    _LOGGER.info("Version %s", VERSION)
    _LOGGER.info(
        "If you have ANY issues with this, please report them here: %s", ISSUE_URL
    )

    name = config.get(CONF_NAME)
    start = config.get(CONF_START)
    end = config.get(CONF_END)
    duration = config.get(CONF_DURATION)
    entities = config.get(CONF_ENTITIES)
    precision = config.get(CONF_PRECISION)

    for template in [start, end]:
        if template is not None:
            template.hass = hass

    async_add_entities(
        [AverageSensor(hass, name, start, end, duration, entities, precision)]
    )


# pylint: disable=r0902
class AverageSensor(Entity):
    """Implementation of an Average sensor."""

    # pylint: disable=r0913
    def __init__(
        self, hass, name: str, start, end, duration, entity_ids: list, precision: int,
    ):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._start_template = start
        self._end_template = end
        self._duration = duration
        self._period = self.start = self.end = None
        self._entity_ids = entity_ids
        self._precision = precision
        self._state = None
        self._unit_of_measurement = None
        self._icon = None
        self._temperature_mode = None
        self.count_sources = len(self._entity_ids)
        self.available_sources = 0
        self.count = 0
        self.min_value = self.max_value = None

    @property
    def _has_period(self) -> bool:
        """Return True if sensor has any period setting."""
        return (
            self._start_template is not None
            or self._end_template is not None
            or self._duration is not None
        )

    @property
    def should_poll(self):
        """Return the polling state."""
        return self._has_period

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        state_attr = {
            attr: getattr(self, attr)
            for attr in ATTR_TO_PROPERTY
            if getattr(self, attr) is not None
        }
        return state_attr

    async def async_added_to_hass(self):
        """Register callbacks."""
        # pylint: disable=unused-argument
        @callback
        def sensor_state_listener(entity, old_state, new_state):
            """Handle device state changes."""
            last_state = self._state
            self._update_state()
            if last_state != self._state:
                self.async_schedule_update_ha_state(True)

        # pylint: disable=unused-argument
        @callback
        def sensor_startup(event):
            """Update template on startup."""
            if self._has_period:
                self.async_schedule_update_ha_state(True)
            else:
                async_track_state_change(
                    self._hass, self._entity_ids, sensor_state_listener
                )
                sensor_state_listener(None, None, None)

        self._hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, sensor_startup)

    @staticmethod
    def _has_state(state) -> bool:
        """Return True if state has any value."""
        return state is not None and state not in [STATE_UNKNOWN, STATE_UNAVAILABLE]

    @staticmethod
    def _is_temperature(entity) -> bool:
        """Return True if entity are temperature sensor."""
        entity_unit = entity.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        return entity_unit in TEMPERATURE_UNITS or isinstance(
            entity, (WeatherEntity, ClimateDevice, WaterHeaterDevice)
        )

    def _get_temperature(self, entity) -> float:
        """Get temperature value from entity."""
        if isinstance(entity, WeatherEntity):
            temperature = entity.temperature
            entity_unit = entity.temperature_unit
        elif isinstance(entity, (ClimateDevice, WaterHeaterDevice)):
            temperature = entity.current_temperature
            entity_unit = entity.temperature_unit
        else:
            temperature = entity.state
            entity_unit = entity.attributes.get(ATTR_UNIT_OF_MEASUREMENT)

        if self._has_state(temperature):
            if entity_unit not in TEMPERATURE_UNITS:
                raise ValueError(
                    UNIT_NOT_RECOGNIZED_TEMPLATE.format(entity_unit, TEMPERATURE)
                )

            temperature = float(temperature)
            ha_unit = self._hass.config.units.temperature_unit

            if entity_unit != ha_unit:
                temperature = convert_temperature(temperature, entity_unit, ha_unit)

        return temperature

    def _get_entity_state(self, entity):
        """Return current state of given entity and count some sensor attributes."""
        state = (
            self._get_temperature(entity) if self._temperature_mode else entity.state
        )
        if not self._has_state(state):
            return None

        try:
            state = float(state)
        except ValueError:
            _LOGGER.error('Could not convert value "%s" to float', state)
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
    def update(self):
        """Update the sensor state if it needed."""
        if self._has_period:
            self._update_state()

    @staticmethod
    def handle_template_exception(ex, field):
        """Log an error nicely if the template cannot be interpreted."""
        if ex.args and ex.args[0].startswith("UndefinedError: 'None' has no attribute"):
            # Common during HA startup - so just a warning
            _LOGGER.warning(ex)
            return
        _LOGGER.error("Error parsing template for field %s", field)
        _LOGGER.error(ex)

    def _update_period(self):  # pylint: disable=r0912
        """Parse the templates and calculate a datetime tuples."""
        start = end = None
        now = dt_util.now()

        # Parse start
        _LOGGER.debug("Process start template: %s", self._start_template)
        if self._start_template is not None:
            try:
                start_rendered = self._start_template.render()
            except (TemplateError, TypeError) as ex:
                self.handle_template_exception(ex, "start")
                return
            start = dt_util.parse_datetime(start_rendered)
            if start is None:
                try:
                    start = dt_util.as_local(
                        dt_util.utc_from_timestamp(math.floor(float(start_rendered)))
                    )
                except ValueError:
                    _LOGGER.error(
                        "Parsing error: start must be a datetime" "or a timestamp"
                    )
                    return

        # Parse end
        _LOGGER.debug("Process end template: %s", self._end_template)
        if self._end_template is not None:
            try:
                end_rendered = self._end_template.render()
            except (TemplateError, TypeError) as ex:
                self.handle_template_exception(ex, "end")
                return
            end = dt_util.parse_datetime(end_rendered)
            if end is None:
                try:
                    end = dt_util.as_local(
                        dt_util.utc_from_timestamp(math.floor(float(end_rendered)))
                    )
                except ValueError:
                    _LOGGER.error(
                        "Parsing error: end must be a datetime " "or a timestamp"
                    )
                    return

        # Calculate start or end using the duration
        _LOGGER.debug("Process duration: %s", self._duration)
        if self._duration is not None:
            if start is None:
                if end is None:
                    end = now
                start = end - self._duration
            else:
                end = start + self._duration

        _LOGGER.debug("Start: %s, End: %s", start, end)
        if start is None or end is None:
            return

        if start > now:
            # History hasn't been written yet for this period
            return
        if now < end:
            # No point in making stats of the future
            end = now

        self._period = start, end
        self.start = start.replace(microsecond=0).isoformat()
        self.end = end.replace(microsecond=0).isoformat()

    def _update_state(self):  # pylint: disable=r0914,r0912,r0915
        """Update the sensor state."""
        _LOGGER.debug('Updating sensor "%s"', self.name)
        start = end = start_ts = end_ts = None
        p_period = self._period

        # Parse templates
        self._update_period()

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
        for entity_id in self._entity_ids:
            _LOGGER.debug('Processing entity "%s"', entity_id)

            entity = self._hass.states.get(entity_id)

            if entity is None:
                _LOGGER.error('Unable to find an entity "%s"', entity_id)
                continue

            if self._temperature_mode is None:
                self._temperature_mode = self._is_temperature(entity)
                if self._temperature_mode:
                    self._unit_of_measurement = self._hass.config.units.temperature_unit
                    self._icon = "mdi:thermometer"
                else:
                    self._unit_of_measurement = entity.attributes.get(
                        ATTR_UNIT_OF_MEASUREMENT
                    )
                    self._icon = entity.attributes.get(ATTR_ICON)

            value = 0
            elapsed = 0

            if self._period is None:
                # Get current state
                value = self._get_entity_state(entity)
                _LOGGER.debug("Current state: %s", value)

            else:
                # Get history between start and now
                history_list = history.state_changes_during_period(
                    self.hass, start, end, str(entity_id)
                )

                if entity_id not in history_list.keys():
                    value = self._get_entity_state(entity)
                    _LOGGER.warning(
                        'Historical data not found for entity "%s". '
                        "Current state used: %s",
                        entity_id,
                        value,
                    )
                else:
                    # Get the first state
                    item = history.get_state(self.hass, start, entity_id)
                    _LOGGER.debug("Initial historical state: %s", item)
                    last_state = None
                    last_time = start_ts
                    if item is not None and self._has_state(item.state):
                        last_state = self._get_entity_state(item)

                    # Get the other states
                    for item in history_list.get(entity_id):
                        _LOGGER.debug("Historical state: %s", item)
                        if self._has_state(item.state):
                            current_state = self._get_entity_state(item)
                            current_time = item.last_changed.timestamp()

                            if last_state:
                                last_elapsed = current_time - last_time
                                value += last_state * last_elapsed
                                elapsed += last_elapsed

                            last_state = current_state
                            last_time = current_time

                    # Count time elapsed between last history state and now
                    if last_state:
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
            self._state = round(sum(values) / len(values), self._precision)
        else:
            self._state = None
        _LOGGER.debug("Total average state: %s", self._state)
