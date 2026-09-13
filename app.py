"""
Interactive Weather Forecasting Dashboard
Built with Streamlit & Plotly.
Returns and visualizes:
1. Temperature
2. Humidity
3. Wind Speed
4. Pressure
5. Rainfall
"""

import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from weather.client import WeatherClient, LocationNotFoundError, WeatherAPIError
from weather.utils import get_weather_description

# Page Configuration
st.set_page_config(
    page_title="Weather Forecasting Dashboard",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        text-align: center;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.5);
    }
    .kpi-icon {
        font-size: 2.2rem;
        margin-bottom: 6px;
    }
    .kpi-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .kpi-unit {
        font-size: 1.0rem;
        font-weight: 400;
        color: #38bdf8;
        margin-left: 3px;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 4px;
    }
    .city-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


from weather.india_cities import (
    INDIAN_CITIES_BY_STATE,
    TOP_INDIAN_CITIES,
    get_all_states,
    get_cities_by_state,
    get_all_indian_cities
)

@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather_report(city_name: str, forecast_days: int = 7, prefer_india: bool = True):
    """Cached weather report fetcher."""
    client = WeatherClient()
    prefer = "India" if prefer_india else None
    return client.get_weather(city_name=city_name, forecast_days=forecast_days, prefer_country=prefer)


# --- Sidebar ---
st.sidebar.title("⛅ Weather Explorer")
st.sidebar.markdown("Explore real-time & forecasted atmospheric parameters.")

city_mode = st.sidebar.radio(
    "City Selection Mode",
    options=[
        "🇮🇳 Browse Indian Cities by State",
        "⚡ Top Indian Metros",
        "🔍 Search Any City"
    ],
    index=0
)

prefer_india = True
if city_mode == "🇮🇳 Browse Indian Cities by State":
    all_states = get_all_states()
    default_state_idx = all_states.index("Maharashtra") if "Maharashtra" in all_states else 0
    selected_state = st.sidebar.selectbox("Select Indian State / UT", all_states, index=default_state_idx)
    state_cities = get_cities_by_state(selected_state)
    selected_city_in_state = st.sidebar.selectbox("Select City", state_cities, index=0)
    city_input = f"{selected_city_in_state}, {selected_state}"
elif city_mode == "⚡ Top Indian Metros":
    selected_metro = st.sidebar.selectbox("Select Major Indian City", TOP_INDIAN_CITIES, index=0)
    city_input = selected_metro
else:
    city_input = st.sidebar.text_input("Enter City Name", value="Mumbai")
    prefer_india = st.sidebar.checkbox("Prioritize Indian Cities", value=True)

units = st.sidebar.radio(
    "Unit System",
    options=["Metric (°C, km/h, hPa)", "Imperial (°F, mph, inHg)"],
    index=0
)
is_imperial = "Imperial" in units
temp_unit = "°F" if is_imperial else "°C"
wind_unit = "mph" if is_imperial else "km/h"
press_unit = "inHg" if is_imperial else "hPa"
rain_unit = "mm"

forecast_days = st.sidebar.slider("Forecast Days", min_value=3, max_value=14, value=7)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Target Meteorological Parameters:**
- 🌡️ Temperature
- 💧 Humidity
- 💨 Wind Speed
- ⏲️ Pressure
- 🌧️ Rainfall
""")
st.sidebar.caption("Powered by [Open-Meteo](https://open-meteo.com) API (No API Key Required).")

# --- Main Dashboard ---
if not city_input.strip():
    st.warning("Please enter a valid city name.")
    st.stop()

with st.spinner(f"Fetching meteorological forecast for {city_input}..."):
    try:
        report = fetch_weather_report(city_input.strip(), forecast_days=forecast_days, prefer_india=prefer_india)
    except LocationNotFoundError:
        st.error(f"❌ City '{city_input}' could not be located. Please check the spelling and try again.")
        st.stop()
    except WeatherAPIError as exc:
        st.error(f"⚠️ Weather API Error: {exc}")
        st.stop()
    except Exception as exc:
        st.error(f"⚠️ An unexpected error occurred: {exc}")
        st.stop()

# Header Information
cur = report.current
loc = report.location
_, icon = get_weather_description(cur.weather_code)

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown(f'<div class="city-badge">📍 {loc.latitude:.2f}°N, {loc.longitude:.2f}°E • Timezone: {loc.timezone}</div>', unsafe_allow_html=True)
    st.title(f"{icon} {loc.name}, {loc.country}")
    st.caption(f"Observed at: **{cur.timestamp}** | Current Condition: **{cur.condition}**")

with header_col2:
    st.metric(
        label="Today's Range",
        value=f"{(report.daily[0].temp_max * 9/5 + 32 if is_imperial else report.daily[0].temp_max):.1f}{temp_unit}",
        delta=f"Min: {(report.daily[0].temp_min * 9/5 + 32 if is_imperial else report.daily[0].temp_min):.1f}{temp_unit}",
        delta_color="off"
    )

st.markdown("---")

# 5 Core Parameters Highlight Cards
st.subheader("📊 Core Weather Parameters")

val_temp = cur.temperature_f if is_imperial else cur.temperature
val_humidity = cur.humidity
val_wind = cur.wind_speed_mph if is_imperial else cur.wind_speed
val_pressure = cur.pressure_inhg if is_imperial else cur.pressure
val_rain = cur.rainfall

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🌡️</div>
        <div class="kpi-title">Temperature</div>
        <div class="kpi-value">{val_temp:.1f}<span class="kpi-unit">{temp_unit}</span></div>
        <div class="kpi-sub">Ambient air temp</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    comfort = "Dry" if val_humidity < 35 else ("Comfortable" if val_humidity <= 65 else "Humid")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">💧</div>
        <div class="kpi-title">Humidity</div>
        <div class="kpi-value">{val_humidity:.0f}<span class="kpi-unit">%</span></div>
        <div class="kpi-sub">{comfort} relative humidity</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">💨</div>
        <div class="kpi-title">Wind Speed</div>
        <div class="kpi-value">{val_wind:.1f}<span class="kpi-unit">{wind_unit}</span></div>
        <div class="kpi-sub">10m surface level</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">⏲️</div>
        <div class="kpi-title">Pressure</div>
        <div class="kpi-value">{val_pressure:.1f}<span class="kpi-unit">{press_unit}</span></div>
        <div class="kpi-sub">Atmospheric pressure</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    rain_status = "No rain" if val_rain == 0 else f"{val_rain:.1f} mm/hr"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🌧️</div>
        <div class="kpi-title">Rainfall</div>
        <div class="kpi-value">{val_rain:.1f}<span class="kpi-unit">{rain_unit}</span></div>
        <div class="kpi-sub">{rain_status}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs for Charts, Forecast Table, and API JSON
tab_hourly, tab_daily, tab_json = st.tabs([
    "⏱️ Hourly Forecast (Next 24-48h)",
    "📅 Daily Forecast Table",
    "💻 Parameter JSON API"
])

with tab_hourly:
    st.markdown("#### Hourly Meteorological Dynamics")
    hours_to_plot = min(len(report.hourly), 48)
    h_slice = report.hourly[:hours_to_plot]

    df_hourly = pd.DataFrame([
        {
            "Time": h.time,
            f"Temperature ({temp_unit})": (h.temperature * 9/5 + 32) if is_imperial else h.temperature,
            "Humidity (%)": h.humidity,
            f"Wind Speed ({wind_unit})": (h.wind_speed * 0.621371) if is_imperial else h.wind_speed,
            f"Pressure ({press_unit})": (h.pressure * 0.02953) if is_imperial else h.pressure,
            "Rainfall (mm)": h.rainfall,
            "Condition": h.condition
        }
        for h in h_slice
    ])

    # Temperature & Humidity Line Chart
    fig_temp_hum = go.Figure()
    fig_temp_hum.add_trace(go.Scatter(
        x=df_hourly["Time"],
        y=df_hourly[f"Temperature ({temp_unit})"],
        name=f"Temperature ({temp_unit})",
        line=dict(color="#f97316", width=3),
        mode="lines+markers"
    ))
    fig_temp_hum.add_trace(go.Scatter(
        x=df_hourly["Time"],
        y=df_hourly["Humidity (%)"],
        name="Humidity (%)",
        yaxis="y2",
        line=dict(color="#38bdf8", width=2, dash="dash"),
        mode="lines"
    ))
    fig_temp_hum.update_layout(
        title="Temperature & Relative Humidity Trends",
        xaxis_title="Time",
        yaxis=dict(title=f"Temperature ({temp_unit})", title_font=dict(color="#f97316")),
        yaxis2=dict(title="Humidity (%)", title_font=dict(color="#38bdf8"), overlaying="y", side="right", range=[0, 100]),
        legend=dict(x=0.01, y=0.99),
        template="plotly_dark",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    st.plotly_chart(fig_temp_hum, use_container_width=True)

    # Wind Speed & Rainfall Chart
    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        fig_rain = px.bar(
            df_hourly,
            x="Time",
            y="Rainfall (mm)",
            title="Precipitation / Rainfall Volume (mm)",
            color="Rainfall (mm)",
            color_continuous_scale="Blues",
            template="plotly_dark",
            height=320
        )
        st.plotly_chart(fig_rain, use_container_width=True)

    with c_chart2:
        fig_wind_press = go.Figure()
        fig_wind_press.add_trace(go.Scatter(
            x=df_hourly["Time"],
            y=df_hourly[f"Wind Speed ({wind_unit})"],
            name=f"Wind Speed ({wind_unit})",
            line=dict(color="#10b981", width=2.5),
            mode="lines"
        ))
        fig_wind_press.add_trace(go.Scatter(
            x=df_hourly["Time"],
            y=df_hourly[f"Pressure ({press_unit})"],
            name=f"Pressure ({press_unit})",
            yaxis="y2",
            line=dict(color="#a855f7", width=2, dash="dot"),
            mode="lines"
        ))
        fig_wind_press.update_layout(
            title=f"Wind Speed & Pressure Trends",
            xaxis_title="Time",
            yaxis=dict(title=f"Wind ({wind_unit})", title_font=dict(color="#10b981")),
            yaxis2=dict(title=f"Pressure ({press_unit})", title_font=dict(color="#a855f7"), overlaying="y", side="right"),
            legend=dict(x=0.01, y=0.99),
            template="plotly_dark",
            height=320,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        st.plotly_chart(fig_wind_press, use_container_width=True)

with tab_daily:
    st.markdown("#### 📅 Multi-Day Forecast Outlook")
    daily_rows = []
    for d in report.daily:
        _, d_icon = get_weather_description(d.weather_code)
        min_t = (d.temp_min * 9/5 + 32) if is_imperial else d.temp_min
        max_t = (d.temp_max * 9/5 + 32) if is_imperial else d.temp_max
        w_spd = (d.wind_speed_max * 0.621371) if is_imperial else d.wind_speed_max
        daily_rows.append({
            "Date": d.date,
            "Condition": f"{d_icon} {d.condition}",
            f"Min Temp ({temp_unit})": f"{min_t:.1f}",
            f"Max Temp ({temp_unit})": f"{max_t:.1f}",
            f"Max Wind ({wind_unit})": f"{w_spd:.1f}",
            "Rainfall Sum (mm)": f"{d.rainfall_sum:.1f}"
        })
    st.dataframe(pd.DataFrame(daily_rows), use_container_width=True, hide_index=True)

with tab_json:
    st.markdown("#### Direct JSON Response (5 Target Parameters)")
    st.caption("Standardized response dictionary containing temperature, humidity, windspeed, pressure, and rainfall.")
    unit_mode = "imperial" if is_imperial else "metric"
    params_summary = report.get_summary_parameters(units=unit_mode)
    st.json(params_summary)
