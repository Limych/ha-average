"""
The Average Sensor.

For more details about this sensor, please refer to the documentation at
https://github.com/Limych/ha-average/
"""
from datetime import timedelta
from typing import Final

# Base component constants
from homeassistant.const import Platform

NAME: Final = "Average Sensor"
DOMAIN: Final = "average"
VERSION: Final = "2.3.3"
ISSUE_URL: Final = "https://github.com/Limych/ha-average/issues"

STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

PLATFORMS = [
    Platform.SENSOR,
]

# Configuration and options
CONF_START: Final = "start"
CONF_END: Final = "end"
CONF_DURATION: Final = "duration"
CONF_PRECISION: Final = "precision"
CONF_PERIOD_KEYS: Final = [CONF_START, CONF_END, CONF_DURATION]
CONF_PROCESS_UNDEF_AS: Final = "process_undef_as"

# Defaults
DEFAULT_NAME: Final = "Average"
DEFAULT_PRECISION: Final = 2

# Attributes
ATTR_START: Final = "start"
ATTR_END: Final = "end"
ATTR_SOURCES: Final = "sources"
ATTR_COUNT_SOURCES: Final = "count_sources"
ATTR_AVAILABLE_SOURCES: Final = "available_sources"
ATTR_COUNT: Final = "count"
ATTR_MIN_VALUE: Final = "min_value"
ATTR_MAX_VALUE: Final = "max_value"
#
ATTR_TO_PROPERTY: Final = [
    ATTR_START,
    ATTR_END,
    ATTR_SOURCES,
    ATTR_COUNT_SOURCES,
    ATTR_AVAILABLE_SOURCES,
    ATTR_COUNT,
    ATTR_MAX_VALUE,
    ATTR_MIN_VALUE,
]


UPDATE_MIN_TIME: Final = timedelta(seconds=20)
