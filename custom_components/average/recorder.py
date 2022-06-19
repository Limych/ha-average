"""Integration platform for recorder."""
from __future__ import annotations

from homeassistant.core import HomeAssistant, callback

from .const import ATTR_SOURCES, ATTR_TO_PROPERTY


@callback
def exclude_attributes(hass: HomeAssistant) -> set[str]:
    """Exclude unimportant attributes from being recorded in the database."""
    attributes_to_exclude = set(ATTR_TO_PROPERTY)
    attributes_to_exclude.discard(ATTR_SOURCES)
    return attributes_to_exclude
