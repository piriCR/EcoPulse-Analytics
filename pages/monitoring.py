import plotly.express as px
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
    st.markdown("### 🔍 Reporte de Riesgos")
    cols = st.columns(3)
    
    valid_data = current_frame.dropna(subset=['value'])
    
    for i, (_, row) in enumerate(valid_data.iterrows()):
        key = str(row["pollutant_name"]).lower().strip()
        info = GUIA_SALUD.get(key, {"nombre": row["pollutant_name"].upper(), "impacto": "Contaminante detectado."})
        
        is_dominant = (key == dominant)
        estado = row["risk_state"]
        color = "#2ecc71" if estado == "good" else ("#f1c40f" if estado == "moderate" else "#e74c3c")
        
        # Estilos visuales
        border_width = "4px" if is_dominant else "2px"
        shadow = "0 4px 8px rgba(0,0,0,0.2)" if is_dominant else "none"
        badge = '<div style="background-color:#e74c3c; color:white; padding:2px 8px; border-radius:10px; font-size:0.7em; margin-bottom:5px; display:inline-block;">CONTAMINANTE DOMINANTE</div><br>' if is_dominant else ""

        # HTML COMPACTO (Sin saltos de línea internos)
        html_card = f'<div style="border:{border_width} solid {color}; padding:15px; border-radius:12px; text-align:center; height:280px; margin-bottom:20px; background-color:#ffffff; box-shadow:{shadow};">{badge}<div style="font-size:1.1em; font-weight:bold; margin-bottom:10px;">{info["nombre"]}</div><div style="font-size:1.6em; color:{color}; font-weight:bold; margin-bottom:10px;">{row["value"]:.1f} <span style="font-size:0.5em; color:#666;">{row["unit"]}</span></div><div style="font-size:0.85em; color:#444; line-height:1.4;">{info["impacto"]}</div></div>'
        
        with cols[i % 3]:
            st.markdown(html_card, unsafe_allow_html=True)

    st.write("---")
    st.markdown("##### 💡 Entendiendo los riesgos")
    st.caption("Los contaminantes afectan al cuerpo principalmente por inflamación y estrés oxidativo al entrar en el sistema respiratorio.")
    
    
if __name__ == "__main__":
    render(get_runtime_filters())