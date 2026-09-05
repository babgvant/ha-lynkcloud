"""Binary sensor entities for Discover Energy LYNK Cloud."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import LynkCloudConfigEntry
from .entity import LynkCloudBatteryEntity


async def async_setup_entry(hass: HomeAssistant, entry: LynkCloudConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Set up battery problem sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        LynkBatteryProblemSensor(coordinator, lynk_id, str(battery["batterySn"]))
        for lynk_id, data in coordinator.data.items()
        for battery in data.get("batteries", [])
        if battery.get("batterySn") is not None
    )


class LynkBatteryProblemSensor(LynkCloudBatteryEntity, BinarySensorEntity):
    """Indicate whether the battery reports faults or warnings."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "fault_or_warning"

    def __init__(self, coordinator, lynk_id: str, battery_sn: str) -> None:
        super().__init__(coordinator, lynk_id, battery_sn)
        self._attr_unique_id = f"{battery_sn}_fault_or_warning"

    @property
    def is_on(self) -> bool:
        return bool(self.battery_data.get("faultOrWarnings"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"faults_or_warnings": self.battery_data.get("faultOrWarnings", [])}

