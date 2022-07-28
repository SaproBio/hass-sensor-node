"""Platform for SaproBio sensor node integration."""
from __future__ import annotations
from datetime import timedelta
from homeassistant.exceptions import ConfigEntryAuthFailed
import logging

from . import Api

import async_timeout

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from homeassistant.const import (
    TEMP_CELSIUS,
    PERCENTAGE,
    CONCENTRATION_PARTS_PER_MILLION,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


_LOGGER = logging.getLogger(__name__)


class DataFetcher(DataUpdateCoordinator):
    def __init__(self, hass, my_api):
        super().__init__(
            hass, _LOGGER, name="Sensor Node", update_interval=timedelta(minutes=1)
        )
        self.my_api = my_api
        self.data = [0, 0, 0]

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(60):
                data = await self.my_api.fetch_data()
                print("DATA")
                print(data)

                self.data[0] = data["humidity"]
                self.data[1] = data["temperature"]
                self.data[2] = data["co2"]

                return data
        # except ApiAuthError as err:
        # Raising ConfigEntryAuthFailed will cancel future updates
        # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #    raise ConfigEntryAuthFailed from err
        except:
            raise UpdateFailed(f"Error communicating with API")


async def async_setup_entry(hass, entry, async_add_entities) -> None:

    my_api = Api(
        entry.data["username"], entry.data["password"]
    )
    #  = hass.data[DOMAIN][entry.entry_id]
    coordinator = DataFetcher(hass, my_api)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [Humidity(coordinator, 0), Temperature(coordinator, 1), Carbon(coordinator, 2)],
        True
    )


class Temperature(CoordinatorEntity, SensorEntity):
    """Representation of a sensor temperature sensor"""

    _attr_name = "Temperature"
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, idx) -> None:
        super().__init__(coordinator)
        self.idx = idx

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle date from coordinator"""
        print(self.coordinator.data)
        self._attr_native_value = self.coordinator.data["temperature"]


class Carbon(CoordinatorEntity, SensorEntity):
    """Representation of a sensor carbon sensor"""

    def __init__(self, coordinator, idx) -> None:
        super().__init__(coordinator)
        self.idx = idx

    _attr_name = "Carbon Dioxide"
    _attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
    _attr_device_class = SensorDeviceClass.CO2
    _attr_state_class = SensorStateClass.MEASUREMENT

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle date from coordinator"""
        print(self.coordinator.data)
        self._attr_native_value = self.coordinator.data["co2"]


class Humidity(CoordinatorEntity, SensorEntity):
    """Representation of a sensor humidity sensor"""

    def __init__(self, coordinator, idx) -> None:
        super().__init__(coordinator)
        self.idx = idx

    _attr_name = "Humidity"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle date from coordinator"""
        print(self.coordinator.data)
        self._attr_native_value = self.coordinator.data["humidity"]