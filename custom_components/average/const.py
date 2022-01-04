"""
The Average Sensor.

For more details about this sensor, please refer to the documentation at
https://github.com/Limych/ha-average/
"""
from datetime import timedelta

# Base component constants
NAME = "Average Sensor"
DOMAIN = "average"
VERSION = "2.2.1"
ISSUE_URL = "https://github.com/Limych/ha-average/issues"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# Configuration and options
CONF_START = "start"
CONF_END = "end"
CONF_DURATION = "duration"
CONF_PRECISION = "precision"
CONF_PERIOD_KEYS = [CONF_START, CONF_END, CONF_DURATION]
CONF_PROCESS_UNDEF_AS = "process_undef_as"

# Defaults
DEFAULT_NAME = "Average"
DEFAULT_PRECISION = 2

# Attributes
ATTR_START = "start"
ATTR_END = "end"
ATTR_SOURCES = "sources"
ATTR_COUNT_SOURCES = "count_sources"
ATTR_AVAILABLE_SOURCES = "available_sources"
ATTR_COUNT = "count"
ATTR_MIN_VALUE = "min_value"
ATTR_MAX_VALUE = "max_value"
#
ATTR_TO_PROPERTY = [
    ATTR_START,
    ATTR_END,
    ATTR_SOURCES,
    ATTR_COUNT_SOURCES,
    ATTR_AVAILABLE_SOURCES,
    ATTR_COUNT,
    ATTR_MAX_VALUE,
    ATTR_MIN_VALUE,
]


UPDATE_MIN_TIME = timedelta(seconds=20)
