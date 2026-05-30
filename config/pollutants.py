from __future__ import annotations

POLLUTANT_CATALOG = [
    {
        "code": "pm2_5",
        "name": "PM2.5",
        "family": "pm",
        "unit": "ug_m3",
        "source_names": ["pm2_5", "pm25", "pm2_5_mass_concentration"],
        "primary": True,
    },
    {
        "code": "pm10",
        "name": "PM10",
        "family": "pm",
        "unit": "ug_m3",
        "source_names": ["pm10"],
        "primary": True,
    },
    {
        "code": "no2",
        "name": "NO2",
        "family": "gas",
        "unit": "ug_m3",
        "source_names": ["no2", "nitrogen_dioxide"],
        "primary": True,
    },
    {
        "code": "o3",
        "name": "O3",
        "family": "gas",
        "unit": "ug_m3",
        "source_names": ["o3", "ozone"],
        "primary": True,
    },
    {
        "code": "so2",
        "name": "SO2",
        "family": "gas",
        "unit": "ug_m3",
        "source_names": ["so2", "sulphur_dioxide"],
        "primary": True,
    },
    {
        "code": "co",
        "name": "CO",
        "family": "gas",
        "unit": "ug_m3",
        "source_names": ["co", "carbon_monoxide"],
        "primary": True,
    },
    {
        "code": "nh3",
        "name": "NH3",
        "family": "gas",
        "unit": "ug_m3",
        "source_names": ["nh3", "ammonia"],
        "primary": False,
    },
]

POLLUTANT_LOOKUP = {item["code"]: item for item in POLLUTANT_CATALOG}
SOURCE_NAME_LOOKUP = {
    source_name: item["code"]
    for item in POLLUTANT_CATALOG
    for source_name in item["source_names"]
}
