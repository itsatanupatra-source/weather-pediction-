# ⛅ Weather Forecasting System

A complete, production-ready weather forecasting application built in Python using the free [Open-Meteo](https://open-meteo.com) Meteorological API (**no API key required**).

The system retrieves real-time weather and forecast projections specifically centered on the 5 core meteorological parameters:
1. 🌡️ **Temperature** (°C / °F)
2. 💧 **Humidity** (%)
3. 💨 **Wind Speed** (km/h / mph / m/s)
4. ⏲️ **Pressure** (hPa / inHg)
5. 🌧️ **Rainfall** (mm)

---

## 🚀 Features

- **No API Key Required**: Works right out of the box with zero configuration or registration.
- **5 Core Parameters**: Always extracts and standardizes temperature, humidity, windspeed, pressure, and rainfall.
- **Multiple Interfaces**:
  - **Interactive Streamlit Web Dashboard**: Visual analytics, KPI cards, interactive Plotly time-series charts, and multi-day outlook tables.
  - **Terminal CLI Tool**: Formatted Rich tables, colored metrics, hourly forecast views, and clean JSON output mode.
  - **Modular Python Library**: Simple `get_weather_forecast("City")` function or full-featured `WeatherClient` for custom integration.
- **Multi-day & Hourly Forecasts**: Next 24–48 hours trend analysis and up to 14-day daily projections.
- **Global Geocoding**: Search for any city worldwide with automatic coordinate resolution.
- **Unit Conversion**: Seamless toggling between **Metric** (°C, km/h, hPa) and **Imperial** (°F, mph, inHg).

---

## 📁 Project Structure

```text
weather/
├── main.py              # Interactive entrypoint: select from all Indian cities or type any city
├── weather/
│   ├── __init__.py      # Package exports
│   ├── client.py        # WeatherClient & get_weather_forecast API wrapper
│   ├── india_cities.py  # Comprehensive database of Indian cities across all 28 States & 8 UTs
│   ├── models.py        # Typed dataclass models for current & forecast data
│   └── utils.py         # WMO weather code mapping and unit conversions
├── app.py               # Interactive Streamlit Web Dashboard (with State/City dropdowns)
├── cli.py               # Command Line Interface (CLI)
├── tests/
│   └── test_weather.py  # Unit and integration test suite (14 tests)
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## ⚡ Quick Run (Interactive Indian Cities Selector)

Simply run:
```bash
python main.py
```
You will be greeted with the Indian Cities Selector:
```text
======================================================
   🇮🇳 WEATHER FORECASTING - INDIAN CITIES SELECTOR
======================================================
  [1] Type any City name (Direct Input)
  [2] Select from Top 20 Indian Cities (Mumbai, Delhi, etc.)
  [3] Browse Indian Cities by State / Union Territory
  [4] Search Indian Cities with Smart Autocomplete
  [5] Exit
======================================================
```

### Options:
- **Option 1**: Type any Indian city (e.g., `Pune`, `Varanasi`, `Nagpur`) or world city.
- **Option 2**: Pick directly by number from India's top 20 metros (Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad, etc.).
- **Option 3**: Browse cities across **all 28 States and 8 Union Territories** (Maharashtra, Karnataka, Tamil Nadu, Uttar Pradesh, Gujarat, Delhi NCR, etc.).
- **Option 4**: Search with smart autocomplete (e.g. typing `jai` matches `Jaipur`, `Jaisalmer`, etc.).

### Example Weather Output:
```text
======================================================
  🌦️ Actual Weather for: Bengaluru, India
  Status: Light drizzle | Observed: 2026-09-12T13:00
======================================================
  🌡️  Temperature : 30.2 °C
  💧  Humidity    : 44.0 %
  💨  Wind Speed  : 9.4 km/h
  ⏲️   Pressure    : 910.8 hPa
  🌧️  Rainfall    : 0.1 mm
======================================================
```

---

## 🛠️ Installation

1. Ensure Python 3.9+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Advanced CLI Usage

### 1. Basic Weather Query (Default: London)
```bash
python cli.py
```

### 2. Search for Any City
```bash
python cli.py --city "Paris"
# or
python cli.py "Tokyo"
```

### 3. Display 7-Day Forecast & 24-Hour Hourly Breakdown
```bash
python cli.py --city "New York" --forecast --hourly
```

### 4. Imperial Units (°F, mph, inHg)
```bash
python cli.py --city "San Francisco" --units imperial
```

### 5. JSON Output Mode (Ideal for Scripting & APIs)
```bash
python cli.py --city "Tokyo" --json
```
**Example JSON Output:**
```json
{
  "location": "Tokyo, Japan",
  "coordinates": {
    "latitude": 35.6895,
    "longitude": 139.69171
  },
  "parameters": {
    "temperature": {
      "value": 25.1,
      "unit": "°C"
    },
    "humidity": {
      "value": 75.0,
      "unit": "%"
    },
    "windspeed": {
      "value": 2.8,
      "unit": "km/h"
    },
    "pressure": {
      "value": 1016.7,
      "unit": "hPa"
    },
    "rainfall": {
      "value": 0.0,
      "unit": "mm"
    }
  },
  "condition": "Partly cloudy",
  "timestamp": "2026-09-12T16:30"
}
```

---

## 🌐 Interactive Web Dashboard

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```

### Dashboard Highlights:
- **City Search & Quick Select**: Search any city or pick from presets.
- **KPI Cards**: Prominently displays the 5 target parameters with comfort indicators.
- **Interactive Plotly Visualizations**:
  - Temperature & humidity dual-axis progression.
  - Precipitation / rainfall volume bar charts.
  - Wind speed and atmospheric pressure curves.
- **Multi-Day Table**: Min/max temperatures, rain totals, and weather condition badges.
- **Live JSON Viewer**: Inspect raw structured parameters in real-time.

---

## 🐍 Python Library Usage

You can import and use the weather module directly in your own Python projects:

```python
from weather import get_weather_forecast, WeatherClient

# Quick 1-liner to get the 5 core parameters
data = get_weather_forecast("Berlin")
print("Temperature:", data["parameters"]["temperature"])
print("Humidity:   ", data["parameters"]["humidity"])
print("Wind Speed: ", data["parameters"]["windspeed"])
print("Pressure:   ", data["parameters"]["pressure"])
print("Rainfall:   ", data["parameters"]["rainfall"])

# Or use the object-oriented WeatherClient
client = WeatherClient()
report = client.get_weather("London", forecast_days=7)

print(f"Location: {report.location}")
print(f"Temp: {report.current.temperature}°C ({report.current.temperature_f}°F)")
print(f"Humidity: {report.current.humidity}%")
print(f"Wind Speed: {report.current.wind_speed} km/h")
print(f"Pressure: {report.current.pressure} hPa")
print(f"Rainfall: {report.current.rainfall} mm")
```

---

## 🧪 Running Tests

Run the full unit and integration test suite:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
All 10 tests verify data models, conversions, response parsing, and live endpoint responses.
