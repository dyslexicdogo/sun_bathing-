"""The sun_bathing integration."""
from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import SunBathingApiClient
from .const import DOMAIN
from .coordinator import SunBathingCoordinator

PLATFORMS = ["sensor"]
CARD_URL = "/sun_bathing/sun-bathing-card.js"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up sun_bathing from a config entry."""
    session = async_get_clientsession(hass)
    client = SunBathingApiClient(
        session,
        entry.data["latitude"],
        entry.data["longitude"],
    )

    coordinator = SunBathingCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Serve the card JS from within the integration's own folder.
    # (Not auto-injected via add_extra_js_url - that has a load-order race
    # with Lovelace card rendering on hard refresh. User registers it
    # once manually as a Lovelace resource instead - see README.)
    if DOMAIN not in hass.data.get("_sun_bathing_frontend_registered", set()):
        www_path = Path(__file__).parent / "www"
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    url_path=CARD_URL,
                    path=str(www_path / "sun-bathing-card.js"),
                    cache_headers=False,
                )
            ]
        )
        hass.data.setdefault("_sun_bathing_frontend_registered", set()).add(DOMAIN)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok