"""Config flow for Discover Energy LYNK Cloud."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LynkCloudApi, LynkCloudAuthError, LynkCloudError
from .const import CONF_HOST, DEFAULT_HOST, DOMAIN


class LynkCloudConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a LYNK Cloud config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Collect and validate cloud credentials."""
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            host = user_input[CONF_HOST].rstrip("/")
            api = LynkCloudApi(
                async_get_clientsession(self.hass), host, username, user_input[CONF_PASSWORD]
            )
            try:
                await api.async_login()
            except LynkCloudAuthError:
                errors["base"] = "invalid_auth"
            except LynkCloudError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(username.casefold())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=username,
                    data={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_HOST: host,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Start reauthentication."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Validate replacement credentials."""
        entry = self._reauth_entry
        errors: dict[str, str] = {}
        if user_input is not None:
            api = LynkCloudApi(
                async_get_clientsession(self.hass),
                entry.data.get(CONF_HOST, DEFAULT_HOST),
                entry.data[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            try:
                await api.async_login()
            except LynkCloudAuthError:
                errors["base"] = "invalid_auth"
            except LynkCloudError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_PASSWORD: user_input[CONF_PASSWORD]}
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
            description_placeholders={"username": entry.data[CONF_USERNAME]},
        )
