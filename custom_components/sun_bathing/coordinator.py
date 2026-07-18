"""DataUpdateCoordinator for sun_bathing."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import SunBathingApiClient, SunBathingApiError
from .const import WINDOW_START_HOURS
from .score import HourlyConditions

_LOGGER = logging.getLogger(__name__)

FORECAST_DAYS = 3
UPDATE_INTERVAL = timedelta(minutes=30)


def _filter_to_window_hours(
    data: list[tuple[datetime, HourlyConditions]]
) -> list[tuple[datetime, HourlyConditions]]:
    """Keep only the hourly points matching a sunbathing window's start hour."""
    return [(ts, cond) for ts, cond in data if ts.hour in WINDOW_START_HOURS]


class SunBathingCoordinator(DataUpdateCoordinator[list[tuple[datetime, HourlyConditions]]]):
    """Coordinator to fetch Open-Meteo data and filter to sunbathing window hours."""

    def __init__(self, hass: HomeAssistant, client: SunBathingApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="sun_bathing",
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> list[tuple[datetime, HourlyConditions]]:
        try:
            raw = await self.client.async_get_hourly_conditions(forecast_days=FORECAST_DAYS)
        except SunBathingApiError as err:
            raise UpdateFailed(str(err)) from err

        return _filter_to_window_hours(raw)