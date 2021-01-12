"""
The Average Sensor.

For more details about this sensor, please refer to the documentation at
https://github.com/Limych/ha-average/
"""
from datetime import timedelta

# Base component constants
from homeassistant.components.min_max.sensor import (
    ATTR_MEDIAN,
    ATTR_MIN_VALUE,
    ATTR_MAX_VALUE,
    ATTR_COUNT_SENSORS,
    ATTR_MEAN,
    ATTR_MAX_ENTITY_ID,
    ATTR_MIN_ENTITY_ID,
    ATTR_LAST,
    ATTR_LAST_ENTITY_ID,
)

VERSION = "dev"
ISSUE_URL = "https://github.com/Limych/ha-average/issues"

CONF_START = "start"
CONF_END = "end"
CONF_DURATION = "duration"
CONF_PRECISION = "precision"
CONF_PERIOD_KEYS = [CONF_START, CONF_END, CONF_DURATION]
CONF_PROCESS_UNDEF_AS = "process_undef_as"

ATTR_START = "start"
ATTR_END = "end"
ATTR_SENSORS = "sensors"
ATTR_AVAILABLE_SENSORS = "available_sensors"
ATTR_COUNT = "count"
ATTR_MODE = "mode"

ATTR_TO_PROPERTY = [
    ATTR_START,
    ATTR_END,
    ATTR_SENSORS,
    ATTR_COUNT_SENSORS,
    ATTR_AVAILABLE_SENSORS,
    ATTR_COUNT,
    ATTR_MAX_VALUE,
    ATTR_MAX_ENTITY_ID,
    ATTR_MIN_VALUE,
    ATTR_MIN_ENTITY_ID,
    ATTR_MEAN,
    ATTR_MEDIAN,
    ATTR_MODE,
    ATTR_LAST,
    ATTR_LAST_ENTITY_ID,
]

UPDATE_MIN_TIME = timedelta(seconds=20)

SENSOR_TYPES = {
    ATTR_MEAN: "mean",
    ATTR_MIN_VALUE: "min",
    ATTR_MAX_VALUE: "max",
    ATTR_MEDIAN: "median",
    ATTR_MODE: "mode",
    ATTR_LAST: "last",
}
