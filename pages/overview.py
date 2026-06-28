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

    st.markdown("""<style>
.eco-module-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.25rem; margin-top: 1rem; margin-bottom: 2rem; }
.eco-module-card { padding: 1.5rem; border: 1px solid var(--border-color); border-radius: 1rem; background-color: var(--secondary-background-color); transition: all 0.3s; display: flex; flex-direction: column; gap: 0.75rem; text-decoration: none; }
.eco-module-card:hover { border-color: #4ade80; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.eco-module-icon { width: 2rem; height: 2rem; color: #4ade80; }
.eco-module-icon-bg { width: 3.5rem; height: 3.5rem; border-radius: 0.75rem; background-color: rgba(74, 222, 128, 0.1); display: flex; align-items: center; justify-content: center; }
.eco-module-title { font-size: 1.125rem; font-weight: 700; color: var(--text-color); margin: 0; }
.eco-module-desc { font-size: 0.875rem; color: var(--text-color); opacity: 0.8; margin: 0; line-height: 1.5; }
.eco-section-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.25rem; }
.eco-section-icon { width: 1.75rem; height: 1.75rem; color: #4ade80; }
.eco-section-title { font-size: 1.5rem; font-weight: 700; color: var(--text-color); margin: 0; }
.eco-section-subtitle { font-size: 0.875rem; color: var(--text-color); opacity: 0.7; margin: 0 0 1.5rem 0; }
</style>
<div class="eco-section-header">
<svg class="eco-section-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
<h3 class="eco-section-title">Explora la Plataforma</h3>
</div>
<p class="eco-section-subtitle">Herramientas analíticas diseñadas para evaluar el riesgo ambiental.</p>
<div class="eco-module-grid">
<div class="eco-module-card">
<div class="eco-module-icon-bg">
<svg class="eco-module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
</div>
<h4 class="eco-module-title">Monitoreo en Vivo</h4>
<p class="eco-module-desc">Análisis forense de una <strong>ciudad específica</strong>. Curvas de tendencia de gases y alertas inmediatas.</p>
</div>
<div class="eco-module-card">
<div class="eco-module-icon-bg">
<svg class="eco-module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path></svg>
</div>
<h4 class="eco-module-title">Ciudad Comparativa</h4>
<p class="eco-module-desc">Contrasta el impacto de múltiples regiones con <strong>mapas de calor</strong> y niveles de toxicidad cara a cara.</p>
</div>
<div class="eco-module-card">
<div class="eco-module-icon-bg">
<svg class="eco-module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
</div>
<h4 class="eco-module-title">Alertas Sanitarias</h4>
<p class="eco-module-desc">Notificaciones automatizadas que detectan si los gases superan los <strong>umbrales seguros de la OMS</strong>.</p>
</div>
</div>""", unsafe_allow_html=True)

    # 2. SECCIÓN DE DATOS GLOBALES
    st.markdown("""<div class="eco-section-header" style="margin-top: 1rem;">
<svg class="eco-section-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
<h3 class="eco-section-title">Panorama Ambiental Actual</h3>
</div>
<p class="eco-section-subtitle">Visión general de capitales seleccionadas para demostración rápida.</p>""", unsafe_allow_html=True)

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
    
    # KPIs Estilizados con HTML y CSS
    val_risk = overview_summary["cities_in_risk"]
    val_crit = overview_summary["cities_critical"]
    time_str = datetime.now().strftime('%H:%M')
    nodes = len(selected_cities)
    
    risk_color = "#eab308" if val_risk > 0 else "#22c55e"
    risk_icon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>' if val_risk > 0 else '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>'
    
    crit_color = "#ef4444" if val_crit > 0 else "#22c55e"
    crit_icon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>' if val_crit > 0 else '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
    
    st.markdown(f"""<style>
.eco-kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
.eco-kpi-card {{ padding: 1.25rem; border: 1px solid var(--border-color); border-radius: 1rem; background-color: var(--secondary-background-color); display: flex; align-items: center; gap: 1rem; transition: all 0.3s; }}
.eco-kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
.eco-kpi-icon-wrapper {{ width: 3rem; height: 3rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
.eco-kpi-icon {{ width: 1.5rem; height: 1.5rem; }}
.eco-kpi-content {{ display: flex; flex-direction: column; }}
.eco-kpi-value {{ font-size: 1.5rem; font-weight: 700; color: var(--text-color); line-height: 1.2; margin: 0; }}
.eco-kpi-label {{ font-size: 0.875rem; color: var(--text-color); opacity: 0.7; margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
</style>
<div class="eco-kpi-grid">
<div class="eco-kpi-card" style="border-left: 4px solid #3b82f6;">
<div class="eco-kpi-icon-wrapper" style="background-color: rgba(59, 130, 246, 0.1); color: #3b82f6;">
<svg class="eco-kpi-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
</div>
<div class="eco-kpi-content">
<p class="eco-kpi-value">{nodes}</p>
<p class="eco-kpi-label">Nodos Analizados</p>
</div>
</div>
<div class="eco-kpi-card" style="border-left: 4px solid {risk_color};">
<div class="eco-kpi-icon-wrapper" style="background-color: {risk_color}20; color: {risk_color};">
<svg class="eco-kpi-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">{risk_icon}</svg>
</div>
<div class="eco-kpi-content">
<p class="eco-kpi-value">{val_risk}</p>
<p class="eco-kpi-label">En Alerta (OMS)</p>
</div>
</div>
<div class="eco-kpi-card" style="border-left: 4px solid {crit_color};">
<div class="eco-kpi-icon-wrapper" style="background-color: {crit_color}20; color: {crit_color};">
<svg class="eco-kpi-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">{crit_icon}</svg>
</div>
<div class="eco-kpi-content">
<p class="eco-kpi-value">{val_crit}</p>
<p class="eco-kpi-label">Riesgo Crítico</p>
</div>
</div>
<div class="eco-kpi-card" style="border-left: 4px solid #10b981;">
<div class="eco-kpi-icon-wrapper" style="background-color: rgba(16, 185, 129, 0.1); color: #10b981;">
<svg class="eco-kpi-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
</div>
<div class="eco-kpi-content">
<p class="eco-kpi-value">{time_str}</p>
<p class="eco-kpi-label">Sincronizado</p>
</div>
</div>
</div>""", unsafe_allow_html=True)

    # 3. GRÁFICAS Y RANKINGS
    left_col, right_col = st.columns([1.2, 1])
    ranking_frame = _summary_to_frame(city_snapshots)
    
    with left_col:
        with st.container(border=True):
            st.markdown("""<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
<svg style="width: 1.5rem; height: 1.5rem; color: #3b82f6;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
<h4 style="margin: 0; font-weight: 600;">Estado de la Calidad del Aire</h4>
</div>
<p style="font-size: 0.85rem; color: var(--text-color); opacity: 0.7; margin-bottom: 1rem;">Proporción de ciudades según su nivel de seguridad ambiental para la población.</p>""", unsafe_allow_html=True)
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
            st.markdown("""<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
<svg style="width: 1.5rem; height: 1.5rem; color: #a855f7;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.618 5.984A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016zM12 9v2m0 4h.01"></path></svg>
<h4 style="margin: 0; font-weight: 600;">¿Qué estamos respirando?</h4>
</div>
<p style="font-size: 0.85rem; color: var(--text-color); opacity: 0.7; margin-bottom: 1rem;">Conciencia ambiental: áreas prioritarias para promover entornos saludables.</p>""", unsafe_allow_html=True)
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
