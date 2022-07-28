"""The sensor_node integration."""
from __future__ import annotations

import aiohttp 

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

import json

from .const import DOMAIN

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]


class Api:
    def __init__(self, username, password):
        self.host = "https://egctaz4bvyr6fwlk2p5mq2slna0tkzlf.lambda-url.ap-southeast-2.on.aws/"

        self.username = username
        self.password = password

        # self.session = aiohttp.ClientSession()

        print(self.username)
        print(self.password)

        # self.service = Service(binary_path="")

    async def fetch_data(self):
        """Fetch data from API"""
        # session = await aiohttp.ClientSession()

        async with aiohttp.ClientSession() as session:
            async with session.post(self.host, json={'username': self.username, 'password': self.password}) as response:
                html = await response.text()
                print(html)
                data = json.loads(html)

                return data[0]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up sensor_node from a config entry."""


    # hass.data[DOMAIN][entry.entry_id] = 

    # TODO Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
