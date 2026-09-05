"""Shared entities for Discover Energy LYNK Cloud."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LynkCloudCoordinator


class LynkCloudEntity(CoordinatorEntity[LynkCloudCoordinator]):
    """Base entity for one LYNK controller."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: LynkCloudCoordinator, lynk_id: str) -> None:
        super().__init__(coordinator)
        self.lynk_id = lynk_id

    @property
    def lynk_data(self) -> dict[str, Any]:
        """Return this controller's latest data."""
        return self.coordinator.data.get(self.lynk_id, {})

    @property
    def device_info(self) -> DeviceInfo:
        """Describe the LYNK controller."""
        data = self.lynk_data
        return DeviceInfo(
            identifiers={(DOMAIN, self.lynk_id)},
            name=data.get("name", f"LYNK {self.lynk_id}"),
            manufacturer="Discover Energy Systems",
            model=data.get("model") or "LYNK Cloud Gateway",
            serial_number=data.get("serial_number"),
            sw_version=data.get("firmware"),
            configuration_url="https://mylynkcloud.com/lynk/",
        )


class LynkCloudBatteryEntity(LynkCloudEntity):
    """Base entity for one battery."""

    def __init__(self, coordinator: LynkCloudCoordinator, lynk_id: str, battery_sn: str) -> None:
        super().__init__(coordinator, lynk_id)
        self.battery_sn = battery_sn

    @property
    def battery_data(self) -> dict[str, Any]:
        """Return this battery's latest telemetry."""
        return next(
            (
                battery
                for battery in self.lynk_data.get("batteries", [])
                if str(battery.get("batterySn")) == self.battery_sn
            ),
            {},
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Describe the battery below its LYNK controller."""
        data = self.battery_data
        return DeviceInfo(
            identifiers={(DOMAIN, self.battery_sn)},
            name=f"Battery {self.battery_sn}",
            manufacturer="Discover Energy Systems",
            model=data.get("batteryType") or "Battery",
            serial_number=self.battery_sn,
            sw_version=data.get("firmware"),
            hw_version=data.get("hardware"),
            via_device=(DOMAIN, self.lynk_id),
        )

