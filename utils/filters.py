from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from config.constants import DEFAULT_CITIES, PRIMARY_POLLUTANTS

FILTER_VERSION = "1.0"


@dataclass(frozen=True)
class FilterDefaults:
    date_from: date
    date_to: date
    country: str
    region: str
    cities: list[str]
    focus_city: str
    primary_pollutant: str
    risk_level: str
    granularity: str
    comparison_mode: str



def get_default_filters() -> dict[str, Any]:
    today = date.today()
    defaults = FilterDefaults(
        date_from=today - timedelta(days=7),
        date_to=today,
        country="",
        region="",
        cities=list(DEFAULT_CITIES[:3]),
        focus_city=DEFAULT_CITIES[0],
        primary_pollutant=PRIMARY_POLLUTANTS[0],
        risk_level="unknown",
        granularity="daily",
        comparison_mode="single",
    )
    return {
        "filters_version": FILTER_VERSION,
        "date_from": defaults.date_from,
        "date_to": defaults.date_to,
        "country": defaults.country,
        "region": defaults.region,
        "cities": defaults.cities,
        "focus_city": defaults.focus_city,
        "primary_pollutant": defaults.primary_pollutant,
        "risk_level": defaults.risk_level,
        "granularity": defaults.granularity,
        "comparison_mode": defaults.comparison_mode,
    }



def normalize_filters(raw_filters: dict[str, Any] | None) -> dict[str, Any]:
    filters = get_default_filters()
    if not raw_filters:
        return filters

    for key, value in raw_filters.items():
        if key not in filters:
            continue
        if key in {"cities"}:
            if isinstance(value, list):
                filters[key] = [item for item in value if item]
            elif value:
                filters[key] = [value]
            continue
        if value is not None and value != "":
            filters[key] = value

    if filters["focus_city"] not in filters["cities"] and filters["cities"]:
        filters["focus_city"] = filters["cities"][0]

    if filters["primary_pollutant"] not in PRIMARY_POLLUTANTS:
        filters["primary_pollutant"] = PRIMARY_POLLUTANTS[0]

    return filters
