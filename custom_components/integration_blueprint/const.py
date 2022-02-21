"""Constants for integration_blueprint."""

# Base component constants
from typing import Final

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
BINARY_SENSOR: Final = "binary_sensor"
SENSOR: Final = "sensor"
SWITCH: Final = "switch"
PLATFORMS: Final = [BINARY_SENSOR, SENSOR, SWITCH]

# Configuration and options
CONF_ENABLED: Final = "enabled"
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"

# Defaults
DEFAULT_NAME: Final = DOMAIN

# Attributes
ATTR_INTEGRATION: Final = "integration"
