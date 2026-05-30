from __future__ import annotations

import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st

from config.cities import get_city_location
from providers.base import ProviderResponse

OPENWEATHER_AIR_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


@st.cache_data(ttl=900, show_spinner=False)
def fetch_current_air_quality(city_key: str) -> ProviderResponse:
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        return ProviderResponse(
            data=None,
            raw_payload=None,
            metadata={"source_system": "openweather", "available": False},
            warnings=["OPENWEATHER_API_KEY no está configurada"],
            is_partial=True,
        )

    location = get_city_location(city_key)
    params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "appid": api_key,
    }
    request = Request(f"{OPENWEATHER_AIR_POLLUTION_URL}?{urlencode(params)}", headers={"User-Agent": "EcoCities/1.0"})
    with urlopen(request, timeout=20) as response:
        payload = response.read().decode("utf-8")

    return ProviderResponse(
        data=payload,
        raw_payload=payload,
        metadata={"source_system": "openweather", "available": True},
        warnings=[],
        is_partial=False,
    )
