"""Helpers for converting a config entry's flat data into scoring dataclasses."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_MIN_APPARENT_TEMP_C,
    CONF_APPARENT_TEMP_RANGE,
    CONF_MAX_CLOUD_PCT,
    CONF_CLOUD_RANGE,
    CONF_MIN_DIRECT_RADIATION,
    CONF_RADIATION_RANGE,
    CONF_MAX_WIND_SPEED_KMH,
    CONF_WIND_SPEED_RANGE,
    CONF_MAX_WIND_GUST_KMH,
    CONF_WIND_GUST_RANGE,
    CONF_MIN_UV_INDEX,
    CONF_UV_RANGE,
    CONF_WEIGHT_APPARENT_TEMP,
    CONF_WEIGHT_CLOUD_COVER,
    CONF_WEIGHT_DIRECT_RADIATION,
    CONF_WEIGHT_WIND_SPEED,
    CONF_WEIGHT_WIND_GUST,
    CONF_WEIGHT_UV_INDEX,
)
from .score import FilterThresholds, ScoreWeights


def build_thresholds(data: dict) -> FilterThresholds:
    """Build a FilterThresholds dataclass from a config entry's data dict."""
    return FilterThresholds(
        min_apparent_temp_c=data[CONF_MIN_APPARENT_TEMP_C],
        apparent_temp_range=data[CONF_APPARENT_TEMP_RANGE],
        max_cloud_pct=data[CONF_MAX_CLOUD_PCT],
        cloud_range=data[CONF_CLOUD_RANGE],
        min_direct_radiation=data[CONF_MIN_DIRECT_RADIATION],
        radiation_range=data[CONF_RADIATION_RANGE],
        max_wind_speed_kmh=data[CONF_MAX_WIND_SPEED_KMH],
        wind_speed_range=data[CONF_WIND_SPEED_RANGE],
        max_wind_gust_kmh=data[CONF_MAX_WIND_GUST_KMH],
        wind_gust_range=data[CONF_WIND_GUST_RANGE],
        min_uv_index=data[CONF_MIN_UV_INDEX],
        uv_range=data[CONF_UV_RANGE],
    )


def build_weights(data: dict) -> ScoreWeights:
    """Build a ScoreWeights dataclass from a config entry's data dict."""
    return ScoreWeights(
        apparent_temp=data[CONF_WEIGHT_APPARENT_TEMP],
        cloud_cover=data[CONF_WEIGHT_CLOUD_COVER],
        direct_radiation=data[CONF_WEIGHT_DIRECT_RADIATION],
        wind_speed=data[CONF_WEIGHT_WIND_SPEED],
        wind_gust=data[CONF_WEIGHT_WIND_GUST],
        uv_index=data[CONF_WEIGHT_UV_INDEX],
    )