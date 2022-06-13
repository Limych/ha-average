"""Constants for integration_blueprint."""

from typing import Final

from homeassistant.const import Platform

# Base component constants
NAME: Final = "Integration blueprint"
DOMAIN: Final = "integration_blueprint"
VERSION: Final = "0.1.0"
ATTRIBUTION: Final = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL: Final = "https://github.com/Limych/ha-blueprint/issues"

STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# Icons
ICON: Final = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS: Final = "connectivity"

# Platforms
PLATFORMS: Final = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]

# Configuration and options
CONF_ENABLED: Final = "enabled"

# Defaults
DEFAULT_NAME: Final = DOMAIN

# Attributes
ATTR_INTEGRATION: Final = "integration"
