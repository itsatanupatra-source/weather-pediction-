#!/usr/bin/env python3
"""
Weather Forecasting System - India & Worldwide City Selector.
Takes input as city name or allows selecting from all Indian cities across
all 28 States and 8 Union Territories.

Returns the 5 actual weather parameters:
- Temperature
- Humidity
- Wind Speed
- Pressure
- Rainfall
"""

import sys

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from weather.client import WeatherClient, LocationNotFoundError, WeatherAPIError
from weather.utils import get_weather_description
from weather.india_cities import (
    INDIAN_CITIES_BY_STATE,
    TOP_INDIAN_CITIES,
    get_all_states,
    get_cities_by_state,
    search_indian_cities
)


def display_weather(city_name: str, prefer_india: bool = True):
    """Fetches and displays the 5 actual meteorological parameters."""
    client = WeatherClient()
    try:
        prefer = "India" if prefer_india else None
        report = client.get_weather(city_name=city_name, prefer_country=prefer)
    except LocationNotFoundError:
        print(f"\n❌ Error: Could not find any city matching '{city_name}'. Please check spelling.\n")
        return
    except WeatherAPIError as err:
        print(f"\n⚠️ API Error: {err}\n")
        return
    except Exception as err:
        print(f"\n⚠️ Unexpected error: {err}\n")
        return

    cur = report.current
    params = cur.to_dict(units="metric")
    _, icon = get_weather_description(cur.weather_code)

    print("\n" + "=" * 54)
    print(f"  {icon} Actual Weather for: {report.location}")
    print(f"  Status: {cur.condition} | Observed: {cur.timestamp}")
    print("=" * 54)
    print(f"  🌡️  Temperature : {params['temperature']['value']} {params['temperature']['unit']}")
    print(f"  💧  Humidity    : {params['humidity']['value']} {params['humidity']['unit']}")
    print(f"  💨  Wind Speed  : {params['windspeed']['value']} {params['windspeed']['unit']}")
    print(f"  ⏲️   Pressure    : {params['pressure']['value']} {params['pressure']['unit']}")
    print(f"  🌧️  Rainfall    : {params['rainfall']['value']} {params['rainfall']['unit']}")
    print("=" * 54 + "\n")


def select_by_top_indian_cities():
    """Select from top 20 major Indian metro and hub cities."""
    print("\n--- 🇮🇳 TOP INDIAN CITIES ---")
    for idx, city in enumerate(TOP_INDIAN_CITIES, start=1):
        print(f"  [{idx:2d}] {city}")
    print("  [ 0] Back to Main Menu")

    choice = input("\nSelect city number (1-20): ").strip()
    if not choice or choice == "0":
        return

    try:
        num = int(choice)
        if 1 <= num <= len(TOP_INDIAN_CITIES):
            selected_city = TOP_INDIAN_CITIES[num - 1]
            display_weather(selected_city, prefer_india=True)
        else:
            print("Invalid number.")
    except ValueError:
        print("Please enter a valid number.")


def select_by_state():
    """Browse Indian cities by State or Union Territory."""
    states = get_all_states()
    print("\n--- 🇮🇳 INDIAN STATES & UNION TERRITORIES ---")
    for idx, state in enumerate(states, start=1):
        print(f"  [{idx:2d}] {state}")
    print("  [ 0] Back to Main Menu")

    choice = input(f"\nSelect State / UT number (1-{len(states)}): ").strip()
    if not choice or choice == "0":
        return

    try:
        num = int(choice)
        if 1 <= num <= len(states):
            chosen_state = states[num - 1]
            cities = get_cities_by_state(chosen_state)
            print(f"\n--- Cities in {chosen_state} ---")
            for c_idx, c_name in enumerate(cities, start=1):
                print(f"  [{c_idx:2d}] {c_name}")
            print("  [ 0] Back")

            c_choice = input(f"\nSelect city number (1-{len(cities)}): ").strip()
            if not c_choice or c_choice == "0":
                return
            c_num = int(c_choice)
            if 1 <= c_num <= len(cities):
                selected_city = cities[c_num - 1]
                display_weather(f"{selected_city}, {chosen_state}", prefer_india=True)
            else:
                print("Invalid city number.")
        else:
            print("Invalid state number.")
    except ValueError:
        print("Please enter a valid number.")


def search_indian_city_by_name():
    """Search for any Indian city by typing all or part of its name."""
    query = input("\nEnter Indian city name to search: ").strip()
    if not query:
        return

    matches = search_indian_cities(query, limit=10)
    if matches:
        print(f"\nFound {len(matches)} matching Indian cities:")
        for idx, m in enumerate(matches, start=1):
            print(f"  [{idx}] {m['city']}, {m['state']}")
        print(f"  [{len(matches) + 1}] Query '{query}' directly via Weather API")

        sel = input(f"\nSelect option (1-{len(matches) + 1}) [default 1]: ").strip()
        if not sel:
            sel = "1"
        try:
            sel_num = int(sel)
            if 1 <= sel_num <= len(matches):
                chosen = matches[sel_num - 1]["city"]
                display_weather(chosen, prefer_india=True)
                return
            elif sel_num == len(matches) + 1:
                display_weather(query, prefer_india=True)
                return
        except ValueError:
            pass

    display_weather(query, prefer_india=True)


def main():
    # If city is passed as a command line argument, immediately show its weather
    if len(sys.argv) > 1:
        city = " ".join(sys.argv[1:]).strip()
        display_weather(city, prefer_india=True)
        return

    while True:
        print("=" * 54)
        print("   🇮🇳 WEATHER FORECASTING - INDIAN CITIES SELECTOR")
        print("=" * 54)
        print("  [1] Type any City name (Direct Input)")
        print("  [2] Select from Top 20 Indian Cities (Mumbai, Delhi, etc.)")
        print("  [3] Browse Indian Cities by State / Union Territory")
        print("  [4] Search Indian Cities with Smart Autocomplete")
        print("  [5] Exit")
        print("=" * 54)

        try:
            choice = input("Enter option (1-5) or type city name directly: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if not choice:
            continue

        if choice == "1":
            try:
                city = input("\nEnter city name: ").strip()
                if city:
                    display_weather(city, prefer_india=True)
            except (KeyboardInterrupt, EOFError):
                break
        elif choice == "2":
            select_by_top_indian_cities()
        elif choice == "3":
            select_by_state()
        elif choice == "4":
            search_indian_city_by_name()
        elif choice in ["5", "exit", "quit", "q"]:
            print("Goodbye!")
            break
        else:
            # If user directly typed a city name like "Bengaluru" or "Chennai"
            display_weather(choice, prefer_india=True)


if __name__ == "__main__":
    main()