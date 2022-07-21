"""The test for the average integration."""
# pylint: disable=redefined-outer-name
from __future__ import annotations

from unittest.mock import patch

from homeassistant import config as hass_config
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import SERVICE_RELOAD
from homeassistant.setup import async_setup_component

from custom_components.average.const import DOMAIN

from . import get_fixture_path
from .const import MOCK_CONFIG, TEST_NAME


async def test_reload(hass):
    """Verify we can reload."""
    assert await async_setup_component(hass, SENSOR_DOMAIN, MOCK_CONFIG)
    await hass.async_block_till_done()
    await hass.async_start()
    await hass.async_block_till_done()

    assert len(hass.states.async_all()) == 1

    assert hass.states.get(f"{SENSOR_DOMAIN}.{TEST_NAME}")

    yaml_path = get_fixture_path("configuration.yaml")

    with patch.object(hass_config, "YAML_CONFIG_FILE", yaml_path):
        await hass.services.async_call(DOMAIN, SERVICE_RELOAD, {}, blocking=True)
        await hass.async_block_till_done()

    assert hass.states.get(f"{SENSOR_DOMAIN}.{TEST_NAME}")


async def test_reload_and_remove_all(hass):
    """Verify we can reload and remove all."""
    assert await async_setup_component(hass, SENSOR_DOMAIN, MOCK_CONFIG)
    await hass.async_block_till_done()
    await hass.async_start()
    await hass.async_block_till_done()

    assert len(hass.states.async_all()) == 1

    assert hass.states.get(f"{SENSOR_DOMAIN}.{TEST_NAME}")

    yaml_path = get_fixture_path("configuration_empty.yaml")

    with patch.object(hass_config, "YAML_CONFIG_FILE", yaml_path):
        await hass.services.async_call(DOMAIN, SERVICE_RELOAD, {}, blocking=True)
        await hass.async_block_till_done()

    print(hass.states.get(f"{SENSOR_DOMAIN}.{TEST_NAME}"))
    assert hass.states.get(f"{SENSOR_DOMAIN}.{TEST_NAME}") is None
