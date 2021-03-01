"""The test for the average sensor platform."""
from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from homeassistant.const import (
    CONF_ENTITIES,
    CONF_NAME,
    CONF_PLATFORM,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import Template
from pytest import raises
from voluptuous import Invalid

from custom_components.average.const import CONF_DURATION, CONF_END, CONF_START, DOMAIN
from custom_components.average.sensor import (
    AverageSensor,
    async_setup_platform,
    check_period_keys,
)

TEST_VALUES = [3, 11.16, -17, 4.29, -29, -16.8, 8, 5, -4.7, 5, -15]


@pytest.fixture(autouse=True)
def mock_legacy_time(legacy_patchable_time):
    """Make time patchable for all the tests."""
    yield


async def test_valid_check_period_keys(hass: HomeAssistant):
    """Test period keys check."""
    assert check_period_keys(
        {
            CONF_DURATION: 10,
        }
    )
    assert check_period_keys(
        {
            CONF_START: 11,
            CONF_DURATION: 12,
        }
    )
    assert check_period_keys(
        {
            CONF_DURATION: 13,
            CONF_END: 14,
        }
    )
    assert check_period_keys(
        {
            CONF_START: 15,
            CONF_END: 16,
        }
    )


async def test_invalid_check_period_keys(hass: HomeAssistant):
    """Test period keys check."""
    with raises(Invalid):
        check_period_keys(
            {
                CONF_END: 20,
            }
        )
    with raises(Invalid):
        check_period_keys(
            {
                CONF_START: 21,
            }
        )
    with raises(Invalid):
        check_period_keys(
            {
                CONF_START: 22,
                CONF_END: 23,
                CONF_DURATION: 24,
            }
        )


async def test_setup_platform(hass: HomeAssistant):
    """Test platform setup."""
    async_add_entities = MagicMock()

    config = {
        CONF_PLATFORM: DOMAIN,
        CONF_NAME: "test",
        CONF_ENTITIES: ["sensor.test_monitored"],
        CONF_START: Template("{{ 0 }}"),
        CONF_DURATION: timedelta(seconds=10),
    }

    await async_setup_platform(hass, config, async_add_entities, None)
    assert async_add_entities.called


async def test_sensor_initialization(hass: HomeAssistant):
    """Test sensor initialization."""
    name = "test"
    entity_ids = ["sensor.test_monitored"]

    expected_attributes = {
        "available_sources": 0,
        "count": 0,
        "count_sources": 1,
        "sources": ["sensor.test_monitored"],
    }

    sensor = AverageSensor(hass, name, None, None, None, entity_ids, 2, None)

    assert sensor.name == name
    assert sensor.should_poll is False
    assert sensor.available is False
    assert sensor.state == STATE_UNAVAILABLE
    assert sensor.unit_of_measurement is None
    assert sensor.icon is None
    assert sensor.device_state_attributes == expected_attributes
