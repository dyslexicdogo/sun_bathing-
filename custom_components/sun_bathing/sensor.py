"""Sensor platform for sun_bathing."""
from __future__ import annotations

from datetime import date

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
    """Score for a single 1-hour sunbathing window, for today."""

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
        """Return today's score for this window, or None if data isn't available."""
        conditions = self._pick_todays_conditions()
        if conditions is None:
            return None
        raw_score = calculate_score(conditions, self._thresholds, self._weights)
        return round(raw_score)

    @property
    def extra_state_attributes(self) -> dict:
        """Expose the unrounded score for future precision needs (e.g. color-scale display)."""
        conditions = self._pick_todays_conditions()
        if conditions is None:
            return {}
        raw_score = calculate_score(conditions, self._thresholds, self._weights)
        return {"raw_score": raw_score}

    def _pick_todays_conditions(self):
        """Find today's hourly conditions matching this window's start hour."""
        today = date.today()
        for ts, conditions in self.coordinator.data:
            if ts.hour == self._start_hour and ts.date() == today:
                return conditions
        return None
    
    @property
    def extra_state_attributes(self) -> dict:
        """Expose raw score and underlying weather values for Lovelace/notifications."""
        conditions = self._pick_todays_conditions()
        if conditions is None:
            return {}
        raw_score = calculate_score(conditions, self._thresholds, self._weights)
        return {
            "raw_score": raw_score,
            "apparent_temperature": conditions.apparent_temperature,
            "cloud_cover": conditions.cloud_cover,
            "direct_radiation": conditions.direct_radiation,
            "wind_speed": conditions.wind_speed,
            "wind_gusts": conditions.wind_gusts,
            "uv_index": conditions.uv_index,
            }