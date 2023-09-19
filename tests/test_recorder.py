"""The tests for recorder platform."""
from __future__ import annotations

from datetime import timedelta
import logging

from pytest_homeassistant_custom_component.common import (
    SetupRecorderInstanceT,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.components.recorder.common import (
    wait_recording_done,
)

from custom_components.average.const import ATTR_SOURCES, ATTR_TO_PROPERTY
from homeassistant.components.input_boolean import DOMAIN
from homeassistant.components.recorder.db_schema import StateAttributes, States
from homeassistant.components.recorder.util import session_scope
from homeassistant.const import ATTR_EDITABLE
from homeassistant.core import HomeAssistant, State
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


async def async_wait_recording_done_without_instance(hass: HomeAssistant) -> None:
    """Block till recording is done."""
    await hass.loop.run_in_executor(None, wait_recording_done, hass)


async def test_exclude_attributes(
    async_setup_recorder_instance: SetupRecorderInstanceT,
    hass: HomeAssistant,
):
    """Test attributes to be excluded."""
    await async_setup_recorder_instance(hass)
    assert await async_setup_component(hass, DOMAIN, {DOMAIN: {"test": {}}})

    state = hass.states.get("input_boolean.test")
    assert state
    assert state.attributes[ATTR_EDITABLE] is False

    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=5))
    await hass.async_block_till_done()
    await async_wait_recording_done_without_instance(hass)

    def _fetch_states() -> list[State]:
        with session_scope(hass=hass) as session:
            native_states = []
            for db_state, db_state_attributes in session.query(States, StateAttributes):
                state = db_state.to_native()
                state.attributes = db_state_attributes.to_native()
                native_states.append(state)
            return native_states

    states: list[State] = await hass.async_add_executor_job(_fetch_states)
    assert len(states) == 1

    attributes_to_exclude = set(ATTR_TO_PROPERTY)
    attributes_to_exclude.discard(ATTR_SOURCES)

    for attr in attributes_to_exclude:
        assert attr not in states[0].attributes
