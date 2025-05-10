"""Config flow for Dovecot quotas integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation
# from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_HOSTNAME, CONF_USERNAME, CONF_PASSWORD, CONF_ACCOUNTS
from .api import QuotasAPI

_LOGGER = logging.getLogger(__name__)


class PlaceholderHub:
    def __init__(self) -> None:
        """Initialize."""

    async def authenticate(
        self, hostname, username, password: str
    ) -> bool:
        """Test if we can find data for the given position."""
        _LOGGER.info("authenticate called with %s %s and <password>", hostname, username)
        api = QuotasAPI(
            hostname=hostname,
            username=username,
            password=password,
        )
        try:
            await api.get_quotas()
        except Exception as err:
            _LOGGER.error("Error in authenticate: %s", err)
            return False
        return True


async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hub = PlaceholderHub()
    if not await hub.authenticate(
        data[CONF_HOSTNAME], data[CONF_USERNAME], data[CONF_PASSWORD]
    ):
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {}


class DovecotQuotasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dovecot Quotas."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self._config: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        STEP_SERVER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_HOSTNAME): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_SERVER_DATA_SCHEMA
            )

        errors = {}

        await self.async_set_unique_id(user_input[CONF_HOSTNAME])
        self._abort_if_unique_id_configured()

        try:
            await validate_input(user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            self._config[CONF_HOSTNAME] = user_input[CONF_HOSTNAME]
            self._config[CONF_USERNAME] = user_input[CONF_USERNAME]
            self._config[CONF_PASSWORD] = user_input[CONF_PASSWORD]
            return await self.async_step_accounts()

        return self.async_show_form(
            step_id="user", data_schema=STEP_SERVER_DATA_SCHEMA, errors=errors
        )

    async def async_step_accounts(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:

        if user_input is None:
            _LOGGER.debug("async_step_accounts: user_input is None, now creating api")
            api = QuotasAPI(
                hostname=self._config[CONF_HOSTNAME],
                username=self._config[CONF_USERNAME],
                password=self._config[CONF_PASSWORD],
            )
            accounts = []
            _LOGGER.debug("async_step_accounts: created api, now getting quotas")
            quotas = await api.get_quotas()
            real_quotas = {
                account: info for account, info in quotas.items()
                if info['quota'] != '-'
            }
            _LOGGER.debug("async_step_accounts: got quotas, now creating accounts list")
            for account in sorted(real_quotas.keys()):
                accounts.append(account)

            STEP_ACCOUNTS_DATA_SCHEMA = vol.Schema(
                {
                    vol.Required(CONF_ACCOUNTS): config_validation.multi_select(accounts)
                }
            )

            return self.async_show_form(
                step_id="accounts", data_schema=STEP_ACCOUNTS_DATA_SCHEMA
            )
        else:
            # Create all the devices and entities
            if CONF_ACCOUNTS in user_input:
                selected_accounts = user_input[CONF_ACCOUNTS]
                _LOGGER.debug("async_step_accounts: selected accounts: %s", selected_accounts)
                self._config[CONF_ACCOUNTS] = selected_accounts
                return self.async_create_entry(title=f"{self._config[CONF_HOSTNAME]}", data=self._config)




class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
