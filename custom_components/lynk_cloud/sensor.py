"""Sensor entities for Discover Energy LYNK Cloud."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfEnergy, UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import LynkCloudConfigEntry
from .entity import LynkCloudBatteryEntity, LynkCloudEntity


@dataclass(frozen=True, kw_only=True)
class LynkSensorDescription(SensorEntityDescription):
    """Description of a cloud telemetry field."""

    value_fn: Callable[[dict[str, Any]], Any]


OVERVIEW_SENSORS = (
    LynkSensorDescription(key="state_of_charge", translation_key="state_of_charge", native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("netSoc")),
    LynkSensorDescription(key="power", translation_key="power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("power")),
    LynkSensorDescription(key="battery_count", translation_key="battery_count", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("batteryNumber")),
    LynkSensorDescription(key="alarm_count", translation_key="alarm_count", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("alarmCount")),
    LynkSensorDescription(key="lifetime_charge", translation_key="lifetime_charge", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("lifetimeCharge")),
    LynkSensorDescription(key="lifetime_discharge", translation_key="lifetime_discharge", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("lifetimeDischarge")),
)

BATTERY_SENSORS = (
    LynkSensorDescription(key="state_of_charge", translation_key="state_of_charge", native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("soc")),
    LynkSensorDescription(key="terminal_voltage", translation_key="terminal_voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("terminalV")),
    LynkSensorDescription(key="current", translation_key="current", native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("currentA")),
    LynkSensorDescription(key="battery_temperature", translation_key="battery_temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("battTemp")),
    LynkSensorDescription(key="bms_temperature", translation_key="bms_temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("bmsTemp")),
    LynkSensorDescription(key="cell_average_voltage", translation_key="cell_average_voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=3, value_fn=lambda d: d.get("cellAvgV")),
    LynkSensorDescription(key="cell_minimum_voltage", translation_key="cell_minimum_voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=3, value_fn=lambda d: d.get("cellMinV")),
    LynkSensorDescription(key="cell_maximum_voltage", translation_key="cell_maximum_voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=3, value_fn=lambda d: d.get("cellMaxV")),
    LynkSensorDescription(key="cell_spread", translation_key="cell_spread", native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("cellSpread")),
    LynkSensorDescription(key="installed_capacity", translation_key="installed_capacity", native_unit_of_measurement="Ah", state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("installedCapacity")),
    LynkSensorDescription(key="lifetime_charge", translation_key="lifetime_charge", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("lifetimeChargeK")),
    LynkSensorDescription(key="lifetime_discharge", translation_key="lifetime_discharge", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda d: d.get("lifetimeDischargeK")),
)


async def async_setup_entry(hass: HomeAssistant, entry: LynkCloudConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Set up all currently discovered sensors."""
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = []
    for lynk_id, data in coordinator.data.items():
        entities.extend(LynkOverviewSensor(coordinator, lynk_id, description) for description in OVERVIEW_SENSORS)
        for battery in data.get("batteries", []):
            if (battery_sn := battery.get("batterySn")) is not None:
                entities.extend(LynkBatterySensor(coordinator, lynk_id, str(battery_sn), description) for description in BATTERY_SENSORS)
    async_add_entities(entities)


class LynkOverviewSensor(LynkCloudEntity, SensorEntity):
    """A controller-level sensor."""

    entity_description: LynkSensorDescription

    def __init__(self, coordinator, lynk_id: str, description: LynkSensorDescription) -> None:
        super().__init__(coordinator, lynk_id)
        self.entity_description = description
        self._attr_unique_id = f"{lynk_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.lynk_data.get("overview", {}))


class LynkBatterySensor(LynkCloudBatteryEntity, SensorEntity):
    """A per-battery sensor."""

    entity_description: LynkSensorDescription

    def __init__(self, coordinator, lynk_id: str, battery_sn: str, description: LynkSensorDescription) -> None:
        super().__init__(coordinator, lynk_id, battery_sn)
        self.entity_description = description
        self._attr_unique_id = f"{battery_sn}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.battery_data)

