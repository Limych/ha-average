#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

"""
The Average Sensor.

For more details about this sensor, please refer to the documentation at
https://github.com/Limych/ha-average/
"""
import logging
import math
from datetime import timedelta

import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.components import history
from homeassistant.components.climate import ClimateDevice
from homeassistant.components.water_heater import WaterHeaterDevice
from homeassistant.components.weather import WeatherEntity
from homeassistant.const import (
    CONF_NAME, CONF_ENTITIES, EVENT_HOMEASSISTANT_START,
    ATTR_UNIT_OF_MEASUREMENT,
    TEMP_CELSIUS, TEMP_FAHRENHEIT, UNIT_NOT_RECOGNIZED_TEMPLATE, TEMPERATURE,
    STATE_UNKNOWN, STATE_UNAVAILABLE, ATTR_ICON)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.util import Throttle
from homeassistant.util.temperature import convert as convert_temperature

VERSION = '1.3.4'

_LOGGER = logging.getLogger(__name__)

CONF_DURATION = 'duration'
CONF_PRECISION = 'precision'

DEFAULT_NAME = 'Average'

ATTR_COUNT = 'count'
ATTR_MIN_VALUE = 'min_value'
ATTR_MAX_VALUE = 'max_value'

UPDATE_MIN_TIME = timedelta(seconds=20)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ENTITIES): cv.entity_ids,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_DURATION): cv.time_period,
    vol.Optional(CONF_PRECISION, default=2): int,
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the Gismeteo weather platform."""
    _LOGGER.debug('Version %s', VERSION)
    _LOGGER.info('if you have ANY issues with this, please report them here:'
                 ' https://github.com/Limych/ha-average')

    name = config.get(CONF_NAME)
    duration = config.get(CONF_DURATION)
    entities = config.get(CONF_ENTITIES)
    precision = config.get(CONF_PRECISION)

    async_add_entities(
        [AverageSensor(hass, name, duration, entities, precision)])


class AverageSensor(Entity):
    """Implementation of an Average sensor."""

    def __init__(self, hass, name: str, measure_duration, entities: list,
                 precision: int):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._duration = measure_duration
        self._entities = entities
        self._precision = precision
        self._state = None
        self._unit_of_measurement = None
        self._icon = None
        self._temperature_mode = None
        self.count = 0
        self.min = None
        self.max = None

    @property
    def should_poll(self):
        """Return the polling state."""
        return self._duration is not None

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
        return {
            ATTR_COUNT: self.count,
            ATTR_MAX_VALUE: self.max,
            ATTR_MIN_VALUE: self.min,
        }

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def sensor_state_listener(entity, old_state, new_state):
            """Handle device state changes."""
            last_state = self._state
            self._update()
            if last_state != self._state:
                self.async_schedule_update_ha_state(True)

        @callback
        def sensor_startup(event):
            """Update template on startup."""
            if self._duration is None:
                async_track_state_change(self._hass, self._entities,
                                         sensor_state_listener)
            sensor_state_listener(None, None, None)

        self._hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START,
                                         sensor_startup)

    @staticmethod
    def _has_state(state):
        return \
            state is not None \
            and state not in [STATE_UNKNOWN, STATE_UNAVAILABLE]

    @staticmethod
    def _is_temperature(entity) -> bool:
        entity_unit = entity.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        return \
            entity_unit in (TEMP_CELSIUS, TEMP_FAHRENHEIT) \
            or isinstance(
                entity, (WeatherEntity, ClimateDevice, WaterHeaterDevice))

    def _get_temperature(self, entity) -> float:
        """Get temperature value from entity and convert it to
        Home Assistant common configured units."""
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
            if entity_unit not in (TEMP_CELSIUS, TEMP_FAHRENHEIT):
                raise ValueError(
                    UNIT_NOT_RECOGNIZED_TEMPLATE.format(entity_unit,
                                                        TEMPERATURE))

            temperature = float(temperature)
            ha_unit = self._hass.config.units.temperature_unit

            if entity_unit != ha_unit:
                temperature = convert_temperature(
                    temperature, entity_unit, ha_unit)

        return temperature

    def _get_entity_state(self, entity):
        state = self._get_temperature(entity) if self._temperature_mode \
            else entity.state
        if not self._has_state(state):
            return None

        try:
            state = float(state)
        except ValueError as exc:
            _LOGGER.error('Could not convert value "%s" to float', state)
            return None

        self.count += 1
        rstate = round(state, self._precision)
        if self.min is None:
            self.min = self.max = rstate
        else:
            self.min = min(self.min, rstate)
            self.max = max(self.max, rstate)
        return state

    @Throttle(UPDATE_MIN_TIME)
    async def async_update(self):
        if self._duration is not None:
            self._update()

    def _update(self):
        """Update the sensor state."""
        _LOGGER.debug('Updating sensor "%s"', self.name)
        start = now = start_timestamp = now_timestamp = None
        if self._duration is not None:
            now = dt_util.now()
            start = dt_util.as_utc(now - self._duration)
            now = dt_util.as_utc(now)

            # Compute integer timestamps
            start_timestamp = math.floor(dt_util.as_timestamp(start))
            now_timestamp = math.floor(dt_util.as_timestamp(now))

        values = []
        self.count = 0
        self.min = self.max = None

        for entity_id in self._entities:
            _LOGGER.debug('Processing entity "%s"', entity_id)

            entity = self._hass.states.get(entity_id)

            if entity is None:
                _LOGGER.error('Unable to find an entity "%s"', entity_id)
                continue

            if self._temperature_mode is None:
                self._temperature_mode = self._is_temperature(entity)
                if self._temperature_mode:
                    self._unit_of_measurement = \
                        self._hass.config.units.temperature_unit
                    self._icon = 'mdi:thermometer'
                else:
                    self._unit_of_measurement = \
                        entity.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
                    self._icon = \
                        entity.attributes.get(ATTR_ICON)

            value = 0
            elapsed = 0

            if self._duration is None:
                # Get current state
                value = self._get_entity_state(entity)
                _LOGGER.debug('Current state: %s', value)

            else:
                # Get history between start and now
                history_list = history.state_changes_during_period(
                    self.hass, start, now, str(entity_id))

                if entity_id not in history_list.keys():
                    value = self._get_entity_state(entity)
                    _LOGGER.warning(
                        'Historical data not found for entity "%s". '
                        'Current state used: %s', entity_id, value)
                else:
                    # Get the first state
                    item = history.get_state(self.hass, start, entity_id)
                    _LOGGER.debug('Initial historical state: %s', item)
                    last_state = None
                    last_time = start_timestamp
                    if (
                            item is not None
                            and self._has_state(item.state)
                    ):
                        last_state = self._get_entity_state(item)

                    # Get the other states
                    for item in history_list.get(entity_id):
                        _LOGGER.debug('Historical state: %s', item)
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
                        last_elapsed = now_timestamp - last_time
                        value += last_state * last_elapsed
                        elapsed += last_elapsed

                    if elapsed:
                        value /= elapsed
                    _LOGGER.debug('Historical average state: %s', value)

            values.append(value)

        if values:
            self._state = round(sum(values) / len(values), self._precision)
        else:
            self._state = None
        _LOGGER.debug('Total average state: %s', self._state)
