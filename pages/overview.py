from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from components.section_header import render_section_header
from config.constants import DEFAULT_CITIES, RISK_STATES
from providers.open_meteo_air_quality import fetch_city_snapshot
from utils.page_context import get_runtime_filters


def _format_numeric(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and pd.isna(value):
        return "—"
    if isinstance(value, (int, float)):
        return f"{value:.1f}"
    return str(value)


def _build_focus_table(current_frame: pd.DataFrame) -> pd.DataFrame:
    if current_frame.empty:
        return pd.DataFrame(columns=["Indicador", "Valor", "Unidad", "Estado", "Presencia"])

    display = current_frame.copy()
    display["Indicador"] = display["pollutant_name"]
    display["Valor"] = display["value"].apply(_format_numeric)
    display["Unidad"] = display["unit"].fillna("—")
    display["Estado"] = display["risk_state"].map(lambda state: RISK_STATES.get(state, RISK_STATES["unknown"])["label"])
    display["Presencia"] = display["present"].map(lambda present: "Sí" if present else "No")
    return display[["Indicador", "Valor", "Unidad", "Estado", "Presencia"]]


def _summary_to_frame(summaries: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(summaries)
    if frame.empty:
        return frame
    frame["AQI europeo"] = pd.to_numeric(frame.get("european_aqi"), errors="coerce")
    frame["Riesgo"] = frame["risk_state"].map(lambda state: RISK_STATES.get(state, RISK_STATES["unknown"])["label"])
    frame["Contaminante crítico"] = frame["dominant_pollutant"].fillna("—")
    frame["Severidad"] = frame["dominant_ratio"].apply(_format_numeric)
    frame["Indicadores activos"] = frame["available_indicators"].fillna(0).astype(int)
    return frame[["city_name", "country_code", "AQI europeo", "Riesgo", "Contaminante crítico", "Severidad", "Indicadores activos"]]


def _build_overview_summary(summaries: list[dict], selected_count: int) -> dict[str, object]:
    frame = pd.DataFrame(summaries)
    if frame.empty:
        return {
            "cities_in_risk": 0,
            "cities_critical": 0,
            "coverage_pct": 0.0,
        }

    safe_states = {"good", "fair"}
    cities_in_risk = int((~frame["risk_state"].isin(safe_states)).sum())
    cities_critical = int((pd.to_numeric(frame["critical_indicators"], errors="coerce").fillna(0) > 0).sum())
    coverage_pct = (len(summaries) / selected_count * 100.0) if selected_count else 0.0
    return {
        "cities_in_risk": cities_in_risk,
        "cities_critical": cities_critical,
        "coverage_pct": coverage_pct,
    }


def _risk_badge_html(risk_state: str) -> str:
    state = RISK_STATES.get(risk_state, RISK_STATES["unknown"])
    return (
        "<div style='display:inline-block;padding:0.45rem 0.8rem;border-radius:999px;"
        f"background:{state['color']};color:white;font-weight:700;font-size:0.9rem;'>"
        f"Estado OMS: {state['label']}"
        "</div>"
    )


def _trend_figure(trend_frame: pd.DataFrame, primary_pollutant: str):
    chart_columns = [column for column in trend_frame.columns if column in {"european_aqi", primary_pollutant}]
    if not chart_columns:
        chart_columns = list(trend_frame.columns)

    display_map = {
        "european_aqi": "AQI europeo",
        "pm2_5": "PM2.5",
        "pm10": "PM10",
        "no2": "NO2",
        "o3": "O3",
        "so2": "SO2",
        "co": "CO",
        "nh3": "NH3",
    }

    if len(chart_columns) == 1:
        y_column = chart_columns[0]
        figure = px.line(
            trend_frame,
            x="timestamp",
            y=y_column,
            markers=True,
            labels={"timestamp": "Hora", y_column: display_map.get(y_column, y_column)},
            title="Tendencia reciente",
        )
    else:
        melted = trend_frame[["timestamp", *chart_columns]].melt(
            id_vars=["timestamp"],
            var_name="Serie",
            value_name="Valor",
        )
        melted["Serie"] = melted["Serie"].map(lambda value: display_map.get(value, value))
        figure = px.line(
            melted,
            x="timestamp",
            y="Valor",
            color="Serie",
            markers=True,
            labels={"timestamp": "Hora", "Valor": "Valor registrado", "Serie": "Serie"},
            title="Tendencia reciente",
        )

    figure.update_layout(
        xaxis_title="Hora",
        yaxis_title="Valor registrado",
        legend_title_text="Serie",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return figure



def render(filters: dict) -> None:
    render_section_header("Inicio", "Resumen ejecutivo del estado ambiental urbano.")

    selected_cities = filters.get("cities") or list(DEFAULT_CITIES[:3])
    focus_city = filters.get("focus_city") or selected_cities[0]
    date_from = filters.get("date_from")
    date_to = filters.get("date_to")
    date_from_str = date_from.isoformat() if hasattr(date_from, "isoformat") else None
    date_to_str = date_to.isoformat() if hasattr(date_to, "isoformat") else None

    st.caption(
        "Fuente principal: Open-Meteo Air Quality API. La pantalla prioriza lectura rápida, estado OMS, comparación breve y acceso directo a detalle."
    )

    city_snapshots: list[dict] = []
    focus_snapshot = None
    errors: list[str] = []

    with st.spinner("Consultando calidad del aire en las ciudades seleccionadas..."):
        for city_key in selected_cities:
            try:
                response = fetch_city_snapshot(city_key, start_date=date_from_str, end_date=date_to_str)
                city_snapshots.append(response.data["summary"])
                if city_key == focus_city:
                    focus_snapshot = response
            except Exception as exc:  # pragma: no cover - runtime resilience
                errors.append(f"{city_key}: {exc}")

    if focus_snapshot is None:
        try:
            focus_snapshot = fetch_city_snapshot(focus_city, start_date=date_from_str, end_date=date_to_str)
        except Exception as exc:  # pragma: no cover - runtime resilience
            st.error(f"No fue posible consultar la ciudad foco '{focus_city}': {exc}")
            if errors:
                st.warning("; ".join(errors))
            return

    focus_data = focus_snapshot.data
    focus_summary = focus_data["summary"]
    focus_current = focus_data["current_frame"]
    focus_trend = focus_data["trend_frame"]
    focus_location = focus_data["location"]

    if focus_summary.get("city_key") is None:
        st.warning("La ciudad foco no devolvió datos estructurados.")

    top_col1, top_col2, top_col3, top_col4 = st.columns(4)
    top_col1.metric("Ciudades consultadas", len(selected_cities))
    top_col2.metric("Indicadores activos", focus_summary.get("available_indicators", 0))
    top_col3.metric("Gases detectados", len(focus_summary.get("detected_gases", [])))
    top_col4.metric("Última actualización", datetime.now().strftime("%H:%M"))


    if focus_summary.get("critical_indicators", 0) > 0:
        st.warning(
            f"Se detectaron {focus_summary['critical_indicators']} indicadores por encima de umbral en la ciudad foco; "
            f"el contaminante más crítico es {focus_summary.get('dominant_pollutant', '—')}.")
    else:
        risk_state = focus_summary.get("risk_state", "unknown")
        state = RISK_STATES.get(risk_state, RISK_STATES["unknown"])
        st.success(
            f"La ciudad foco se mantiene dentro de la banda visual {state['label'].lower()} con el catálogo actual de indicadores.")

    overview_summary = _build_overview_summary(city_snapshots, len(selected_cities))
    st.markdown("### Resumen OMS y cobertura")
    oms_col1, oms_col2, oms_col3 = st.columns(3)
    oms_col1.metric("Ciudades en riesgo", overview_summary["cities_in_risk"])
    oms_col2.metric("Ciudades críticas", overview_summary["cities_critical"])
    oms_col3.metric("Cobertura de consulta", f"{overview_summary['coverage_pct']:.0f}%")

    left_col, right_col = st.columns([1.35, 1])
    with left_col:
        st.markdown("### Indicadores unificados")
        st.caption("Tabla de lectura rápida con valor, unidad y presencia por contaminante.")
        focus_table = _build_focus_table(focus_current)
        st.dataframe(focus_table, use_container_width=True, hide_index=True)

        detected_gases = focus_summary.get("detected_gases", [])
        if detected_gases:
            st.info(f"Gases detectados en el entorno: {', '.join(detected_gases)}")
        else:
            st.info("No se detectaron gases con valor positivo en el conjunto actual de indicadores.")

    with right_col:
        st.markdown("### Ranking rápido de ciudades")
        st.caption("Ordenado por Severidad y número de indicadores activos.")
        ranking_frame = _summary_to_frame(city_snapshots)
        if ranking_frame.empty:
            st.info("No hay ciudades suficientes para construir el ranking.")
        else:
            ranking_frame = ranking_frame.sort_values(by=["Severidad", "Indicadores activos"], ascending=[False, False])

            st.dataframe(ranking_frame, use_container_width=True, hide_index=True)

            worst_city = ranking_frame.iloc[0]
            best_city = ranking_frame.iloc[-1]
            
            st.metric("Ciudad con peor estado OMS", f"{worst_city['city_name']}")
            st.metric("Ciudad con mejor estado OMS", f"{best_city['city_name']}")

    st.markdown("### Tendencia reciente")
    trend_frame = focus_trend.copy()
    if trend_frame.empty:
        st.info("No se pudo construir una tendencia temporal con los datos recibidos.")
    else:
        st.caption("Eje horizontal: hora. Eje vertical: valor registrado del indicador.")
        figure = _trend_figure(trend_frame, filters.get("primary_pollutant", "pm2_5"))
        st.plotly_chart(figure, use_container_width=True)

    st.markdown("### Acceso rápido")
    st.caption("Atajos contextuales para moverse sin perder el foco analítico actual.")
    quick_city = st.selectbox("Ciudad para detalle", options=selected_cities, index=selected_cities.index(focus_city) if focus_city in selected_cities else 0)
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    if quick_col1.button("Abrir perfil de ciudad", use_container_width=True):
        updated_filters = {**filters, "focus_city": quick_city}
        st.session_state["global_filters"] = updated_filters
        st.switch_page("pages/city_profile.py")
    with quick_col2:
        st.page_link("pages/alerts.py", label="Ir a Alertas OMS", icon=":material/warning:")
        st.page_link("pages/monitoring.py", label="Monitoreo en Vivo", icon=":material/radar:")
    with quick_col3:
        st.page_link("pages/comparison.py", label="Ciudad Comparativa", icon=":material/compare_arrows:")
        st.page_link("pages/timeline.py", label="Evolución Temporal", icon=":material/timeline:")

    if errors:
        with st.expander("Advertencias de consulta"):
            for error in errors:
                st.write(f"- {error}")


if __name__ == "__main__":
    render(get_runtime_filters())
