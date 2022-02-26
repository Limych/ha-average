"""Constants for tests."""
from typing import Final

from custom_components.integration_blueprint.const import CONF_PASSWORD, CONF_USERNAME

# Mock config data to be used across multiple tests
MOCK_CONFIG: Final = {CONF_USERNAME: "test_username", CONF_PASSWORD: "test_password"}
