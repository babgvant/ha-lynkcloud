"""Data coordinator for Discover Energy LYNK Cloud."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import LynkCloudApi, LynkCloudAuthError, LynkCloudError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .discovery import lynk_node_id, lynk_nodes

_LOGGER = logging.getLogger(__name__)


class LynkCloudCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch all account telemetry in one coordinated update."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: LynkCloudApi) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=entry,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            nodes = lynk_nodes(await self.api.async_get_tree())
            if not nodes:
                raise UpdateFailed("No LYNK controllers were found for this account")
            results = await asyncio.gather(
                *(self._async_device_data(node) for node in nodes)
            )
            return {item["id"]: item for item in results}
        except LynkCloudAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except LynkCloudError as err:
            raise UpdateFailed(str(err)) from err

    async def _async_device_data(self, node: dict[str, Any]) -> dict[str, Any]:
        ul_id = lynk_node_id(node)
        if ul_id is None:
            raise UpdateFailed("LYNK controller is missing its telemetry identifier")
        day_start = dt_util.start_of_local_day()
        begin_time = int(day_start.timestamp() * 1000)
        end_time = int((day_start + timedelta(days=1)).timestamp() * 1000) - 1
        overview, batteries = await asyncio.gather(
            self.api.async_get_overview(ul_id, begin_time, end_time),
            self.api.async_get_batteries(ul_id),
        )
        return {
            "id": ul_id,
            "name": node.get("name") or node.get("label") or f"LYNK {ul_id}",
            "serial_number": node.get("serialNumber"),
            "model": node.get("type"),
            "firmware": node.get("firmwareVersion"),
            "overview": overview,
            "batteries": batteries,
        }
