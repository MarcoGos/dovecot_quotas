"""The Dovecot quotas integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import QuotasAPI
from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_HOSTNAME,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from .coordinator import DovecotQuotasUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Dovecot quotas from a config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    hostname = config_entry.data[CONF_HOSTNAME]
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]

    api = QuotasAPI(
        hostname=hostname,
        username=username,
        password=password,
    )

    hass.data[DOMAIN][config_entry.entry_id] = coordinator = (
        DovecotQuotasUpdateCoordinator(hass, api=api, config_entry=config_entry)
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(config_entry.entry_id)
