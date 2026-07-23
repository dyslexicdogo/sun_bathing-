# ☀️ Sun Bathing

A Home Assistant custom integration that scores hourly sunbathing conditions
using [Open-Meteo](https://open-meteo.com/) weather data — tuned for places
where good weather is rare enough that the thresholds need to be forgiving
(built with Inverness, Scotland in mind).

Each day is split into seven one-hour windows (10am–5pm), each scored 0–100
based on apparent temperature, cloud cover, direct solar radiation, wind
speed, wind gusts, and UV index. Includes a custom Lovelace card with a
tabbed 3-day forecast view, and a ready-made notification blueprint.

## Features

- 🌤️ **7 hourly window sensors** (10am–11am through 4pm–5pm), each scored 0–100
- 📅 **3-day forecast** built into every sensor's attributes
- 🎨 **Custom Lovelace card** — color-coded scores, threshold-aware icons, tabbed day view
- 🔔 **Notification blueprint** — get notified of the day's best window, on your terms
- ⚙️ **Fully configurable thresholds** — tune what counts as "good enough" weather for each factor
- 🧪 **Tested** — full test suite across the API client, coordinator, and sensors

## Installation

### HACS (recommended)

1. In HACS, go to **Integrations → ⋮ → Custom repositories**
2. Add `https://github.com/dyslexicdogo/sun_bathing` as an **Integration**
3. Search for "Sun Bathing" in HACS and install
4. Restart Home Assistant

### Manual

1. Copy `custom_components/sun_bathing` into your Home Assistant `config/custom_components/` folder
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Sun Bathing**
3. Walk through the 4-step setup wizard:
   - **Location** — latitude/longitude (defaults to your Home Assistant location)
   - **Thresholds** — the "good enough" value for each weather factor
   - **Ranges** — how quickly each factor's score falls off as conditions move away from the threshold
   - **Weights** — how much each factor matters to your overall score (0–5 each; these auto-normalize, so they don't need to add up to anything specific)

Once complete, you'll have 7 sensor entities:
`sensor.sunbathing_score_10_00_11_00` through `sensor.sunbathing_score_16_00_17_00`.

### Default thresholds

Tuned for Inverness, Scotland — forgiving on purpose. Adjust freely for your climate.

| Factor | Threshold | Range | Weight |
|---|---|---|---|
| Min apparent temperature | 5.0 °C | 10.0 | 2.0 |
| Max cloud cover | 60% | 40 | 3.0 |
| Min direct radiation | 300 W/m² | 300 | 2.5 |
| Max wind speed | 24.1 km/h | 24.1 | 1.5 |
| Max wind gust | 29.0 km/h | 19.3 | 0.5 |
| Min UV index | 5.0 | 5.0 | 0.5 |

> **Note:** there's currently no way to change these after initial setup other
> than removing and re-adding the integration. An options flow for in-place
> editing is planned.

## The Lovelace Card

A custom card (`custom:sun-bathing-card`) shows all 7 windows at a glance,
with tabs for Today / Tomorrow / Day+2, color-coded scores (red/amber/green),
and per-factor icons that switch based on whether that factor is above or
below its threshold.

### Setup

1. **Settings → Dashboards → ⋮ → Resources → Add Resource**
   - URL: `/sun_bathing/sun-bathing-card.js`
   - Resource type: **JavaScript Module**
2. Edit any dashboard → **+ Add Card → Manual**, and paste:
   ```yaml
   type: custom:sun-bathing-card
   ```

If the card doesn't appear after adding the resource, try a hard refresh
(`Ctrl+Shift+R` / `Cmd+Shift+R`) — Home Assistant caches `/local/` resources
aggressively.

## Notifications

`sun_bathing` doesn't send notifications itself — everyone's notification
setup differs too much (device, timing, level of detail) to bake into the
integration. Instead, a ready-made **Blueprint** handles this with a few
clicks.

### Import

1. **Settings → Automations & Scenes → Blueprints tab → Import Blueprint**
2. Paste: `https://github.com/dyslexicdogo/sun_bathing/blob/main/blueprints/automation/sun_bathing/morning_notification.yaml`
3. **Preview → Import Blueprint**
4. **Automations tab → Create Automation →** select "Sunbathing Morning Notification"
5. Configure:
   - **Sunbathing Window Sensors** — select all 7
   - **Notify Service** — e.g. `notify.mobile_app_your_phone`
   - **Notification Time** — default 8:00 AM
   - **Minimum Score to Notify** — default 40 (skip notifying on days where even the best window isn't great)
6. Save

Each day's notification replaces the previous one on your phone rather than
piling up.

## Roadmap

- [ ] Options flow — edit thresholds without re-adding the integration
- [ ] Additional forecast days beyond Day+2

## Development

Built incrementally as a learning project — see
[`sun_bathing_project_summary.md`](./sun_bathing_project_summary.md) for the
full architecture notes, design decisions, and phase-by-phase build log.

Tests: `pytest tests/ -v`

## License

MIT — see [LICENSE](./LICENSE).