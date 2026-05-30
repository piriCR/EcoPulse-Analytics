from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date, datetime

import pandas as pd

from config.oms_thresholds import classify_ratio, safe_threshold_for
from config.pollutants import POLLUTANT_CATALOG, POLLUTANT_LOOKUP, SOURCE_NAME_LOOKUP


def pollutant_display_name(code: str) -> str:
    return POLLUTANT_LOOKUP.get(code, {}).get("name", code.upper())


def pollutant_unit(code: str) -> str:
    return POLLUTANT_LOOKUP.get(code, {}).get("unit", "ug_m3")


def _extract_source_value(values: dict[str, object], code: str) -> object:
    if code in values:
        return values.get(code)
    for source_name in POLLUTANT_LOOKUP.get(code, {}).get("source_names", []):
        if source_name in values:
            return values.get(source_name)
    return None


def build_current_frame(current_values: dict[str, object]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for pollutant in POLLUTANT_CATALOG:
        code = pollutant["code"]
        value = _extract_source_value(current_values, code)
        numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        threshold = safe_threshold_for(code)
        ratio = None
        if threshold and pd.notna(numeric_value):
            ratio = float(numeric_value) / threshold
        rows.append(
            {
                "pollutant_code": code,
                "pollutant_name": pollutant["name"],
                "value": None if pd.isna(numeric_value) else float(numeric_value),
                "unit": pollutant_unit(code),
                "threshold": threshold,
                "ratio": ratio,
                "risk_state": classify_ratio(ratio),
                "present": pd.notna(numeric_value),
            }
        )
    return pd.DataFrame(rows)


def build_trend_frame(
    hourly_payload: dict[str, Sequence[object]],
    value_columns: Iterable[str],
    start_date: date | datetime | str | None = None,
    end_date: date | datetime | str | None = None,
) -> pd.DataFrame:
    timestamps = pd.to_datetime(hourly_payload.get("time", []), errors="coerce")
    frame = pd.DataFrame({"timestamp": timestamps})
    for source_name, values in hourly_payload.items():
        if source_name == "time":
            continue
        target_column = SOURCE_NAME_LOOKUP.get(source_name, source_name)
        if target_column not in value_columns and target_column != "european_aqi":
            continue
        frame[target_column] = pd.to_numeric(pd.Series(values), errors="coerce")
    if not frame.empty:
        frame = frame.dropna(subset=["timestamp"]).reset_index(drop=True)
        start_ts = pd.to_datetime(start_date, errors="coerce") if start_date is not None else None
        end_ts = pd.to_datetime(end_date, errors="coerce") if end_date is not None else None
        if start_ts is not None and not pd.isna(start_ts):
            frame = frame.loc[frame["timestamp"] >= start_ts]
        if end_ts is not None and not pd.isna(end_ts):
            frame = frame.loc[frame["timestamp"] <= end_ts + pd.Timedelta(days=1)]
        frame = frame.reset_index(drop=True)
    return frame


def summarize_current_frame(current_frame: pd.DataFrame) -> dict[str, object]:
    numeric_frame = current_frame.copy()
    if numeric_frame.empty:
        return {
            "available_indicators": 0,
            "detected_gases": [],
            "risk_state": "unknown",
            "european_aqi": None,
            "dominant_pollutant": None,
            "dominant_ratio": None,
            "critical_indicators": 0,
        }

    available_indicators = int(numeric_frame["present"].fillna(False).sum())
    detected_gases = [
        row.pollutant_code
        for row in numeric_frame.itertuples(index=False)
        if row.present and row.pollutant_code in {"no2", "o3", "so2", "co", "nh3"}
    ]

    ratios = pd.to_numeric(numeric_frame["ratio"], errors="coerce")
    if ratios.notna().any():
        dominant_index = ratios.idxmax()
        dominant_row = numeric_frame.loc[dominant_index]
        dominant_ratio = float(ratios.loc[dominant_index])
        dominant_pollutant = str(dominant_row["pollutant_code"])
        risk_state = classify_ratio(dominant_ratio)
        critical_indicators = int((ratios > 1.0).fillna(False).sum())
    else:
        dominant_pollutant = None
        dominant_ratio = None
        risk_state = "unknown"
        critical_indicators = 0

    european_aqi = None
    if "european_aqi" in numeric_frame.columns:
        european_values = pd.to_numeric(numeric_frame["european_aqi"], errors="coerce")
        if european_values.notna().any():
            european_aqi = float(european_values.dropna().iloc[0])

    return {
        "available_indicators": available_indicators,
        "detected_gases": detected_gases,
        "risk_state": risk_state,
        "european_aqi": european_aqi,
        "dominant_pollutant": dominant_pollutant,
        "dominant_ratio": dominant_ratio,
        "critical_indicators": critical_indicators,
    }