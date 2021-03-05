"""The test for the average sensor platform."""
# pylint: disable=redefined-outer-name
import json
from asyncio import sleep
from datetime import timedelta
from unittest.mock import MagicMock, patch

import homeassistant.util.dt as dt_util
import pytest
from homeassistant.components.history import LazyState
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ENTITIES,
    CONF_NAME,
    CONF_PLATFORM,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    TEMP_FAHRENHEIT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import Template
from homeassistant.setup import async_setup_component
from pytest import raises
from pytest_homeassistant_custom_component.common import assert_setup_component
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


@pytest.fixture()
def default_sensor(hass: HomeAssistant):
    """Create an AverageSensor with default values."""
    name = "test"
    entity_ids = ["sensor.test_monitored"]

    return AverageSensor(
        hass,
        name,
        None,
        Template("{{ now() }}"),
        timedelta(minutes=3),
        entity_ids,
        2,
        None,
    )


class Objectview:
    """Mock dict to object."""

    def __init__(self, d):
        """Mock dict to object."""
        self.__dict__ = d


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


async def test_entity_initialization(default_sensor):
    """Test sensor initialization."""
    expected_attributes = {
        "available_sources": 0,
        "count": 0,
        "count_sources": 1,
        "sources": ["sensor.test_monitored"],
    }

    assert default_sensor.name == "test"
    assert default_sensor.unique_id == "2ef66732fb7155dce84ad53afe910beba59cfad4"
    assert default_sensor.should_poll is True
    assert default_sensor.available is False
    assert default_sensor.state == STATE_UNAVAILABLE
    assert default_sensor.unit_of_measurement is None
    assert default_sensor.icon is None
    assert default_sensor.state_attributes == expected_attributes


async def test_async_setup_platform(hass: HomeAssistant):
    """Test platform setup."""
    mock_sensor = {
        "platform": "template",
        "sensors": {"test_monitored": {"value_template": "{{ 2 }}"}},
    }
    config = {
        CONF_PLATFORM: DOMAIN,
        CONF_ENTITIES: ["sensor.test_monitored", "sensor.nonexistent"],
    }

    with assert_setup_component(2, "sensor"):
        assert await async_setup_component(
            hass,
            "sensor",
            {
                "sensor": [
                    config,
                    mock_sensor,
                ]
            },
        )
    await hass.async_block_till_done()

    await hass.async_start()
    await hass.async_block_till_done()

    state = hass.states.get("sensor.average")
    assert state is not None
    assert state.state == "2.0"


# pylint: disable=protected-access
async def test__has_state():
    """Test states checker."""
    # Valid states
    states = [True, 12, "qwe", 45.22, False]
    for state in states:
        assert AverageSensor._has_state(state)

    # Invalid states
    states = [None, STATE_UNKNOWN, STATE_UNAVAILABLE, "None", ""]
    for state in states:
        assert AverageSensor._has_state(state) is False


# pylint: disable=protected-access
async def test__get_temperature(default_sensor):
    """Test temperature getter."""
    state = LazyState(
        Objectview(
            {
                "entity_id": "weather.test",
                "state": "test",
                "attributes": json.dumps({"temperature": 25}),
            }
        )
    )
    assert default_sensor._get_temperature(state) == 25

    state = LazyState(
        Objectview(
            {
                "entity_id": "climate.test",
                "state": "test",
                "attributes": json.dumps({"current_temperature": 16}),
            }
        )
    )
    assert default_sensor._get_temperature(state) == 16

    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": 125,
                "attributes": json.dumps({ATTR_UNIT_OF_MEASUREMENT: TEMP_FAHRENHEIT}),
                "last_changed": dt_util.now(),
            }
        )
    )
    assert round(default_sensor._get_temperature(state), 3) == 51.667

    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": "",
                "attributes": json.dumps({ATTR_UNIT_OF_MEASUREMENT: TEMP_FAHRENHEIT}),
                "last_changed": dt_util.now(),
            }
        )
    )
    assert default_sensor._get_temperature(state) is None

    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": "qwe",
                "attributes": json.dumps({ATTR_UNIT_OF_MEASUREMENT: TEMP_FAHRENHEIT}),
                "last_changed": dt_util.now(),
            }
        )
    )
    assert default_sensor._get_temperature(state) is None


# pylint: disable=protected-access
async def test__get_state_value(default_sensor):
    """Test state getter."""
    default_sensor._undef = "Undef"

    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": "None",
                "attributes": json.dumps({ATTR_UNIT_OF_MEASUREMENT: None}),
                "last_changed": dt_util.now(),
            }
        )
    )
    assert default_sensor._get_state_value(state) == "Undef"

    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": "asd",
                "attributes": json.dumps({ATTR_UNIT_OF_MEASUREMENT: None}),
                "last_changed": dt_util.now(),
            }
        )
    )
    assert default_sensor._get_state_value(state) is None

    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": 21,
                "attributes": json.dumps({ATTR_UNIT_OF_MEASUREMENT: None}),
                "last_changed": dt_util.now(),
            }
        )
    )
    assert default_sensor._get_state_value(state) == 21

    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": 34,
                "attributes": json.dumps({ATTR_UNIT_OF_MEASUREMENT: None}),
                "last_changed": dt_util.now(),
            }
        )
    )
    assert default_sensor._get_state_value(state) == 34

    assert default_sensor.min_value == 21
    assert default_sensor.max_value == 34


async def test_update(default_sensor):
    """Test update throttler."""
    with patch.object(default_sensor, "_update_state") as ups:
        default_sensor.update()
        await sleep(1)
        default_sensor.update()

        assert ups.call_count == 1


# pylint: disable=protected-access
async def test__update_period(default_sensor):
    """Test period updater."""
    # default_sensor._update_period()
