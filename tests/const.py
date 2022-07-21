"""Constants for tests."""
from __future__ import annotations

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_ENTITIES, CONF_NAME, CONF_UNIQUE_ID
from homeassistant.util import yaml

from tests import get_fixture_path

MOCK_CONFIG = yaml.load_yaml(str(get_fixture_path("configuration.yaml")))

_cfg = MOCK_CONFIG.get(SENSOR_DOMAIN)[0]  # type: dict

TEST_UNIQUE_ID = _cfg.get(CONF_UNIQUE_ID)
TEST_NAME = _cfg.get(CONF_NAME)
TEST_ENTITY_IDS = _cfg.get(CONF_ENTITIES)
TEST_VALUES = [3, 11.16, -17, 4.29, -29, -16.8, 8, 5, -4.7, 5, -15]
