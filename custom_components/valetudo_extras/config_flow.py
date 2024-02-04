"""Config flow for the Valetudo Extras component."""
from __future__ import annotations

from typing import Any

import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, LOGGER


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
        errors = {}
        if user_input:
            details, error = await self._get_device_info(user_input[CONF_HOST])

            if details is not None:
                systemId = details["systemId"]
                await self.async_set_unique_id(systemId, raise_on_progress=False)
                self._abort_if_unique_id_configured(error="already_configured_device")

                return self.async_create_entry(title=systemId, data=user_input)

            if error is not None:
                errors = {"base": error}

        data_schema = vol.Schema({vol.Required(CONF_HOST): str})
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _get_device_info(self, address: str) -> tuple[dict | None, str | None]:
        """Fetch data from the robot."""
        try:
            LOGGER.error("_get_device_info:")
            response = await self.hass.async_add_executor_job(
                requests.get, f"http://{address}/api/v2/valetudo"
            )
            response.raise_for_status()
            LOGGER.error("fetch : %s", response.json())

            return (response.json(), None)
        except requests.RequestException as ex:
            LOGGER.error("Unable to connect error: %s", ex)
            return (None, "unreachable")
