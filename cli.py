#!/usr/bin/env python3
"""
Command-line interface for the Weather Forecasting System.
Returns key parameters: Temperature, Humidity, Wind Speed, Pressure, and Rainfall.
"""

import argparse
import json
import sys

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from weather.client import WeatherClient, LocationNotFoundError, WeatherAPIError
from weather.utils import get_weather_description

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def print_weather_rich(report, units: str, show_forecast: bool = False, show_hourly: bool = False):
    console = Console(legacy_windows=False, highlight=False)
    cur = report.current
    params = cur.to_dict(units=units)
    _, icon = get_weather_description(cur.weather_code)

    # Header Panel
    title = f"{icon} Weather Forecast for [bold cyan]{report.location}[/bold cyan]"
    subtitle = f"Observation Time: {cur.timestamp} | Status: [bold green]{cur.condition}[/bold green]"
    
    # 5 Parameters Table
    table = Table(
        title="Current Meteorological Parameters",
        title_style="bold magenta",
        box=box.ROUNDED,
        header_style="bold blue",
        show_lines=True
    )
    table.add_column("Parameter", style="cyan", width=20)
    table.add_column("Value", justify="right", style="bold yellow", width=15)
    table.add_column("Unit", justify="left", style="white", width=12)
    table.add_column("Description", style="dim", width=25)

    table.add_row(
        "🌡️ Temperature",
        str(params["temperature"]["value"]),
        params["temperature"]["unit"],
        "Ambient air temperature"
    )
    table.add_row(
        "💧 Humidity",
        str(params["humidity"]["value"]),
        params["humidity"]["unit"],
        "Relative air humidity"
    )
    table.add_row(
        "💨 Wind Speed",
        str(params["windspeed"]["value"]),
        params["windspeed"]["unit"],
        "10-meter surface wind"
    )
    table.add_row(
        "⏲️ Pressure",
        str(params["pressure"]["value"]),
        params["pressure"]["unit"],
        "Atmospheric surface pressure"
    )
    table.add_row(
        "🌧️ Rainfall",
        str(params["rainfall"]["value"]),
        params["rainfall"]["unit"],
        "Current precipitation"
    )

    console.print()
    console.print(Panel(table, title=title, subtitle=subtitle, expand=False))

    # Daily forecast table if requested
    if show_forecast and report.daily:
        forecast_table = Table(
            title="📅 7-Day Forecast",
            title_style="bold cyan",
            box=box.SIMPLE_HEAD,
            header_style="bold blue"
        )
        forecast_table.add_column("Date", style="white")
        forecast_table.add_column("Condition", style="yellow")
        temp_unit = "°F" if units == "imperial" else "°C"
        wind_unit = "mph" if units == "imperial" else "km/h"
        forecast_table.add_column(f"Min / Max Temp ({temp_unit})", justify="center")
        forecast_table.add_column(f"Max Wind ({wind_unit})", justify="right")
        forecast_table.add_column("Rain Total (mm)", justify="right", style="blue")

        for d in report.daily:
            _, d_icon = get_weather_description(d.weather_code)
            min_t = (d.temp_min * 9/5 + 32) if units == "imperial" else d.temp_min
            max_t = (d.temp_max * 9/5 + 32) if units == "imperial" else d.temp_max
            w_spd = (d.wind_speed_max * 0.621371) if units == "imperial" else d.wind_speed_max

            forecast_table.add_row(
                d.date,
                f"{d_icon} {d.condition}",
                f"{min_t:.1f}° / {max_t:.1f}°",
                f"{w_spd:.1f}",
                f"{d.rainfall_sum:.1f}"
            )
        console.print()
        console.print(forecast_table)

    # Next 24 Hours hourly forecast if requested
    if show_hourly and report.hourly:
        hourly_table = Table(
            title="⏱️ Next 24 Hours Forecast",
            title_style="bold green",
            box=box.SIMPLE_HEAD,
            header_style="bold blue"
        )
        hourly_table.add_column("Time", style="white")
        hourly_table.add_column("Condition", style="yellow")
        temp_unit = "°F" if units == "imperial" else "°C"
        wind_unit = "mph" if units == "imperial" else "km/h"
        hourly_table.add_column(f"Temp ({temp_unit})", justify="right")
        hourly_table.add_column("Humidity (%)", justify="right")
        hourly_table.add_column(f"Wind ({wind_unit})", justify="right")
        hourly_table.add_column("Pressure (hPa)", justify="right")
        hourly_table.add_column("Rain (mm)", justify="right", style="blue")

        for h in report.hourly[:24]:
            _, h_icon = get_weather_description(h.weather_code)
            h_temp = (h.temperature * 9/5 + 32) if units == "imperial" else h.temperature
            h_wind = (h.wind_speed * 0.621371) if units == "imperial" else h.wind_speed
            time_part = h.time.split("T")[-1] if "T" in h.time else h.time

            hourly_table.add_row(
                time_part,
                f"{h_icon} {h.condition}",
                f"{h_temp:.1f}",
                f"{h.humidity:.0f}%",
                f"{h_wind:.1f}",
                f"{h.pressure:.0f}",
                f"{h.rainfall:.1f}"
            )
        console.print()
        console.print(hourly_table)

    console.print()


def print_weather_plain(report, units: str, show_forecast: bool = False):
    cur = report.current
    params = cur.to_dict(units=units)
    print("=" * 60)
    print(f"WEATHER FORECAST FOR: {report.location}")
    print(f"Condition: {cur.condition} | Time: {cur.timestamp}")
    print("=" * 60)
    print(f"  [1] Temperature:  {params['temperature']['value']} {params['temperature']['unit']}")
    print(f"  [2] Humidity:     {params['humidity']['value']} {params['humidity']['unit']}")
    print(f"  [3] Wind Speed:   {params['windspeed']['value']} {params['windspeed']['unit']}")
    print(f"  [4] Pressure:     {params['pressure']['value']} {params['pressure']['unit']}")
    print(f"  [5] Rainfall:     {params['rainfall']['value']} {params['rainfall']['unit']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch weather forecasts including Temperature, Humidity, Wind Speed, Pressure, and Rainfall."
    )
    parser.add_argument(
        "city",
        nargs="?",
        default=None,
        help="City name to fetch weather for"
    )
    parser.add_argument(
        "-c", "--city-name",
        dest="city_opt",
        help="Alternative flag to specify city name"
    )
    parser.add_argument(
        "-u", "--units",
        choices=["metric", "imperial"],
        default="metric",
        help="Unit system ('metric' [°C, km/h, hPa] or 'imperial' [°F, mph, inHg])"
    )
    parser.add_argument(
        "-f", "--forecast",
        action="store_true",
        help="Show 7-day daily forecast summary"
    )
    parser.add_argument(
        "--hourly",
        action="store_true",
        help="Show next 24 hours forecast"
    )
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output the 5 parameters in JSON format"
    )

    args = parser.parse_args()
    target_city = args.city_opt or args.city
    if not target_city:
        try:
            target_city = input("Enter city name: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(0)

    if not target_city:
        print("Error: City name cannot be empty.", file=sys.stderr)
        sys.exit(1)

    client = WeatherClient()

    try:
        report = client.get_weather(city_name=target_city)
    except LocationNotFoundError as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except WeatherAPIError as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"API Error: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        output_data = report.get_summary_parameters(units=args.units)
        print(json.dumps(output_data, indent=2))
        return

    if RICH_AVAILABLE:
        print_weather_rich(report, units=args.units, show_forecast=args.forecast, show_hourly=args.hourly)
    else:
        print_weather_plain(report, units=args.units, show_forecast=args.forecast)


if __name__ == "__main__":
    main()
