"""Discover Energy LYNK Cloud integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LynkCloudApi
from .const import CONF_HOST, DEFAULT_HOST, PLATFORMS
from .coordinator import LynkCloudCoordinator

type LynkCloudConfigEntry = ConfigEntry[LynkCloudCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: LynkCloudConfigEntry) -> bool:
    """Set up LYNK Cloud from a config entry."""
    api = LynkCloudApi(
        async_get_clientsession(hass),
        entry.data.get(CONF_HOST, DEFAULT_HOST),
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )
    coordinator = LynkCloudCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: LynkCloudConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

