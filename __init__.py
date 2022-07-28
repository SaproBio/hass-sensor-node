"""The sensor_node integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from selenium import webdriver

from chromedriver_py import binary_path

from .const import DOMAIN

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.LIGHT]


class Api:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

        self.service = Service(binary_path)
        self.driver = webdriver.Chrome(service=self.service)

    async def fetch_data(self):
        """Fetch data from API"""
        self.driver.get(self.host)

        elements = self.driver.find_elements(
            By.CLASS_NAME, "native-input sc-ion-input-md"
        )
        elements[0].send_keys(self.username)
        elements[1].send_keys(self.password)

        self.driver.find_elements(By.CLASS_NAME, "md button")[0].send_keys(Keys.ENTER)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up sensor_node from a config entry."""

    hass.data[DOMAIN][entry.entry_id] = Api(
        entry.data.get("host"), entry.data.get("username"), entry.data.get("password")
    )

    # TODO Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
