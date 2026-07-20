class SunBathingCard extends HTMLElement {
  constructor() {
    super();
    this._activeDayOffset = 0;
  }

  setConfig(config) {
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _fieldScore(value, threshold, range, higherIsBetter) {
    const raw = higherIsBetter ? (value - threshold) / range : (threshold - value) / range;
    return Math.max(0, Math.min(100, 50 + 50 * raw));
  }

  _colorFor(score) {
    if (score < 40) return { text: "#ff5252", bg: "rgba(255,82,82,0.15)", fill: "#ff5252" };
    if (score < 70) return { text: "#ffb300", bg: "rgba(255,179,0,0.15)", fill: "#ffb300" };
    return { text: "#66bb6a", bg: "rgba(102,187,106,0.15)", fill: "#66bb6a" };
  }

  _to12h(hour) {
    const period = hour < 12 ? "am" : "pm";
    let h12 = hour % 12;
    if (h12 === 0) h12 = 12;
    return `${h12}${period}`;
  }

  _setDayOffset(offset) {
    this._activeDayOffset = offset;
    this._render();
  }

  _render() {
    if (!this._hass || !this._config) return;
    const windows = this._config.windows || [
      [10, 11], [11, 12], [12, 13], [13, 14], [14, 15], [15, 16], [16, 17],
    ];

    const dayLabels = ["Today", "Tomorrow", "Day+2"];
    const activeOffset = this._activeDayOffset;

    const tabsHtml = dayLabels
      .map((label, offset) => {
        const isActive = offset === activeOffset;
        const style = isActive
          ? "background:var(--primary-color);color:var(--text-primary-color,#fff)"
          : "background:transparent;color:var(--secondary-text-color)";
        return `<button data-offset="${offset}" style="flex:1;padding:6px 0;border:none;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;${style}">${label}</button>`;
      })
      .join("");

    const rows = windows
      .map(([start, end]) => {
        const id = `sensor.sunbathing_score_${start}_00_${end}_00`;
        const st = this._hass.states[id];
        if (!st) return "";
        const a = st.attributes;
        const forecast = (a.forecast || []).find((f) => f.day_offset === activeOffset);

        const cellStyle =
          "display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:2px";

        if (!forecast || forecast.score === null || forecast.score === undefined) {
          return `
            <div style="${cellStyle}">${this._to12h(start)}-${this._to12h(end)}</div>
            <div style="${cellStyle};grid-column:span 7;color:var(--secondary-text-color);font-size:12px">No data</div>`;
        }

        const score = forecast.score;
        const scoreColor = this._colorFor(score);

        const tempScore = this._fieldScore(forecast.apparent_temperature, a.min_apparent_temp_c, a.apparent_temp_range, true);
        const cloudScore = this._fieldScore(forecast.cloud_cover, a.max_cloud_pct, a.cloud_range, false);
        const radScore = this._fieldScore(forecast.direct_radiation, a.min_direct_radiation, a.radiation_range, true);
        const windScore = this._fieldScore(forecast.wind_speed, a.max_wind_speed_kmh, a.wind_speed_range, false);
        const gustScore = this._fieldScore(forecast.wind_gusts, a.max_wind_gust_kmh, a.wind_gust_range, false);
        const uvScore = this._fieldScore(forecast.uv_index, a.min_uv_index, a.uv_range, true);

        const tempIcon = tempScore >= 50 ? "mdi:thermometer" : "mdi:snowflake";
        const cloudIcon = cloudScore >= 50 ? "mdi:weather-sunny" : "mdi:cloud";
        const radIcon = radScore < 40 ? "mdi:weather-cloudy" : radScore < 70 ? "mdi:white-balance-sunny" : "mdi:weather-sunny";
        const windIcon = windScore >= 70 ? "mdi:weather-windy-variant" : "mdi:weather-windy";
        const gustIcon = gustScore >= 70 ? "mdi:weather-windy-variant" : "mdi:weather-windy";

        const cell = (icon, cellScore, value) => `
          <div style="${cellStyle}">
            <ha-icon icon="${icon}" style="color:${this._colorFor(cellScore).text};--mdc-icon-size:18px"></ha-icon>
            <div style="font-size:11px;color:var(--secondary-text-color)">${value}</div>
          </div>`;

        return `
          <div style="${cellStyle}">${this._to12h(start)}-${this._to12h(end)}</div>
          <div style="${cellStyle}">
            <span style="background:${scoreColor.bg};color:${scoreColor.text};padding:3px 10px;border-radius:12px;font-weight:600">${score}</span>
          </div>
          ${cell(tempIcon, tempScore, forecast.apparent_temperature + "°C")}
          ${cell(cloudIcon, cloudScore, forecast.cloud_cover + "%")}
          ${cell(radIcon, radScore, forecast.direct_radiation + "W")}
          ${cell(windIcon, windScore, forecast.wind_speed + "km/h")}
          ${cell(gustIcon, gustScore, forecast.wind_gusts + "km/h")}
          <div style="${cellStyle}">
            <div style="width:12px;height:12px;border-radius:50%;background:${this._colorFor(uvScore).fill}"></div>
            <div style="font-size:11px;color:var(--secondary-text-color)">${forecast.uv_index}</div>
          </div>`;
      })
      .join("");

    const headerCellStyle = "text-align:center;color:var(--secondary-text-color);font-weight:500;font-size:12px";

    this.innerHTML = `
      <ha-card style="padding:12px 16px">
        <div style="display:flex;gap:6px;margin-bottom:12px">${tabsHtml}</div>
        <div style="display:grid;grid-template-columns:72px 56px repeat(6,1fr);gap:8px 8px;font-size:13px;align-items:stretch">
          <div style="${headerCellStyle}">Window</div>
          <div style="${headerCellStyle}">Score</div>
          <div style="${headerCellStyle}">Temp</div>
          <div style="${headerCellStyle}">Cloud</div>
          <div style="${headerCellStyle}">Radiation</div>
          <div style="${headerCellStyle}">Wind</div>
          <div style="${headerCellStyle}">Gust</div>
          <div style="${headerCellStyle}">UV</div>
          ${rows}
        </div>
      </ha-card>`;

    this.querySelectorAll("button[data-offset]").forEach((btn) => {
      btn.addEventListener("click", () => this._setDayOffset(Number(btn.dataset.offset)));
    });
  }

  getCardSize() {
    return 4;
  }
}
customElements.define("sun-bathing-card", SunBathingCard);