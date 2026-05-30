from __future__ import annotations

POLLUTANT_SAFE_THRESHOLDS = {
    "pm2_5": 15.0,
    "pm10": 45.0,
    "no2": 25.0,
    "o3": 100.0,
    "so2": 40.0,
    "co": 4000.0,
    "nh3": 200.0,
}

RISK_BANDS = [
    (0.5, "good"),
    (1.0, "fair"),
    (1.5, "moderate"),
    (2.5, "poor"),
    (4.0, "very_poor"),
]


def classify_ratio(ratio: float | None) -> str:
    if ratio is None:
        return "unknown"
    for limit, state in RISK_BANDS:
        if ratio <= limit:
            return state
    return "hazardous"


def safe_threshold_for(pollutant_code: str) -> float | None:
    return POLLUTANT_SAFE_THRESHOLDS.get(pollutant_code)
