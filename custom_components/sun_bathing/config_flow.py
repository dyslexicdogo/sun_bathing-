from __future__ import annotations
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, OPEN_METEO_URL



async def _validate_location(hass, latitude: float, longitude: float) -> None:
    session = async_get_clientsession(hass)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m"}
    async with session.get(OPEN_METEO_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
        response.raise_for_status()
        await response.json()  # We don't need the data, just checking if the request is successful.


class SunBathingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sun Bathing."""

    VERSION = 1

    def _schema(self):
        return vol.Schema({
            vol.Required("latitude", default=self.hass.config.latitude): vol.All(vol.Coerce(float), vol.Range(min=-90, max=90)),
            vol.Required("longitude", default=self.hass.config.longitude): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180)),
        })

    async def async_step_user(self, user_input: dict | None = None):
        if user_input is not None:
            try:
                await _validate_location(self.hass, user_input["latitude"], user_input["longitude"])
            except (aiohttp.ClientError, ValueError, KeyError):
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._schema(),
                    errors={"base": "cannot_connect"},
                )
            
            return self.async_create_entry(
                title="Sun Bathing", 
                data=user_input)
        
        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(),
        )
