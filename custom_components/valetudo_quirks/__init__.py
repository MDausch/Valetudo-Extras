"""AutoAreas custom_component for Home Assistant"""
import logging

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity import Entity
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity_component import EntityComponent


from homeassistant.helpers.entity import Entity
import requests

_LOGGER = logging.getLogger(__name__)


DOMAIN = "quirker"
PLATFORMS = ["select"]
API_ENDPOINT = "http://192.168.1.53/api/v2/robot/capabilities/QuirksCapability"


async def async_setup(hass, config):
    """Set up the custom integration."""
    _LOGGER.error("VALETUDO_QUIRKS Loading async_setup")

    component = EntityComponent(_LOGGER, DOMAIN, hass)
    data = await hass.async_add_executor_job(fetch_data_from_endpoint)
    _LOGGER.error("VALETUDO_QUIRKS async_setup_entry %s", data)

    entities = []
    for capability in data:
        _LOGGER.error(
            "VALETUDO_QUIRKS async_setup_entry Building MyCustomSelect for: %s",
            capability,
        )
        entities.append(MyCustomSelect(capability))
    await component.async_add_entities(entities)
    return True


async def async_unload_entry(hass, config_entry):
    """Unload entities based on a config entry."""
    _LOGGER.error("VALETUDO_QUIRKS async_unload_entry")

    unload_ok = await hass.data[DOMAIN][config_entry.entry_id].async_unload()
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)
    return unload_ok


def fetch_data_from_endpoint():
    """Fetch data from the REST endpoint."""
    try:
        response = requests.get(API_ENDPOINT)
        _LOGGER.error("VALETUDO_QUIRKS Fetch data for endpoint: %s", response)

        response.raise_for_status()
        return response.json()
    except requests.RequestException as ex:
        _LOGGER.error("VALETUDO_QUIRKS Error fetching data from endpoint: %s", ex)
        return []


class MyCustomSelect(SelectEntity):
    """Representation of a select entity for My Custom Integration."""

    def __init__(self, capability):
        """Initialize the select entity."""
        self._capability = capability
        self._attr_options = self._capability["options"]
        self._attr_unique_id = self._capability["id"]

        _LOGGER.warning(
            "VALETUDO_QUIRKS capability: %s State: %s options: %s",
            self.name,
            self.state,
            self.options,
        )

    @property
    def name(self):
        """Return the name of the select entity."""
        return self._capability["title"]

    @property
    def current_option(self):
        """Return the current state of the select entity."""
        return self._capability["value"]

    async def async_select_option(self, option):
        """Set the state to the selected option."""
        try:
            response = requests.put(
                f"{API_ENDPOINT}",
                json={"id": self._capability["id"], "value": option},
            )
            response.raise_for_status()
            self._capability["value"] = option
        except requests.RequestException as ex:
            _LOGGER.error("Error setting value for %s: %s", self.name, ex)

    # async def async_update(self):
    #     """Update the state of the select entity."""
    #     data = await self.hass.async_add_executor_job(fetch_data_from_endpoint)

    #     for capability in data:
    #         if capability["id"] == self._capability["id"]:
    #             self._capability = capability
    #             break
