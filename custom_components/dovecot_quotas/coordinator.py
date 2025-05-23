"""Coordinator for Dovecot Quotas integration."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging
from homeassistant.helpers.update_coordinator import UpdateFailed, DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from .api import QuotasAPI
from .const import DEFAULT_SYNC_INTERVAL, DOMAIN, CONF_ACCOUNTS, CONF_VERSION

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DovecotQuotasUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api: QuotasAPI) -> None:
        """Initialize."""
        self.api = api
        self.platforms: list[str] = []
        self.last_updated = None
        self._hass = hass

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SYNC_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            data = {}
            data[CONF_ACCOUNTS] = await self.api.get_quotas()
            data[CONF_VERSION] = await self.api.get_version()
            self.last_updated = datetime.now().replace(
                tzinfo=ZoneInfo(self._hass.config.time_zone)
            )
            return data
        except Exception as exception:
            _LOGGER.error("Error _async_update_data: %s", exception)
            raise UpdateFailed() from exception
