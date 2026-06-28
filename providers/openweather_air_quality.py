from __future__ import annotations

import json
import os
import urllib.error
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st

from config.cities import get_city_location
from providers.base import ProviderResponse

OPENWEATHER_AIR_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
OPENWEATHER_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

OW_AQI_TO_RISK = {
    1: "good",
    2: "fair",
    3: "moderate",
    4: "poor",
    5: "very_poor"
}


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
    
    try:
        with urlopen(request, timeout=20) as response:
            payload_str = response.read().decode("utf-8")
            payload = json.loads(payload_str)
            
            # Extract AQI and map it
            list_data = payload.get("list", [])
            if not list_data:
                raise ValueError("Respuesta vacía de OpenWeather")
                
            item = list_data[0]
            aqi = item.get("main", {}).get("aqi")
            components = item.get("components", {})
            risk_state = OW_AQI_TO_RISK.get(aqi, "unknown")
            
            data = {
                "aqi": aqi,
                "risk_state": risk_state,
                "components": components
            }

        return ProviderResponse(
            data=data,
            raw_payload=payload,
            metadata={"source_system": "openweather", "available": True},
            warnings=[],
            is_partial=False,
        )
    except Exception as e:
        return ProviderResponse(
            data=None,
            raw_payload=None,
            metadata={"source_system": "openweather", "available": False},
            warnings=[f"Error consultando OpenWeather: {str(e)}"],
            is_partial=True,
        )


@st.cache_data(ttl=900, show_spinner=False)
def fetch_current_weather(city_key: str) -> ProviderResponse:
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
        "units": "metric"
    }
    request = Request(f"{OPENWEATHER_WEATHER_URL}?{urlencode(params)}", headers={"User-Agent": "EcoCities/1.0"})
    
    try:
        with urlopen(request, timeout=20) as response:
            payload_str = response.read().decode("utf-8")
            payload = json.loads(payload_str)
            
            main_data = payload.get("main", {})
            wind_data = payload.get("wind", {})
            
            data = {
                "temperature": main_data.get("temp"),
                "humidity": main_data.get("humidity"),
                "wind_speed": wind_data.get("speed"),
                "wind_deg": wind_data.get("deg")
            }

        return ProviderResponse(
            data=data,
            raw_payload=payload,
            metadata={"source_system": "openweather", "available": True},
            warnings=[],
            is_partial=False,
        )
    except Exception as e:
        return ProviderResponse(
            data=None,
            raw_payload=None,
            metadata={"source_system": "openweather", "available": False},
            warnings=[f"Error consultando OpenWeather Clima: {str(e)}"],
            is_partial=True,
        )
