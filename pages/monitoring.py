# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd

from components.live_risk_semaphore import render_live_risk_semaphore
from components.section_header import render_section_header
from providers.open_meteo_air_quality import fetch_city_snapshot
from config.constants import DEFAULT_CITIES, RISK_STATES
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


def render(filters: dict) -> None:
    render_section_header(
        "Monitoreo en Vivo",
        "Centro operativo para vigilancia ambiental detallada."
    )
    st.caption("Vista enfocada en la detección rápida de riesgos ambientales para una ciudad específica.")

    st.sidebar.header("Filtros de Monitoreo")
    focus_city = st.sidebar.selectbox(
        "Ciudad foco",
        options=DEFAULT_CITIES,
        index=0,
        help="Selecciona una ciudad para ver sus indicadores detallados."
    )

    granularity_map = {"hourly": "hora", "daily": "día", "weekly": "semana"}
    reverse_map = {v: k for k, v in granularity_map.items()}
    current_granularity = filters.get("granularity", "daily")
    granularity_label = granularity_map.get(current_granularity, "día")

    with st.spinner("Consultando calidad del aire..."):
        try:
            response = fetch_city_snapshot(
                focus_city,
                start_date=filters.get("date_from"),
                end_date=filters.get("date_to")
            )
        except Exception as exc:
            st.error(f"Error al consultar la ciudad foco: {exc}")
            return

    data = response.data
    summary = data["summary"]
    trend_frame = data["trend_frame"]
    current_frame = data["current_frame"]
    location = data["location"]

    top_col1, top_col2 = st.columns([1.5, 1])
    
    with top_col1:
        render_live_risk_semaphore(
            summary["risk_state"],
            location["city_name"],
            summary["dominant_pollutant"]
        )

    with top_col2:
        st.markdown("### Ubicación")
        map_df = pd.DataFrame({'lat': [location['latitude']], 'lon': [location['longitude']]})
        st.map(map_df, zoom=10, use_container_width=True)

    if summary.get("critical_indicators", 0) > 0:
        st.warning(
            f"Se detectaron {summary['critical_indicators']} indicadores por encima de umbral en {location['city_name']}; "
            f"el contaminante más crítico es {summary.get('dominant_pollutant', '—')}.",
            icon=":material/warning:"
        )
    else:
        risk_state = summary.get("risk_state", "unknown")
        state = RISK_STATES.get(risk_state, RISK_STATES["unknown"])
        st.success(
            f"{location['city_name']} se mantiene dentro de la banda visual {state['label'].lower()} con el catálogo actual de indicadores.",
            icon=":material/check_circle:"
        )

    left_col, right_col = st.columns([1.2, 1.8])

    with left_col:
        st.markdown("### Radiografía de Contaminantes")
        st.caption("Detalle de los elementos en el aire. Valores más altos implican mayor contaminación y riesgo respiratorio.")
        focus_table = _build_focus_table(current_frame)
        st.dataframe(focus_table, use_container_width=True, hide_index=True)

        detected_gases = summary.get("detected_gases", [])
        if detected_gases:
            st.info(f"Gases detectados en el entorno: {', '.join(detected_gases)}")
        else:
            st.info("No se detectaron gases con valor positivo en el conjunto actual de indicadores.")

    with right_col:
        st.markdown("### Evolución Temporal del Aire")
        st.caption("Observa cómo ha variado la contaminación recientemente.")
        
        granularity = st.selectbox(
            "Granularidad",
            ["hora", "día", "semana"],
            index=["hora", "día", "semana"].index(granularity_label),
            key="granularity_select"
        )
        
        display_trend_frame = trend_frame.copy()
        
        if reverse_map[granularity] == "daily":
            display_trend_frame = display_trend_frame.resample("D", on="timestamp").mean().reset_index()
        elif reverse_map[granularity] == "weekly":
            display_trend_frame = display_trend_frame.resample("W", on="timestamp").mean().reset_index()

        pollutant = summary.get("dominant_pollutant") or filters.get("primary_pollutant", "pm2_5")
        
        if pollutant and pollutant in display_trend_frame.columns and not display_trend_frame.empty:
            chart = px.line(
                display_trend_frame,
                x="timestamp",
                y=pollutant,
                markers=True,
                line_shape="linear",
                title=f"Tendencia reciente de {pollutant.upper()} ({granularity})"
            )
            chart.update_traces(line=dict(width=3), marker=dict(size=6))
            chart.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=50, b=20),
                yaxis=dict(title=f"{pollutant.upper()} concentración"),
                xaxis=dict(title="Fecha/Hora")
            )
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No hay suficientes datos para construir la tendencia.")

if __name__ == "__main__":
    render(get_runtime_filters())
