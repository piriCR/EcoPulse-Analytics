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

# Guía de salud
GUIA_SALUD = {
    "pm2_5": {"nombre": "Partículas Finas (PM2.5)", "impacto": "Penetran profundamente en pulmones y sangre. Riesgo de inflamación sistémica."},
    "pm10": {"nombre": "Partículas Gruesas (PM10)", "impacto": "Se depositan en vías respiratorias superiores, causando tos e irritación."},
    "o3": {"nombre": "Ozono (O3)", "impacto": "Actúa como oxidante que quema el tejido pulmonar, agravando el asma."},
    "no2": {"nombre": "Dióxido de Nitrógeno (NO2)", "impacto": "Debilita las defensas pulmonares, aumentando la susceptibilidad a infecciones."},
    "so2": {"nombre": "Dióxido de Azufre (SO2)", "impacto": "Provoca el estrechamiento de vías aéreas, dificultando la respiración."},
    "co": {"nombre": "Monóxido de Carbono (CO)", "impacto": "Impide que el oxígeno llegue al cerebro y corazón, causando fatiga extrema."}
}

def render(filters: dict) -> None:
    render_section_header("¿Cómo está el aire?", "Monitoreo ciudadano para tu salud.")
    
    focus_city = st.sidebar.selectbox("Ciudad:", options=DEFAULT_CITIES)
    
    with st.spinner("Consultando datos ambientales..."):
        response = fetch_city_snapshot(focus_city, start_date=filters.get("date_from"), end_date=filters.get("date_to"))
        summary, current_frame = response.data["summary"], response.data["current_frame"]
        dominant = summary.get("dominant_pollutant", "").lower()

        # Guardar contexto global para el chat de IA
        st.session_state["current_pollution_context"] = {
            "page_name": "Monitoreo en Vivo",
            "ciudad": focus_city,
            "resumen_estado": summary,
            "datos_contaminantes": current_frame
        }

    # 1. Semáforo y Ubicación
    c1, c2 = st.columns([1.5, 1])
    with c1:
        render_live_risk_semaphore(summary["risk_state"], response.data["location"]["city_name"], summary["dominant_pollutant"])
    with c2:
        st.map(pd.DataFrame({'lat': [response.data["location"]['latitude']], 'lon': [response.data["location"]['longitude']]}))

    # 2. Diagnóstico Visual Directo
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 2rem; margin-bottom: 1.5rem;">
        <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; background-color: rgba(239, 68, 68, 0.1); display: flex; align-items: center; justify-content: center; color: #ef4444;">
            <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>
        </div>
        <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--text-color);">Reporte de Riesgos</h3>
    </div>
    <style>
    .eco-risk-card { padding: 1.25rem; border: 1px solid var(--border-color); border-radius: 1rem; background-color: var(--secondary-background-color); transition: all 0.3s; height: 260px; display: flex; flex-direction: column; position: relative; overflow: hidden; }
    .eco-risk-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
    .eco-risk-dominant { border: 2px solid #ef4444; box-shadow: 0 4px 6px -1px rgba(239,68,68,0.15); }
    .eco-risk-badge { position: absolute; top: 0; right: 0; background-color: #ef4444; color: white; font-size: 0.65rem; font-weight: 700; padding: 0.25rem 0.75rem; border-bottom-left-radius: 0.5rem; letter-spacing: 0.05em; z-index: 10; }
    .eco-risk-title { font-size: 1rem; font-weight: 700; color: var(--text-color); margin-bottom: 0.5rem; text-align: center; }
    .eco-risk-value { font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem; text-align: center; line-height: 1; }
    .eco-risk-unit { font-size: 0.875rem; font-weight: 500; opacity: 0.7; }
    .eco-risk-impact { font-size: 0.85rem; color: var(--text-color); opacity: 0.8; text-align: center; line-height: 1.4; margin-top: auto; padding-top: 0.75rem; border-top: 1px dashed var(--border-color); }
    </style>
    """, unsafe_allow_html=True)
    cols = st.columns(3)
    
    valid_data = current_frame.dropna(subset=['value'])
    
    for i, (_, row) in enumerate(valid_data.iterrows()):
        key = str(row["pollutant_name"]).lower().strip()
        info = GUIA_SALUD.get(key, {"nombre": row["pollutant_name"].upper(), "impacto": "Contaminante detectado."})
        
        is_dominant = (key == dominant)
        estado = row["risk_state"]
        color = "#2ecc71" if estado == "good" else ("#f1c40f" if estado == "moderate" else "#e74c3c")
        
        # Estilos visuales
        estado = row["risk_state"]
        color = "#10b981" if estado == "good" else ("#f59e0b" if estado == "moderate" else "#ef4444")
        
        dom_class = "eco-risk-dominant" if is_dominant else ""
        badge = '<div class="eco-risk-badge">DOMINANTE</div>' if is_dominant else ""
        
        html_card = f"""<div class="eco-risk-card {dom_class}">
{badge}
<div class="eco-risk-title">{info["nombre"]}</div>
<div class="eco-risk-value" style="color: {color};">{row["value"]:.1f} <span class="eco-risk-unit" style="color: var(--text-color);">{row["unit"]}</span></div>
<div class="eco-risk-impact">{info["impacto"]}</div>
<div style="position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: {color}; opacity: 0.8;"></div>
</div>"""
        
        with cols[i % 3]:
            st.markdown(html_card, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("""
    <div style="display: flex; align-items: flex-start; gap: 1rem; padding: 1.5rem; border-radius: 1rem; background-color: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2);">
        <div style="background-color: rgba(59, 130, 246, 0.15); color: #3b82f6; border-radius: 50%; padding: 0.5rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
            <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
        <div>
            <h5 style="margin: 0 0 0.5rem 0; font-size: 1.125rem; font-weight: 700; color: var(--text-color);">Entendiendo los riesgos</h5>
            <p style="margin: 0; font-size: 0.875rem; color: var(--text-color); opacity: 0.8; line-height: 1.5;">Los contaminantes afectan al cuerpo principalmente por inflamación y estrés oxidativo al entrar en el sistema respiratorio.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    
if __name__ == "__main__":
    render(get_runtime_filters())