"""Sensor platform for sun_bathing."""
from __future__ import annotations

from datetime import date, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunBathingCoordinator
from .helpers import build_thresholds, build_weights
from .score import calculate_score

WINDOWS = [(10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17)]
FORECAST_DAY_OFFSETS = (0, 1, 2)  # today, tomorrow, day+2


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sun_bathing window sensors from a config entry."""
    coordinator: SunBathingCoordinator = hass.data[DOMAIN][entry.entry_id]

    thresholds = build_thresholds(entry.data)
    weights = build_weights(entry.data)

    entities = [
        SunBathingWindowSensor(coordinator, start, end, thresholds, weights, entry.entry_id)
        for start, end in WINDOWS
    ]
    async_add_entities(entities)


class SunBathingWindowSensor(CoordinatorEntity, SensorEntity):
    """Score for a single 1-hour sunbathing window, with a 3-day forecast attribute."""

    _attr_icon = "mdi:weather-sunny"
    _attr_native_unit_of_measurement = None

    def __init__(self, coordinator, start_hour, end_hour, thresholds, weights, entry_id):
        super().__init__(coordinator)
        self._start_hour = start_hour
        self._thresholds = thresholds
        self._weights = weights
        self._attr_unique_id = f"{entry_id}_window_{start_hour}_{end_hour}"
        self._attr_name = f"Sunbathing score {start_hour}:00-{end_hour}:00"

    @property
    def native_value(self) -> int | None:
        """Return today's score for this window (day_offset=0), or None if unavailable."""
        conditions = self._pick_conditions_for_day(date.today())
        if conditions is None:
            return None
        return round(calculate_score(conditions, self._thresholds, self._weights))

    @property
    def extra_state_attributes(self) -> dict:
        """Expose today's raw values/thresholds plus a 3-day forecast list."""
        today = date.today()
        conditions = self._pick_conditions_for_day(today)
        t = self._thresholds

        attrs = {
            "min_apparent_temp_c": t.min_apparent_temp_c,
            "apparent_temp_range": t.apparent_temp_range,
            "max_cloud_pct": t.max_cloud_pct,
            "cloud_range": t.cloud_range,
            "min_direct_radiation": t.min_direct_radiation,
            "radiation_range": t.radiation_range,
            "max_wind_speed_kmh": t.max_wind_speed_kmh,
            "wind_speed_range": t.wind_speed_range,
            "max_wind_gust_kmh": t.max_wind_gust_kmh,
            "wind_gust_range": t.wind_gust_range,
            "min_uv_index": t.min_uv_index,
            "uv_range": t.uv_range,
        }

        if conditions is not None:
            attrs["raw_score"] = calculate_score(conditions, self._thresholds, self._weights)
            attrs["apparent_temperature"] = conditions.apparent_temperature
            attrs["cloud_cover"] = conditions.cloud_cover
            attrs["direct_radiation"] = conditions.direct_radiation
            attrs["wind_speed"] = conditions.wind_speed
            attrs["wind_gusts"] = conditions.wind_gusts
            attrs["uv_index"] = conditions.uv_index

        attrs["forecast"] = self._build_forecast()
        return attrs

    def _build_forecast(self) -> list[dict]:
        """Build a list of per-day forecast entries for day_offset 0, 1, 2."""
        forecast = []
        today = date.today()
        for offset in FORECAST_DAY_OFFSETS:
            target_date = today + timedelta(days=offset)
            conditions = self._pick_conditions_for_day(target_date)
            if conditions is None:
                forecast.append({"day_offset": offset, "score": None})
                continue
            score = round(calculate_score(conditions, self._thresholds, self._weights))
            forecast.append({
                "day_offset": offset,
                "score": score,
                "apparent_temperature": conditions.apparent_temperature,
                "cloud_cover": conditions.cloud_cover,
                "direct_radiation": conditions.direct_radiation,
                "wind_speed": conditions.wind_speed,
                "wind_gusts": conditions.wind_gusts,
                "uv_index": conditions.uv_index,
            })
        return forecast

    def _pick_conditions_for_day(self, target_date: date):
        """Find hourly conditions matching this window's start hour on the given date."""
        for ts, conditions in self.coordinator.data:
            if ts.hour == self._start_hour and ts.date() == target_date:
                return conditions
        return None
    