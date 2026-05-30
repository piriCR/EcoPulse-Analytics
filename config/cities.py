from __future__ import annotations

CITY_CATALOG = {
    "Costa Rica": {
        "city_name": "San José",
        "country_code": "CR",
        "region_name": "San José",
        "latitude": 9.9281,
        "longitude": -84.0907,
        "timezone_name": "America/Costa_Rica",
        "location_scope": "city",
        "source_system": "open_meteo",
    },
    "Lima": {
        "city_name": "Lima",
        "country_code": "PE",
        "region_name": "Lima",
        "latitude": -12.0464,
        "longitude": -77.0428,
        "timezone_name": "America/Lima",
        "location_scope": "city",
        "source_system": "open_meteo",
    },
    "Santiago": {
        "city_name": "Santiago",
        "country_code": "CL",
        "region_name": "Región Metropolitana",
        "latitude": -33.4489,
        "longitude": -70.6693,
        "timezone_name": "America/Santiago",
        "location_scope": "city",
        "source_system": "open_meteo",
    },
    "Ciudad de México": {
        "city_name": "Ciudad de México",
        "country_code": "MX",
        "region_name": "Ciudad de México",
        "latitude": 19.4326,
        "longitude": -99.1332,
        "timezone_name": "America/Mexico_City",
        "location_scope": "city",
        "source_system": "open_meteo",
    },
}


def get_city_location(city_key: str) -> dict:
    return CITY_CATALOG.get(city_key, CITY_CATALOG["Costa Rica"])
