import plotly.express as px
import streamlit as st
import pandas as pd

from components.live_risk_semaphore import render_live_risk_semaphore
from components.section_header import render_section_header
from providers.open_meteo_air_quality import fetch_city_snapshot
from config.constants import DEFAULT_CITIES
from utils.page_context import get_runtime_filters

def render(filters: dict) -> None:
    render_section_header(
        "Monitoreo en Vivo",
        "Centro operativo para vigilancia ambiental inmediata."
    )
    st.caption("Vista enfocada en la detección rápida de riesgos ambientales.")

    selected_city = filters.get("focus_city")

    granularity_map = {"hourly": "hora", "daily": "día", "weekly": "semana"}
    reverse_map = {v: k for k, v in granularity_map.items()}

    mode_map = {"single": "única ciudad", "compare": "comparar"}
    reverse_mode_map = {v: k for k, v in mode_map.items()}

    current_granularity = filters.get("granularity", "daily")
    granularity_label = granularity_map.get(current_granularity, "día")

    current_mode = filters.get("comparison_mode", "single")
    mode_label = mode_map.get(current_mode, "única ciudad")

    updated_filters = {
        **filters,
        "granularity": reverse_map[granularity_label],
        "comparison_mode": reverse_mode_map[mode_label]
    }
    st.session_state["global_filters"] = updated_filters

    with st.spinner("Consultando calidad del aire..."):
        response = fetch_city_snapshot(
            selected_city,
            start_date=updated_filters.get("date_from"),
            end_date=updated_filters.get("date_to")
        )

    data = response.data
    summary = data["summary"]
    trend_frame = data["trend_frame"]
    location = data["location"]

    render_live_risk_semaphore(
        summary["risk_state"],
        location["city_name"],
        summary["dominant_pollutant"]
    )

    st.markdown("### Alerta rápida")
    risk_state = summary["risk_state"]
    if risk_state in ["good", "fair"]:
        st.success("Condiciones aceptables según los umbrales OMS.")
    elif risk_state == "moderate":
        st.warning("Riesgo moderado detectado. Se recomienda seguimiento.")
    else:
        st.error("Riesgo elevado detectado. Atención inmediata recomendada.")

    st.markdown("### Variación reciente")

    granularity = st.selectbox(
        "Granularidad",
        ["hora", "día", "semana"],
        index=["hora", "día", "semana"].index(granularity_label)
    )

    if reverse_map[granularity] == "daily":
        trend_frame = trend_frame.resample("D", on="timestamp").mean().reset_index()
    elif reverse_map[granularity] == "weekly":
        trend_frame = trend_frame.resample("W", on="timestamp").mean().reset_index()


    pollutant = summary.get("dominant_pollutant")
    if pollutant and pollutant in trend_frame.columns and not trend_frame.empty:
        chart = px.line(
            trend_frame,
            x="timestamp",
            y=pollutant,
            markers=True,
            line_shape="linear",
            title=f"Tendencia reciente de {pollutant.upper()} ({granularity})"
        )
        chart.update_traces(line=dict(width=3), marker=dict(size=6))
        chart.update_layout(
            height=420,
            margin=dict(l=20, r=20, t=50, b=20),
            yaxis=dict(title=f"{pollutant.upper()} concentración"),
            xaxis=dict(title="Fecha/Hora")
        )
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("No hay suficientes datos para construir la tendencia.")

    
if __name__ == "__main__":
    render(get_runtime_filters())
