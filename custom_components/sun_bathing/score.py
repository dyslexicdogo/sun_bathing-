"""Sunbathing score calculation."""

from __future__ import annotations

from dataclasses import dataclass


def _centered_min(value: float, threshold: float, range_: float) -> float:
    """Higher value = better. Score = 50 exactly at threshold."""
    """for temperature, radiation, and UV index."""
    delta = (value - threshold) / range_
    return max(0.0, min(100.0, 50.0 + 50.0 * delta))


def _centered_max(value: float, threshold: float, range_: float) -> float:
    """Lower value = better. Mirror of _centered_min."""
    """for cloud cover, wind speed, and wind gusts."""
    delta = (threshold - value) / range_
    return max(0.0, min(100.0, 50.0 + 50.0 * delta))


@dataclass
class FilterThresholds:
    min_apparent_temp_c: float = 5.0
    apparent_temp_range: float = 10.0

    max_cloud_pct: float = 60.0
    cloud_range: float = 40.0

    min_direct_radiation: float = 300.0
    radiation_range: float = 300.0

    max_wind_speed_kmh: float = 24.1
    wind_speed_range: float = 24.1

    max_wind_gust_kmh: float = 29.0
    wind_gust_range: float = 19.3

    min_uv_index: float = 5.0
    uv_range: float = 5.0


@dataclass
class ScoreWeights:
    apparent_temp: float = 2.0
    cloud_cover: float = 3.0
    direct_radiation: float = 2.5
    wind_speed: float = 1.5
    wind_gust: float = 0.5
    uv_index: float = 0.5


@dataclass
class HourlyConditions:
    apparent_temperature: float
    cloud_cover: float
    direct_radiation: float
    wind_speed: float
    wind_gusts: float
    uv_index: float


def calculate_score(
    conditions: HourlyConditions,
    thresholds: FilterThresholds,
    weights: ScoreWeights,
) -> float:
    factor_scores = {
        "apparent_temp": _centered_min(
            conditions.apparent_temperature, thresholds.min_apparent_temp_c, thresholds.apparent_temp_range
        ),
        "cloud_cover": _centered_max(
            conditions.cloud_cover, thresholds.max_cloud_pct, thresholds.cloud_range
        ),
        "direct_radiation": _centered_min(
            conditions.direct_radiation, thresholds.min_direct_radiation, thresholds.radiation_range
        ),
        "wind_speed": _centered_max(
            conditions.wind_speed, thresholds.max_wind_speed_kmh, thresholds.wind_speed_range
        ),
        "wind_gust": _centered_max(
            conditions.wind_gusts, thresholds.max_wind_gust_kmh, thresholds.wind_gust_range
        ),
        "uv_index": _centered_min(
            conditions.uv_index, thresholds.min_uv_index, thresholds.uv_range
        ),
    }

    raw_weights = {
        "apparent_temp": weights.apparent_temp,
        "cloud_cover": weights.cloud_cover,
        "direct_radiation": weights.direct_radiation,
        "wind_speed": weights.wind_speed,
        "wind_gust": weights.wind_gust,
        "uv_index": weights.uv_index,
    }
    weight_sum = sum(raw_weights.values())
    if weight_sum == 0:
        return 0.0

    weighted_total = sum(factor_scores[k] * (raw_weights[k] / weight_sum) for k in factor_scores)
    return round(weighted_total, 1)