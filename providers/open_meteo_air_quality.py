from __future__ import annotations

from datetime import date, datetime
from typing import Any

import streamlit as st

from config.cities import get_city_location
from config.constants import PRIMARY_POLLUTANTS
from providers.base import ProviderResponse
from providers.http_client import get_json
from providers.normalization import build_current_frame, build_trend_frame, summarize_current_frame

OPEN_METEO_AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def _to_date(value: str | date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return None


def _build_params(city_key: str, start_date: str | date | datetime | None, end_date: str | date | datetime | None) -> dict[str, Any]:
    location = get_city_location(city_key)
    hourly_variables = [
        "european_aqi",
        "pm2_5",
        "pm10",
        "carbon_monoxide",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone",
        "ammonia",
    ]
    params: dict[str, Any] = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": ",".join(hourly_variables),
        "hourly": ",".join(hourly_variables),
        "timezone": location.get("timezone_name", "auto"),
        "timeformat": "iso8601",
        "forecast_days": 7,
        "past_days": 7,
    }
    return params


@st.cache_data(ttl=1200, show_spinner=False)
def fetch_city_snapshot(city_key: str, start_date: str | date | datetime | None = None, end_date: str | date | datetime | None = None) -> ProviderResponse:
    location = get_city_location(city_key)
    payload = get_json(OPEN_METEO_AIR_QUALITY_URL, params=_build_params(city_key, start_date, end_date))

    current_payload = payload.get("current", {}) or {}
    hourly_payload = payload.get("hourly", {}) or {}

    current_frame = build_current_frame(current_payload)
    trend_frame = build_trend_frame(hourly_payload, ["european_aqi", *PRIMARY_POLLUTANTS], start_date=start_date, end_date=end_date)
    summary = summarize_current_frame(current_frame)

    summary.update(
        {
            "city_key": city_key,
            "city_name": location["city_name"],
            "country_code": location["country_code"],
            "region_name": location["region_name"],
        }
    )

    data = {
        "summary": summary,
        "current_frame": current_frame,
        "trend_frame": trend_frame,
        "location": location,
    }

    return ProviderResponse(
        data=data,
        raw_payload=payload,
        metadata={"source_system": "open_meteo", "available": True},
        warnings=[],
        is_partial=False,
    )