"""Integration tests for sun_bathing's __init__.py setup/unload."""
import re
from datetime import datetime, timezone

from aioresponses import aioresponses
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sun_bathing.client import BASE_URL
from custom_components.sun_bathing.const import DOMAIN

URL_PATTERN = re.compile(rf"^{re.escape(BASE_URL)}.*$")


def _open_meteo_payload_for_today():
    """Build a minimal but realistic 3-day Open-Meteo payload covering all window hours."""
    today = datetime.now(timezone.utc).date()
    times = []
    apparent_temperature = []
    cloud_cover = []
    direct_radiation = []
    wind_speed_10m = []
    wind_gusts_10m = []
    uv_index = []

    for day_offset in range(3):
        for hour in range(24):
            d = today.replace(day=today.day) if day_offset == 0 else today  # keep simple, single day is enough for setup test
            times.append(f"{d.isoformat()}T{hour:02d}:00")
            apparent_temperature.append(18.0)
            cloud_cover.append(20)
            direct_radiation.append(400)
            wind_speed_10m.append(10.0)
            wind_gusts_10m.append(15.0)
            uv_index.append(5.0)

    return {
        "hourly": {
            "time": times,
            "apparent_temperature": apparent_temperature,
            "cloud_cover": cloud_cover,
            "direct_radiation": direct_radiation,
            "wind_speed_10m": wind_speed_10m,
            "wind_gusts_10m": wind_gusts_10m,
            "uv_index": uv_index,
        }
    }


async def test_setup_and_unload_entry(hass, sample_entry_data):
    """Setting up the config entry should create 7 sensor entities with real states."""
    assert await async_setup_component(hass, "http", {})
    await hass.async_block_till_done()

    entry_data = {**sample_entry_data}  # includes latitude/longitude + all 18 threshold/range/weight keys
    entry = MockConfigEntry(domain=DOMAIN, data=entry_data)
    entry.add_to_hass(hass)

    with aioresponses() as mocked:
        mocked.get(URL_PATTERN, payload=_open_meteo_payload_for_today(), repeat=True)

        setup_ok = await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert setup_ok is True
    assert entry.state.value == "loaded"

    # confirm all 7 window sensors exist with a real numeric state
    for start, end in [(10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17)]:
        entity_id = f"sensor.sunbathing_score_{start}_00_{end}_00"
        state = hass.states.get(entity_id)
        assert state is not None, f"{entity_id} was not created"
        assert state.state != "unavailable"
        assert 0 <= int(state.state) <= 100

    # unload should clean up hass.data
    unload_ok = await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert unload_ok is True
    assert entry.entry_id not in hass.data.get(DOMAIN, {})


async def test_setup_entry_handles_api_failure(hass, sample_entry_data):
    """If Open-Meteo fails during first refresh, setup should raise ConfigEntryNotReady (retry later)."""
    entry = MockConfigEntry(domain=DOMAIN, data=sample_entry_data)
    entry.add_to_hass(hass)

    with aioresponses() as mocked:
        mocked.get(URL_PATTERN, status=500, repeat=True)

        setup_ok = await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # first refresh failing should leave the entry in a retry state, not crash
    assert setup_ok is False
    assert entry.state.value == "setup_retry"