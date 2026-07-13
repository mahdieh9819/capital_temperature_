#!/usr/bin/env python3
"""Print a capital's temperature plus country oil and gas reserve figures."""

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
    parser = argparse.ArgumentParser(description="Get a capital temperature and country oil/gas reserves.")
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

    print(f"{capital}, capital of {country.title()}: {temperature:.1f} degrees C (observed {observed_at} local time)")
    print(format_reserves(country))


# ---------------------------------------------------------------------------
# Oil and gas reserves output (added after the original temperature code)
# ---------------------------------------------------------------------------
# These datasets contain country-level *proved reserves*, rather than an
# estimate of all undiscovered resources. Values are downloaded at runtime.
import csv
from io import StringIO

OIL_RESERVES_URL = "https://ourworldindata.org/grapher/oil-proved-reserves.csv?v=1&csvType=full&useColumnShortNames=false"
GAS_RESERVES_URL = "https://ourworldindata.org/grapher/natural-gas-proved-reserves.csv?v=1&csvType=full&useColumnShortNames=false"

RESOURCE_COUNTRY_NAMES = {
    "uk": "United Kingdom", "usa": "United States",
    "united states of america": "United States",
}


def get_csv(url: str) -> list[dict[str, str]]:
    """Download an OWID CSV dataset without external Python packages."""
    request = Request(url, headers={"User-Agent": "capital-temperature-model/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            return list(csv.DictReader(StringIO(response.read().decode("utf-8"))))
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError("Could not contact the oil and gas data service.") from error


def latest_reserve(rows: list[dict[str, str]], country: str) -> tuple[float, int] | None:
    """Find a country's newest non-empty reserve value in an OWID CSV."""
    country_rows = [row for row in rows if row["Entity"].casefold() == country.casefold()]
    if not country_rows:
        return None
    value_column = next(name for name in country_rows[0] if name not in {"Entity", "Code", "Year"})
    valid_rows = [row for row in country_rows if row.get(value_column)]
    if not valid_rows:
        return None
    latest = max(valid_rows, key=lambda row: int(row["Year"]))
    return float(latest[value_column]), int(latest["Year"])


def format_reserves(country: str) -> str:
    """Return latest available oil and natural-gas proved reserve figures."""
    dataset_country = RESOURCE_COUNTRY_NAMES.get(country.strip().casefold(), country.strip())
    try:
        oil = latest_reserve(get_csv(OIL_RESERVES_URL), dataset_country)
        gas = latest_reserve(get_csv(GAS_RESERVES_URL), dataset_country)
    except RuntimeError as error:
        return f"Oil and gas proved reserves: unavailable ({error})"

    def display(record: tuple[float, int] | None, unit: str) -> str:
        if record is None:
            return "no country value available"
        value, year = record
        return f"{value:,.0f} {unit} ({year})"

    return (
        "Proved reserves (latest available data):\n"
        f"  Oil: {display(oil, 'tonnes')}\n"
        f"  Natural gas: {display(gas, 'cubic metres')}"
    )


if __name__ == "__main__":
    main()
