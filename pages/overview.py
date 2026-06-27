from __future__ import annotations

import base64
import os
from datetime import datetime

import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import streamlit as st

from config.constants import DEFAULT_CITIES, RISK_STATES
from providers.open_meteo_air_quality import fetch_city_snapshot
from utils.page_context import get_runtime_filters


def get_base64_of_bin_file(bin_file):
    if not os.path.exists(bin_file):
        return ""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def _format_numeric(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and pd.isna(value):
        return "—"
    if isinstance(value, (int, float)):
        return f"{value:.1f}"
    return str(value)


def _summary_to_frame(summaries: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(summaries)
    if frame.empty:
        return frame
    frame["Índice Global (AQI)"] = pd.to_numeric(frame.get("european_aqi"), errors="coerce")
    frame["Riesgo"] = frame["risk_state"].map(lambda state: RISK_STATES.get(state, RISK_STATES["unknown"])["label"])
    frame["Peor Contaminante"] = frame["dominant_pollutant"].fillna("—")
    frame["Nivel de Severidad"] = frame["dominant_ratio"].apply(_format_numeric)
    frame["Datos Disponibles"] = frame["available_indicators"].fillna(0).astype(int)
    return frame[["city_name", "country_code", "Índice Global (AQI)", "Riesgo", "Peor Contaminante", "Nivel de Severidad", "Datos Disponibles"]]


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


def render(filters: dict) -> None:
    # 1. BANNER HERO PROFESIONAL CON CSS Y HTML
    img_path = r"C:\Users\Sanch\.gemini\antigravity\brain\e884dfb5-82af-4887-b6d3-88e60311a4b3\climate_action_hero_bg_1781581238331.png"
    img_base64 = get_base64_of_bin_file(img_path)
    
    bg_style = f"background-image: linear-gradient(rgba(10, 40, 20, 0.65), rgba(5, 20, 10, 0.85)), url('data:image/png;base64,{img_base64}');" if img_base64 else "background-color: #0f2a1a;"

    st.markdown(f"""
        <div style="
            {bg_style}
            background-size: cover;
            background-position: center;
            border-radius: 16px;
            padding: 60px 40px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 2rem;
            margin-top: -2rem;
            border: 1px solid rgba(255,255,255,0.1);
        ">
            <h1 style="color: #ffffff; font-size: 3rem; font-weight: 800; margin-bottom: 5px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); font-family: 'Inter', sans-serif;">
                ¡Bienvenido a EcoPulse Analytics!
            </h1>
            <h2 style="color: #4ade80; font-size: 1.8rem; font-weight: 600; margin-bottom: 20px; text-shadow: 0 1px 3px rgba(0,0,0,0.5);">
                ODS 13: Acción por el Clima
            </h2>
            <p style="font-size: 1.15rem; font-weight: 300; max-width: 850px; margin: 0 auto; line-height: 1.6; color: #f1f5f9; text-shadow: 0 1px 2px rgba(0,0,0,0.8);">
                Tu centro de inteligencia para el monitoreo en tiempo real de la calidad del aire y el impacto ambiental. 
                Democratizamos los datos climáticos globales para impulsar la concientización y ayudar a tomar decisiones sostenibles.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1.5 SECCIÓN DE NAVEGACIÓN Y MÓDULOS
    st.markdown("### :material/dashboard_customize: Explora la Plataforma")
    st.caption("Herramientas analíticas diseñadas para evaluar el riesgo ambiental.")
    
    mod1, mod2, mod3 = st.columns(3)
    with mod1:
        with st.container(border=True, height=170):
            st.markdown("#### :material/monitoring: Monitoreo en Vivo")
            st.markdown("Análisis forense de una **ciudad específica**. Curvas de tendencia de gases y alertas inmediatas.")
    with mod2:
        with st.container(border=True, height=170):
            st.markdown("#### :material/map: Ciudad Comparativa")
            st.markdown("Contrasta el impacto de múltiples regiones con **mapas de calor** y niveles de toxicidad cara a cara.")
    with mod3:
        with st.container(border=True, height=170):
            st.markdown("#### :material/notifications_active: Alertas Sanitarias")
            st.markdown("Notificaciones automatizadas que detectan si los gases superan los **umbrales seguros de la OMS**.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. SECCIÓN DE DATOS GLOBALES
    st.markdown("### :material/public: Panorama Ambiental Actual")
    st.caption("Visión general de capitales seleccionadas para demostración rápida.")

    selected_cities = list(DEFAULT_CITIES[:5]) # 5 ciudades de demostración
    
    date_from = filters.get("date_from")
    date_to = filters.get("date_to")
    date_from_str = date_from.isoformat() if hasattr(date_from, "isoformat") else None
    date_to_str = date_to.isoformat() if hasattr(date_to, "isoformat") else None

    city_snapshots: list[dict] = []
    errors: list[str] = []

    with st.spinner("Sincronizando con satélites y estaciones terrestres..."):
        for city_key in selected_cities:
            try:
                response = fetch_city_snapshot(city_key, start_date=date_from_str, end_date=date_to_str)
                city_snapshots.append(response.data["summary"])
            except Exception as exc:  # pragma: no cover
                errors.append(f"{city_key}: {exc}")

    overview_summary = _build_overview_summary(city_snapshots, len(selected_cities))
    
    # KPIs Estilizados
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.info(f"**Nodos Analizados**\n### {len(selected_cities)}", icon=":material/location_city:")
    with kpi_col2:
        val = overview_summary["cities_in_risk"]
        if val > 0: st.warning(f"**En Alerta (OMS)**\n### {val}", icon=":material/warning:")
        else: st.success(f"**En Alerta (OMS)**\n### {val}", icon=":material/shield:")
    with kpi_col3:
        val = overview_summary["cities_critical"]
        if val > 0: st.error(f"**Riesgo Crítico**\n### {val}", icon=":material/emergency:")
        else: st.success(f"**Riesgo Crítico**\n### {val}", icon=":material/check_circle:")
    with kpi_col4:
        st.success(f"**Sincronizado**\n### {datetime.now().strftime('%H:%M')}", icon=":material/sync:")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. GRÁFICAS Y RANKINGS
    left_col, right_col = st.columns([1.2, 1])
    ranking_frame = _summary_to_frame(city_snapshots)
    
    with left_col:
        with st.container(border=True):
            st.markdown("#### :material/air: Estado de la Calidad del Aire")
            st.caption("Proporción de ciudades según su nivel de seguridad ambiental para la población.")
            if not ranking_frame.empty:
                risk_counts = ranking_frame['Riesgo'].value_counts().reset_index()
                risk_counts.columns = ['Estado Ambiental', 'Cantidad de Ciudades']
                
                chart = px.pie(
                    risk_counts, 
                    values='Cantidad de Ciudades', 
                    names='Estado Ambiental',
                    hole=0.45,
                    color='Estado Ambiental',
                    color_discrete_map={state["label"]: state["color"] for state in RISK_STATES.values()}
                )
                chart.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
                chart.update_layout(
                    margin=dict(l=10, r=10, t=10, b=30), 
                    height=320,
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                chart.add_annotation(text="ODS 13", x=0.5, y=0.5, font_size=18, showarrow=False)
                st.plotly_chart(chart, use_container_width=True)
            
    with right_col:
        with st.container(border=True):
            st.markdown("#### :material/masks: ¿Qué estamos respirando?")
            st.caption("Conciencia ambiental: áreas prioritarias para promover entornos saludables.")
            if not ranking_frame.empty:
                ranking_display = ranking_frame.sort_values(by=["Nivel de Severidad"], ascending=[False])
                
                for _, row in ranking_display.iterrows():
                    risk_label = row["Riesgo"]
                    color = next((s["color"] for s in RISK_STATES.values() if s["label"] == risk_label), "gray")
                    
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; margin-bottom: 8px; border-radius: 8px; background-color: rgba(128,128,128,0.05); border-left: 5px solid {color};">
                        <div>
                            <strong style="font-size: 1.1rem;">{row['city_name']}</strong>
                            <div style="font-size: 0.8rem; color: #666;">Elemento más crítico: {row['Peor Contaminante']}</div>
                        </div>
                        <div style="text-align: right;">
                            <span style="background-color: {color}; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                                {risk_label}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    if errors:
        with st.expander("Información de diagnóstico (Errores de conexión)"):
            for error in errors:
                st.write(f"- {error}")
                
    st.session_state["current_pollution_context"] = {
        "page_name": "Inicio (Panorama Global)",
        "kpis_resumen": overview_summary,
        "ranking_ciudades": ranking_frame
    }

if __name__ == "__main__":
    render(get_runtime_filters())
