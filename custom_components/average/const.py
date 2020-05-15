"""
The Average Sensor.

For more details about this sensor, please refer to the documentation at
https://github.com/Limych/ha-average/
"""
from datetime import timedelta

# Base component constants
VERSION = "1.4.3"
ISSUE_URL = "https://github.com/Limych/ha-average/issues"

CONF_START = "start"
CONF_END = "end"
CONF_DURATION = "duration"
CONF_PRECISION = "precision"
CONF_PERIOD_KEYS = [CONF_START, CONF_END, CONF_DURATION]

DEFAULT_NAME = "Average"

ATTR_START = "start"
ATTR_END = "end"
ATTR_COUNT_SOURCES = "count_sources"
ATTR_AVAILABLE_SOURCES = "available_sources"
ATTR_COUNT = "count"
ATTR_MIN_VALUE = "min_value"
ATTR_MAX_VALUE = "max_value"

ATTR_TO_PROPERTY = [
    ATTR_START,
    ATTR_END,
    ATTR_COUNT_SOURCES,
    ATTR_AVAILABLE_SOURCES,
    ATTR_COUNT,
    ATTR_MAX_VALUE,
    ATTR_MIN_VALUE,
]

UPDATE_MIN_TIME = timedelta(seconds=20)
