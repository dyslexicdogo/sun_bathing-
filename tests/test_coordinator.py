"""Tests for the sun_bathing coordinator."""
from datetime import datetime

import pytest

from custom_components.sun_bathing.coordinator import (
    SunBathingCoordinator,
    _filter_to_window_hours,
)
from custom_components.sun_bathing.score import HourlyConditions


def _make_conditions(**overrides) -> HourlyConditions:
    """Build a HourlyConditions with sensible defaults, overridable per test."""
    defaults = dict(
        apparent_temperature=15.0,
        cloud_cover=20,
        direct_radiation=400,
        wind_speed=10.0,
        wind_gusts=15.0,
        uv_index=4.0,
    )
    defaults.update(overrides)
    return HourlyConditions(**defaults)


def test_filter_to_window_hours_keeps_only_window_start_hours():
    data = [
        (datetime(2026, 7, 18, 9, 0), _make_conditions()),
        (datetime(2026, 7, 18, 10, 0), _make_conditions()),
        (datetime(2026, 7, 18, 13, 0), _make_conditions()),
        (datetime(2026, 7, 18, 17, 0), _make_conditions()),
        (datetime(2026, 7, 18, 22, 0), _make_conditions()),
    ]

    result = _filter_to_window_hours(data)

    result_hours = [ts.hour for ts, _ in result]
    assert result_hours == [10, 13]


class FakeApiClient:
    """Stub client returning canned data instead of hitting Open-Meteo."""

    def __init__(self, data):
        self._data = data
        self.last_forecast_days = None

    async def async_get_hourly_conditions(self, forecast_days=1):
        self.last_forecast_days = forecast_days
        return self._data


@pytest.mark.asyncio
async def test_coordinator_filters_fetched_data(hass):
    raw_data = [
        (datetime(2026, 7, 18, 9, 0), _make_conditions()),
        (datetime(2026, 7, 18, 10, 0), _make_conditions(cloud_cover=50)),
        (datetime(2026, 7, 18, 22, 0), _make_conditions()),
    ]
    fake_client = FakeApiClient(raw_data)
    coordinator = SunBathingCoordinator(hass, fake_client)

    result = await coordinator._async_update_data()

    assert len(result) == 1
    ts, conditions = result[0]
    assert ts.hour == 10
    assert conditions.cloud_cover == 50
    assert fake_client.last_forecast_days == 3