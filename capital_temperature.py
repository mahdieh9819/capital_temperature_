#!/usr/bin/env python3
"""Print the current temperature for a country's capital city.

Uses the free Open-Meteo geocoding and weather APIs. No API key or third-party
Python packages are required.
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# A compact built-in lookup keeps the program useful without a country API.
CAPITALS = {
    "afghanistan": "Kabul", "argentina": "Buenos Aires", "australia": "Canberra",
    "brazil": "Brasilia", "canada": "Ottawa", "china": "Beijing",
    "egypt": "Cairo", "france": "Paris", "germany": "Berlin", "india": "New Delhi",
    "indonesia": "Jakarta", "iran": "Tehran", "iraq": "Baghdad", "italy": "Rome",
    "japan": "Tokyo", "mexico": "Mexico City", "netherlands": "Amsterdam",
    "pakistan": "Islamabad", "russia": "Moscow", "saudi arabia": "Riyadh",
    "south africa": "Pretoria", "south korea": "Seoul", "spain": "Madrid",
    "sweden": "Stockholm", "turkey": "Ankara", "uk": "London",
    "united kingdom": "London", "usa": "Washington, D.C.",
    "united states": "Washington, D.C.", "united states of america": "Washington, D.C.",
}


def get_json(url: str, params: dict[str, str]) -> dict:
    request = Request(f"{url}?{urlencode(params)}", headers={"User-Agent": "capital-temperature-model/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError("Could not contact the weather service. Check your internet connection and try again.") from error


def find_capital(country: str) -> str:
    """Return a capital from the built-in list, or ask REST Countries."""
    normalized = country.strip().casefold()
    if normalized in CAPITALS:
        return CAPITALS[normalized]

    try:
        data = get_json(f"https://restcountries.com/v3.1/name/{country}", {"fullText": "true", "fields": "capital,name"})
        return data[0]["capital"][0]
    except (RuntimeError, KeyError, IndexError, TypeError):
        raise ValueError(f"I could not find a capital for '{country}'. Try a full country name.")


def current_temperature(city: str) -> tuple[float, str]:
    places = get_json("https://geocoding-api.open-meteo.com/v1/search", {"name": city, "count": "1", "language": "en", "format": "json"})
    if not places.get("results"):
        raise ValueError(f"I could not locate {city}.")
    place = places["results"][0]
    weather = get_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": str(place["latitude"]), "longitude": str(place["longitude"]),
        "current": "temperature_2m", "temperature_unit": "celsius",
    })
    current = weather["current"]
    return current["temperature_2m"], current["time"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Get the current temperature in a country's capital.")
    parser.add_argument("country", nargs="?", help="Country name, for example: Iran")
    args = parser.parse_args()
    country = args.country or input("Country: ").strip()
    if not country:
        parser.error("Please provide a country name.")

    try:
        capital = find_capital(country)
        temperature, observed_at = current_temperature(capital)
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    print(f"{capital}, capital of {country.title()}: {temperature:.1f} °C (observed {observed_at} local time)")


if __name__ == "__main__":
    main()
