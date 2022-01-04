"""BlueprintEntity class."""
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_ID
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_INTEGRATION, ATTRIBUTION, DOMAIN, NAME, VERSION


class IntegrationBlueprintEntity(CoordinatorEntity):
    """Blueprint entity."""

    def __init__(self, coordinator, config_entry):
        """Class initialization."""
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": NAME,
            "model": VERSION,
            "manufacturer": NAME,
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_ID: str(self.coordinator.data.get("id")),
            ATTR_INTEGRATION: DOMAIN,
        }
