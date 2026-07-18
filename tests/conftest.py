"""Shared pytest fixtures."""
import json
from pathlib import Path

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
    CONF_WEIGHT_UV_INDEX
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def load_fixture():
    """Return a function that loads and parses a JSON fixture by filename."""
    def _load(filename: str):
        path = FIXTURES_DIR / filename
        return json.loads(path.read_text())
    return _load

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom_components/ during tests (required by pytest-homeassistant-custom-component)."""
    yield


@pytest.fixture
def sample_entry_data():
    """A full flat entry.data dict, matching what config_flow produces after all 4 steps."""
    return {
        "latitude": 57.47,
        "longitude": -4.22,

        CONF_MIN_APPARENT_TEMP_C: 5.0,
        CONF_MAX_CLOUD_PCT: 60.0,
        CONF_MIN_DIRECT_RADIATION: 300.0,
        CONF_MAX_WIND_SPEED_KMH: 24.1,
        CONF_MAX_WIND_GUST_KMH: 29.0,
        CONF_MIN_UV_INDEX: 5.0,

        CONF_APPARENT_TEMP_RANGE: 10.0,
        CONF_CLOUD_RANGE: 40.0,
        CONF_RADIATION_RANGE: 300.0,
        CONF_WIND_SPEED_RANGE: 24.1,
        CONF_WIND_GUST_RANGE: 19.3,
        CONF_UV_RANGE: 5.0,

        CONF_WEIGHT_APPARENT_TEMP: 2.0,
        CONF_WEIGHT_CLOUD_COVER: 3.0,
        CONF_WEIGHT_DIRECT_RADIATION: 2.5,
        CONF_WEIGHT_WIND_SPEED: 1.5,
        CONF_WEIGHT_WIND_GUST: 0.5,
        CONF_WEIGHT_UV_INDEX: 0.5,
    }
