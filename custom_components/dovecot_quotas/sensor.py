"""Sensor setup for our Integration."""

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.components.sensor.const import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorStateClass,
)


from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfInformation,
)
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import DovecotQuotasUpdateCoordinator

from .const import (
    DOMAIN,
    MODEL,
    MANUFACTURER,
    CONF_ACCOUNTS,
    CONF_VERSION,
)


def get_sensor_descriptions() -> list[SensorEntityDescription]:
    descriptions: list[SensorEntityDescription] = [
        SensorEntityDescription(
            key="quota",
            translation_key="quota",
            icon="mdi:car-speed-limiter",
            device_class=SensorDeviceClass.DATA_SIZE,
            native_unit_of_measurement=UnitOfInformation.KILOBYTES,
            suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
            suggested_display_precision=1,
        ),
        SensorEntityDescription(
            key="used",
            translation_key="used",
            icon="mdi:gauge-low",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.DATA_SIZE,
            native_unit_of_measurement=UnitOfInformation.KILOBYTES,
            suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
            suggested_display_precision=1,
        ),
        SensorEntityDescription(
            key="percentage_used",
            translation_key="percentage_used",
            icon="mdi:percent-outline",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="free",
            translation_key="free",
            icon="mdi:gauge-low",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.DATA_SIZE,
            native_unit_of_measurement=UnitOfInformation.KILOBYTES,
            suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
            suggested_display_precision=1,
            entity_registry_enabled_default=False,
        ),
        SensorEntityDescription(
            key="percentage_free",
            translation_key="percentage_free",
            icon="mdi:percent-outline",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        ),
    ]
    return descriptions


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Dovecot Quotas sensors based on a config entry."""
    coordinator: DovecotQuotasUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    entities: list[AccountSensor] = []

    # Add all sensors described above.
    for account in config_entry.data.get(CONF_ACCOUNTS, []):
        for description in get_sensor_descriptions():
            entities.append(
                AccountSensor(
                    coordinator=coordinator,
                    entry_id=config_entry.entry_id,
                    description=description,
                    account=account,
                )
            )
    async_add_entities(entities)


class AccountSensor(CoordinatorEntity[DovecotQuotasUpdateCoordinator], SensorEntity):
    """Defines a Dovecot Quotas sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DovecotQuotasUpdateCoordinator,
        entry_id: str,
        description: SensorEntityDescription,
        account: str,
    ) -> None:
        """Initialize Dovecot Quotas sensor."""
        super().__init__(coordinator=coordinator)
        version = coordinator.data.get(CONF_VERSION, None)
        self.entity_description = description
        self.entity_id = f"{SENSOR_DOMAIN}.{account} {description.key}".lower()
        self._attr_unique_id = f"{entry_id}-{account} {description.key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, account)},
            name=account,
            model=MODEL,
            manufacturer=MANUFACTURER,
            sw_version=version,
        )
        self._account = account

    @property
    def native_value(self) -> StateType:  # type: ignore
        """Return the state of the sensor."""
        accounts = self.coordinator.data.get(CONF_ACCOUNTS, {})
        quota_info = accounts.get(self._account, None)
        return quota_info.get(self.entity_description.key, None)
