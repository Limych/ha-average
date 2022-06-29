"""Adds config flow for Blueprint."""
from typing import Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import IntegrationBlueprintApiClient
from .const import DOMAIN, PLATFORMS  # pylint: disable=unused-import


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input: Optional[ConfigType] = None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")     # noqa: E800

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )

            self._errors["base"] = "auth"

        user_input = {}
        # Provide defaults for form
        user_input[CONF_USERNAME] = ""
        user_input[CONF_PASSWORD] = ""

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Get component options flow."""
        return BlueprintOptionsFlowHandler(config_entry)

    # pylint: disable=unused-argument
    async def _show_config_form(self, user_input: Optional[ConfigType]):
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=user_input[CONF_USERNAME]): str,
                    vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username: str, password: str) -> bool:
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = IntegrationBlueprintApiClient(username, password, session)
            await client.async_get_data()
            return True

        except Exception:  # pylint: disable=broad-except
            return False


class BlueprintOptionsFlowHandler(config_entries.OptionsFlow):
    """Blueprint config flow options handler."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize Blueprint options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    # pylint: disable=unused-argument
    async def async_step_init(self, user_input: Optional[ConfigType] = None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input: Optional[ConfigType] = None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(str(x), default=self.options.get(str(x), True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_USERNAME), data=self.options
        )
