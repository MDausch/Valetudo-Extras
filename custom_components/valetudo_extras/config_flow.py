"""Config flow for the Valetudo Extras component."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class ValetudoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Valetudo Extras."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._host: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input:
            # TODO:
            # - Check we can access the host
            # - Tie this device to a configured mqtt robot instance?
            # - Validate we have not already set up this host
            return self.async_create_entry(title="Vaccuum", data=user_input)

        data_schema = vol.Schema({vol.Required(CONF_HOST): str})
        return self.async_show_form(step_id="user", data_schema=data_schema)
