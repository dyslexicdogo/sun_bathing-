from __future__ import annotations
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import (
    DOMAIN, 
    OPEN_METEO_URL,
    CONF_MIN_APPARENT_TEMP_C,
    CONF_MAX_CLOUD_PCT,
    CONF_MIN_DIRECT_RADIATION,
    CONF_MAX_WIND_SPEED_KMH,
    CONF_MAX_WIND_GUST_KMH,
    CONF_MIN_UV_INDEX,

    CONF_APPARENT_TEMP_RANGE,
    CONF_CLOUD_RANGE,
    CONF_RADIATION_RANGE,
    CONF_WIND_SPEED_RANGE,
    CONF_WIND_GUST_RANGE,
    CONF_UV_RANGE,

    CONF_WEIGHT_APPARENT_TEMP,
    CONF_WEIGHT_CLOUD_COVER,
    CONF_WEIGHT_DIRECT_RADIATION,
    CONF_WEIGHT_WIND_SPEED,
    CONF_WEIGHT_WIND_GUST,
    CONF_WEIGHT_UV_INDEX
)



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

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data = {}

    def _location_schema(self):
        return vol.Schema({
            vol.Required("latitude", default=self.hass.config.latitude): vol.All(vol.Coerce(float), vol.Range(min=-90, max=90)),
            vol.Required("longitude", default=self.hass.config.longitude): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180)),
        })
    
    def _thresholds_schema(self):
        return vol.Schema({
            vol.Required(CONF_MIN_APPARENT_TEMP_C, default=5.0): vol.All(vol.Coerce(float), vol.Range(min=-20, max=40)),
            vol.Required(CONF_MAX_CLOUD_PCT, default=60.0): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
            vol.Required(CONF_MIN_DIRECT_RADIATION, default=300.0): vol.All(vol.Coerce(float), vol.Range(min=0, max=1000)),
            vol.Required(CONF_MAX_WIND_SPEED_KMH, default=24.1): vol.All(vol.Coerce(float), vol.Range(min=0, max=80)),
            vol.Required(CONF_MAX_WIND_GUST_KMH, default=29.0): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
            vol.Required(CONF_MIN_UV_INDEX, default=5.0): vol.All(vol.Coerce(float), vol.Range(min=0, max=11)),
        })
    
    def _ranges_schema(self):
        return vol.Schema({
            vol.Required(CONF_APPARENT_TEMP_RANGE, default=10.0): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=50)),
            vol.Required(CONF_CLOUD_RANGE, default=40.0): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_RADIATION_RANGE, default=300.0): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000)),
            vol.Required(CONF_WIND_SPEED_RANGE, default=24.1): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=80)),
            vol.Required(CONF_WIND_GUST_RANGE, default=19.3): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_UV_RANGE, default=5.0): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=11)),
        })
    
    def _weights_schema(self):
        return vol.Schema({
            vol.Required(CONF_WEIGHT_APPARENT_TEMP, default=2.0): vol.All(vol.Coerce(float), vol.Range(min=0, max=5)),
            vol.Required(CONF_WEIGHT_CLOUD_COVER, default=3.0): vol.All(vol.Coerce(float), vol.Range(min=0, max=5)),
            vol.Required(CONF_WEIGHT_DIRECT_RADIATION, default=2.5): vol.All(vol.Coerce(float), vol.Range(min=0, max=5)),
            vol.Required(CONF_WEIGHT_WIND_SPEED, default=1.5): vol.All(vol.Coerce(float), vol.Range(min=0, max=5)),
            vol.Required(CONF_WEIGHT_WIND_GUST, default=0.5): vol.All(vol.Coerce(float), vol.Range(min=0, max=5)),
            vol.Required(CONF_WEIGHT_UV_INDEX, default=0.5): vol.All(vol.Coerce(float), vol.Range(min=0, max=5)),
        })

    async def async_step_user(self, user_input: dict | None = None):
        if user_input is not None:
            try:
                await _validate_location(self.hass, user_input["latitude"], user_input["longitude"])
            except (aiohttp.ClientError, ValueError, KeyError):
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._location_schema(),
                    errors={"base": "cannot_connect"},
                )
            self._data.update(user_input)
            return await self.async_step_thresholds()
        
        return self.async_show_form(
            step_id="user",
            data_schema=self._location_schema(),
        )
    
    async def async_step_thresholds(self, user_input: dict | None = None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_ranges()
        
        return self.async_show_form(
            step_id="thresholds",
            data_schema=self._thresholds_schema(),
        )
    
    async def async_step_ranges(self, user_input: dict | None = None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_weights()
        
        return self.async_show_form(
            step_id="ranges",
            data_schema=self._ranges_schema(),
        )
    
    async def async_step_weights(self, user_input: dict | None = None):
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="Sun Bathing", data=self._data)
        
        return self.async_show_form(
            step_id="weights",
            data_schema=self._weights_schema(),
        )
