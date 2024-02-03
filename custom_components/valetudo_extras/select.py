"""Demo platform that offers a fake select entity."""
from __future__ import annotations

import requests

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the valetudo quirk select platform."""
    entities = []
    resource = config_entry.data[CONF_HOST]
    data = await hass.async_add_executor_job(fetch_data_from_endpoint, resource)
    for capability in data:
        LOGGER.debug(
            "%s: %s Building ValetudoQuirkSelect for: %s",
            DOMAIN,
            resource,
            capability,
        )
        entities.append(ValetudoQuirkSelect(hass, capability, resource))
    async_add_entities(entities)


class ValetudoQuirkSelect(SelectEntity):
    """Representation of a select entity for Valetudo Extras Integration."""

    def __init__(self, hass: HomeAssistant, capability: dict, resource: str) -> None:
        """Initialize the quirk."""
        self._hass: HomeAssistant = hass
        self._capability = capability
        self._attr_options = self._capability["options"]
        self._attr_unique_id = self._capability["id"]
        self._attr_current_option = self._capability["value"]
        self._resource = resource

    @property
    def name(self):
        """Return the name of the select entity."""
        return self._capability["title"]

    @property
    def current_option(self):
        """Return the current state of the select entity."""
        return self._capability["value"]

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""

        def do_select_option(option: str):
            """Fetch data from the REST endpoint."""
            try:
                response = requests.put(
                    f"http://{self._resource}/api/v2/robot/capabilities/QuirksCapability",
                    json={"id": self._capability["id"], "value": option},
                )
                response.raise_for_status()
                return response.text == "OK"
            except requests.exceptions.RequestException as ex:
                LOGGER.error("%s execute_select_option failed: %s", DOMAIN, ex)
            return False

        response = await self._hass.async_add_executor_job(do_select_option, option)

        if response:
            self._capability["value"] = option
            self.async_write_ha_state()

    async def async_update(self):
        """Update the state of the select entity."""
        data = await self.hass.async_add_executor_job(
            fetch_data_from_endpoint, self._resource
        )

        for capability in data:
            if capability["id"] == self._capability["id"]:
                self._capability = capability
                break


# TODO: Move to data coordinator
def fetch_data_from_endpoint(resource: str):
    """Fetch data from the Valetudo Quirk endpoint."""
    try:
        response = requests.get(
            f"http://{resource}/api/v2/robot/capabilities/QuirksCapability",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as ex:
        LOGGER.error("%s Error fetching data from endpoint: %s", DOMAIN, ex)
        return []
