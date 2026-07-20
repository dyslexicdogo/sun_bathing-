"""Tests for sun_bathing sensor entities."""
from datetime import date, datetime, timedelta

import pytest

from custom_components.sun_bathing.const import (
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
    CONF_WEIGHT_UV_INDEX,
)
from custom_components.sun_bathing.helpers import build_thresholds, build_weights
from custom_components.sun_bathing.score import HourlyConditions
from custom_components.sun_bathing.sensor import SunBathingWindowSensor


def _make_conditions(**overrides) -> HourlyConditions:
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


class FakeCoordinator:
    """Minimal stand-in for SunBathingCoordinator, just holding .data."""

    def __init__(self, data):
        self.data = data

    @property
    def last_update_success(self):
        return True

    def async_add_listener(self, update_callback, context=None):
        # CoordinatorEntity registers a listener on init; return a no-op remover.
        return lambda: None


def _make_sensor(coordinator, start_hour=10, end_hour=11, sample_entry_data=None):
    thresholds = build_thresholds(sample_entry_data)
    weights = build_weights(sample_entry_data)
    return SunBathingWindowSensor(
        coordinator, start_hour, end_hour, thresholds, weights, "test_entry_id"
    )


def test_native_value_returns_score_for_todays_window(sample_entry_data):
    today = date.today()
    conditions = _make_conditions(cloud_cover=0, direct_radiation=500)  # good conditions
    coordinator = FakeCoordinator(
        data=[(datetime(today.year, today.month, today.day, 10, 0), conditions)]
    )
    sensor = _make_sensor(coordinator, start_hour=10, end_hour=11, sample_entry_data=sample_entry_data)

    value = sensor.native_value

    assert value is not None
    assert 0 <= value <= 100


def test_native_value_returns_none_when_hour_missing(sample_entry_data):
    today = date.today()
    conditions = _make_conditions()
    coordinator = FakeCoordinator(
        data=[(datetime(today.year, today.month, today.day, 12, 0), conditions)]  # wrong hour
    )
    sensor = _make_sensor(coordinator, start_hour=10, end_hour=11, sample_entry_data=sample_entry_data)

    assert sensor.native_value is None


def test_native_value_ignores_other_days_same_hour(sample_entry_data):
    """A matching hour on a different day should not be picked."""
    today = date.today()
    tomorrow = today.replace(day=today.day + 1) if today.day < 28 else today  # simple same-month bump
    conditions_tomorrow = _make_conditions(cloud_cover=99)
    coordinator = FakeCoordinator(
        data=[(datetime(tomorrow.year, tomorrow.month, tomorrow.day, 10, 0), conditions_tomorrow)]
    )
    sensor = _make_sensor(coordinator, start_hour=10, end_hour=11, sample_entry_data=sample_entry_data)

    assert sensor.native_value is None


def test_extra_state_attributes_contains_raw_score(sample_entry_data):
    today = date.today()
    conditions = _make_conditions()
    coordinator = FakeCoordinator(
        data=[(datetime(today.year, today.month, today.day, 13, 0), conditions)]
    )
    sensor = _make_sensor(coordinator, start_hour=13, end_hour=14, sample_entry_data=sample_entry_data)

    attrs = sensor.extra_state_attributes

    assert "raw_score" in attrs
    assert isinstance(attrs["raw_score"], float)


def test_unique_id_and_name_reflect_window(sample_entry_data):
    coordinator = FakeCoordinator(data=[])
    sensor = _make_sensor(coordinator, start_hour=14, end_hour=15, sample_entry_data=sample_entry_data)

    assert sensor.unique_id == "test_entry_id_window_14_15"
    assert sensor.name == "Sunbathing score 14:00-15:00"

def test_extra_state_attributes_contains_all_weather_fields(sample_entry_data):
    today = date.today()
    conditions = _make_conditions(
        apparent_temperature=18.5, cloud_cover=30, direct_radiation=450,
        wind_speed=12.0, wind_gusts=20.0, uv_index=6.0,
    )
    coordinator = FakeCoordinator(
        data=[(datetime(today.year, today.month, today.day, 13, 0), conditions)]
    )
    sensor = _make_sensor(coordinator, start_hour=13, end_hour=14, sample_entry_data=sample_entry_data)

    attrs = sensor.extra_state_attributes

    assert attrs["apparent_temperature"] == 18.5
    assert attrs["cloud_cover"] == 30
    assert attrs["direct_radiation"] == 450
    assert attrs["wind_speed"] == 12.0
    assert attrs["wind_gusts"] == 20.0
    assert attrs["uv_index"] == 6.0

def test_extra_state_attributes_includes_3_day_forecast(sample_entry_data):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    day_plus_2 = today + timedelta(days=2)

    coordinator = FakeCoordinator(data=[
        (datetime(today.year, today.month, today.day, 10, 0), _make_conditions(cloud_cover=10)),
        (datetime(tomorrow.year, tomorrow.month, tomorrow.day, 10, 0), _make_conditions(cloud_cover=50)),
        (datetime(day_plus_2.year, day_plus_2.month, day_plus_2.day, 10, 0), _make_conditions(cloud_cover=90)),
    ])
    sensor = _make_sensor(coordinator, start_hour=10, end_hour=11, sample_entry_data=sample_entry_data)

    forecast = sensor.extra_state_attributes["forecast"]

    assert len(forecast) == 3
    assert [f["day_offset"] for f in forecast] == [0, 1, 2]
    assert all(f["score"] is not None for f in forecast)
    # cloudier days should score lower for this field, confirming correct day matched
    assert forecast[0]["cloud_cover"] == 10
    assert forecast[1]["cloud_cover"] == 50
    assert forecast[2]["cloud_cover"] == 90


def test_forecast_entry_is_none_when_day_missing(sample_entry_data):
    today = date.today()
    coordinator = FakeCoordinator(data=[
        (datetime(today.year, today.month, today.day, 10, 0), _make_conditions()),
        # tomorrow and day+2 deliberately missing
    ])
    sensor = _make_sensor(coordinator, start_hour=10, end_hour=11, sample_entry_data=sample_entry_data)

    forecast = sensor.extra_state_attributes["forecast"]

    assert forecast[0]["score"] is not None
    assert forecast[1]["score"] is None
    assert forecast[2]["score"] is None