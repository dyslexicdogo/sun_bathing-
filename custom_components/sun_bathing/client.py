"""Open-Meteo API client for sun_bathing."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from aiohttp import ClientError, ClientSession

from .score import HourlyConditions

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY_FIELDS = [
    "apparent_temperature",
    "cloud_cover",
    "direct_radiation",
    "wind_speed_10m",
    "wind_gusts_10m",
    "uv_index",
]


class SunBathingApiError(Exception):
    """Raised when the Open-Meteo call fails or returns bad data."""


class SunBathingApiClient:
    """Fetch and parse Open-Meteo hourly forecast data."""

    def __init__(self, session: ClientSession, latitude: float, longitude: float) -> None:
        self._session = session
        self._latitude = latitude
        self._longitude = longitude

    async def async_get_hourly_conditions(self) -> list[tuple[datetime, HourlyConditions]]:
        """Fetch today's hourly forecast.

        Returns a list of (timestamp, HourlyConditions) tuples, one per hour.
        """
        params = {
            "latitude": self._latitude,
            "longitude": self._longitude,
            "hourly": ",".join(HOURLY_FIELDS),
            "forecast_days": 1,
            "timezone": "auto",
        }

        try:
            async with self._session.get(BASE_URL, params=params) as resp:
                resp.raise_for_status()
                data: dict[str, Any] = await resp.json()
        except ClientError as err:
            raise SunBathingApiError(f"Error communicating with Open-Meteo: {err}") from err

        try:
            hourly = data["hourly"]
            times = hourly["time"]
            results = [
                (
                    datetime.fromisoformat(times[i]),
                    HourlyConditions(
                        apparent_temperature=hourly["apparent_temperature"][i],
                        cloud_cover=hourly["cloud_cover"][i],
                        direct_radiation=hourly["direct_radiation"][i],
                        wind_speed=hourly["wind_speed_10m"][i],
                        wind_gusts=hourly["wind_gusts_10m"][i],
                        uv_index=hourly["uv_index"][i],
                    ),
                )
                for i in range(len(times))
            ]
        except (KeyError, IndexError) as err:
            raise SunBathingApiError(f"Unexpected Open-Meteo response shape: {err}") from err

        return results