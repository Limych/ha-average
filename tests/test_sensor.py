"""The test for the average sensor platform."""
# pylint: disable=redefined-outer-name
import json
import logging
from asyncio import sleep
from datetime import timedelta
from unittest.mock import MagicMock, patch

import homeassistant.util.dt as dt_util
import pytest
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ENTITIES,
    CONF_NAME,
    CONF_PLATFORM,
    DEVICE_CLASS_TEMPERATURE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    TEMP_FAHRENHEIT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import Template
from homeassistant.setup import async_setup_component
from homeassistant.util.unit_system import TEMPERATURE_UNITS
from pytest import raises
from pytest_homeassistant_custom_component.common import assert_setup_component
from voluptuous import Invalid

from custom_components.average.const import CONF_DURATION, CONF_END, CONF_START, DOMAIN
from custom_components.average.sensor import (
    AverageSensor,
    async_setup_platform,
    check_period_keys,
)

# pylint: disable=ungrouped-imports
try:
    from homeassistant.components.recorder.models import LazyState
except ImportError:
    from homeassistant.components.history import LazyState


TEST_UNIQUE_ID = "test_id"
TEST_NAME = "test_name"
TEST_ENTITY_IDS = ["sensor.test_monitored"]
TEST_VALUES = [3, 11.16, -17, 4.29, -29, -16.8, 8, 5, -4.7, 5, -15]


@pytest.fixture(autouse=True)
def mock_legacy_time(legacy_patchable_time):
    """Make time patchable for all the tests."""
    yield


@pytest.fixture()
def default_sensor(hass: HomeAssistant):
    """Create an AverageSensor with default values."""
    entity = AverageSensor(
        hass,
        TEST_UNIQUE_ID,
        TEST_NAME,
        None,
        Template("{{ now() }}"),
        timedelta(minutes=3),
        TEST_ENTITY_IDS,
        2,
        None,
    )
    entity.hass = hass
    return entity


class Objectview:
    """Mock dict to object."""

    def __init__(self, dct):
        """Mock dict to object."""
        self.__dict__ = dct


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


async def test_entity_initialization(hass: HomeAssistant, default_sensor):
    """Test sensor initialization."""
    expected_attributes = {
        "available_sources": 0,
        "count": 0,
        "count_sources": 1,
        "sources": ["sensor.test_monitored"],
    }

    assert default_sensor.unique_id == TEST_UNIQUE_ID
    assert default_sensor.name == TEST_NAME
    assert default_sensor.should_poll is True
    assert default_sensor.available is False
    assert default_sensor.native_value is None
    assert default_sensor.native_unit_of_measurement is None
    assert default_sensor.icon is None
    assert default_sensor.extra_state_attributes == expected_attributes

    entity = AverageSensor(
        hass,
        None,
        TEST_NAME,
        None,
        Template("{{ now() }}"),
        timedelta(minutes=3),
        TEST_ENTITY_IDS,
        2,
        None,
    )

    assert entity.unique_id is None

    entity = AverageSensor(
        hass,
        "__legacy__",
        TEST_NAME,
        None,
        Template("{{ now() }}"),
        timedelta(minutes=3),
        TEST_ENTITY_IDS,
        2,
        None,
    )

    assert entity.unique_id == "2ef66732fb7155dce84ad53afe910beba59cfad4"


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

    with assert_setup_component(2, SENSOR):
        assert await async_setup_component(
            hass,
            SENSOR,
            {
                SENSOR: [
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
                "shared_attrs": json.dumps({"temperature": 25}),
            }
        )
    )
    assert default_sensor._get_temperature(state) == 25

    state = LazyState(
        Objectview(
            {
                "entity_id": "climate.test",
                "state": "test",
                "shared_attrs": json.dumps({"current_temperature": 16}),
            }
        )
    )
    assert default_sensor._get_temperature(state) == 16

    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": 125,
                "shared_attrs": json.dumps({ATTR_UNIT_OF_MEASUREMENT: TEMP_FAHRENHEIT}),
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
                "shared_attrs": json.dumps({ATTR_UNIT_OF_MEASUREMENT: TEMP_FAHRENHEIT}),
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
                "shared_attrs": json.dumps({ATTR_UNIT_OF_MEASUREMENT: TEMP_FAHRENHEIT}),
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
                "shared_attrs": json.dumps({ATTR_UNIT_OF_MEASUREMENT: None}),
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
                "shared_attrs": json.dumps({ATTR_UNIT_OF_MEASUREMENT: None}),
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
                "shared_attrs": json.dumps({ATTR_UNIT_OF_MEASUREMENT: None}),
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
                "shared_attrs": json.dumps({ATTR_UNIT_OF_MEASUREMENT: None}),
                "last_changed": dt_util.now(),
            }
        )
    )
    assert default_sensor._get_state_value(state) == 34

    assert default_sensor.min_value == 21
    assert default_sensor.max_value == 34


async def test__init_mode(hass: HomeAssistant, default_sensor, caplog):
    """Test sensor mode initialization."""
    caplog.set_level(logging.DEBUG)

    assert default_sensor._temperature_mode is None
    assert default_sensor._attr_device_class is None
    assert default_sensor._attr_native_unit_of_measurement is None
    assert default_sensor._attr_icon is None

    # Detect by device class
    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": None,
                "shared_attrs": json.dumps(
                    {
                        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
                    }
                ),
            }
        )
    )

    caplog.clear()
    default_sensor._temperature_mode = None
    default_sensor._attr_device_class = None
    default_sensor._attr_native_unit_of_measurement = None

    default_sensor._init_mode(state)

    assert default_sensor._temperature_mode is True
    assert default_sensor._attr_device_class is DEVICE_CLASS_TEMPERATURE
    assert (
        default_sensor._attr_native_unit_of_measurement
        is hass.config.units.temperature_unit
    )
    assert len(caplog.records) == 1

    # Detect by measuring unit
    for unit in TEMPERATURE_UNITS:
        state = LazyState(
            Objectview(
                {
                    "entity_id": "sensor.test",
                    "state": None,
                    "shared_attrs": json.dumps(
                        {
                            ATTR_UNIT_OF_MEASUREMENT: unit,
                        }
                    ),
                }
            )
        )

        caplog.clear()
        default_sensor._temperature_mode = None
        default_sensor._attr_device_class = None
        default_sensor._attr_native_unit_of_measurement = None

        default_sensor._init_mode(state)

        assert default_sensor._temperature_mode is True
        assert default_sensor._attr_device_class is DEVICE_CLASS_TEMPERATURE
        assert (
            default_sensor._attr_native_unit_of_measurement
            == hass.config.units.temperature_unit
        )
        assert len(caplog.records) == 1

    # Detect by domain
    for domain in (WEATHER_DOMAIN, CLIMATE_DOMAIN, WATER_HEATER_DOMAIN):
        state = LazyState(
            Objectview(
                {
                    "entity_id": f"{domain}.test",
                    "state": None,
                    "shared_attrs": json.dumps({}),
                }
            )
        )

        caplog.clear()
        default_sensor._temperature_mode = None
        default_sensor._attr_device_class = None
        default_sensor._attr_native_unit_of_measurement = None

        default_sensor._init_mode(state)

        assert default_sensor._temperature_mode is True
        assert default_sensor._attr_device_class is DEVICE_CLASS_TEMPERATURE
        assert (
            default_sensor._attr_native_unit_of_measurement
            == hass.config.units.temperature_unit
        )
        assert len(caplog.records) == 1

    # Can't detect
    state = LazyState(
        Objectview(
            {
                "entity_id": "sensor.test",
                "state": None,
                "shared_attrs": json.dumps(
                    {
                        ATTR_ICON: "some_icon",
                    }
                ),
            }
        )
    )

    caplog.clear()
    default_sensor._temperature_mode = None
    default_sensor._attr_device_class = None
    default_sensor._attr_native_unit_of_measurement = None

    default_sensor._init_mode(state)

    assert default_sensor._temperature_mode is False
    assert default_sensor._attr_device_class is None
    assert default_sensor._attr_native_unit_of_measurement is None
    assert default_sensor._attr_icon == "some_icon"
    assert len(caplog.records) == 1

    # Skip if mode already detected
    caplog.clear()

    default_sensor._init_mode(state)

    assert len(caplog.records) == 0


async def test_update(default_sensor):
    """Test update throttler."""
    with patch.object(default_sensor, "_async_update_state") as ups:
        await default_sensor.async_update()
        await sleep(1)
        await default_sensor.async_update()

        assert ups.call_count == 1


# pylint: disable=protected-access
async def test__update_period(default_sensor):
    """Test period updater."""
    # default_sensor._update_period()
    # todo; pylint: disable=fixme
