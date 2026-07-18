"""Tests for the sun_bathing Open-Meteo API client."""
import re

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.sun_bathing.client import (
    BASE_URL,
    SunBathingApiClient,
    SunBathingApiError,
)

URL_PATTERN = re.compile(rf"^{re.escape(BASE_URL)}.*$")


@pytest.mark.asyncio
async def test_get_hourly_conditions_parses_response(load_fixture):
    """Client should parse a valid Open-Meteo response into HourlyConditions."""
    payload = load_fixture("open_meteo_response.json")

    with aioresponses() as mocked:
        mocked.get(URL_PATTERN, payload=payload, repeat=True)

        async with aiohttp.ClientSession() as session:
            client = SunBathingApiClient(session, 57.47, -4.22)
            result = await client.async_get_hourly_conditions()

    ts, conditions = result[0]
    assert len(result) == 72
    assert ts.hour == 0
    assert conditions.apparent_temperature == payload["hourly"]["apparent_temperature"][0]

    ts16, conditions16 = result[16]
    assert ts16.hour == 16
    assert conditions16.cloud_cover == payload["hourly"]["cloud_cover"][16]

@pytest.mark.asyncio
async def test_get_hourly_conditions_raises_on_bad_shape():
    """Client should raise SunBathingApiError if the response is missing expected keys."""
    with aioresponses() as mocked:
        mocked.get(URL_PATTERN, payload={"hourly": {}}, repeat=True)

        async with aiohttp.ClientSession() as session:
            client = SunBathingApiClient(session, 57.47, -4.22)
            with pytest.raises(SunBathingApiError) as exc_info:
                await client.async_get_hourly_conditions()

    assert "Unexpected Open-Meteo response shape" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_hourly_conditions_raises_on_http_error():
    """Client should raise SunBathingApiError on network/HTTP failure."""
    with aioresponses() as mocked:
        mocked.get(URL_PATTERN, status=500, repeat=True)

        async with aiohttp.ClientSession() as session:
            client = SunBathingApiClient(session, 57.47, -4.22)
            with pytest.raises(SunBathingApiError) as exc_info:
                await client.async_get_hourly_conditions()

    assert "Error communicating with Open-Meteo" in str(exc_info.value)