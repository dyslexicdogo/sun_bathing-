# tests/test_helpers.py
from custom_components.sun_bathing.helpers import build_thresholds, build_weights
from custom_components.sun_bathing.const import (
    CONF_MIN_APPARENT_TEMP_C, CONF_WEIGHT_CLOUD_COVER,
    # ...etc, or just build a full fake entry.data dict inline
)


def test_build_thresholds_maps_all_fields(sample_entry_data):
    thresholds = build_thresholds(sample_entry_data)
    assert thresholds.min_apparent_temp_c == sample_entry_data[CONF_MIN_APPARENT_TEMP_C]
    # ... one assertion per field, or just spot-check a few + assert no exception


def test_build_weights_maps_all_fields(sample_entry_data):
    weights = build_weights(sample_entry_data)
    assert weights.cloud_cover == sample_entry_data[CONF_WEIGHT_CLOUD_COVER]