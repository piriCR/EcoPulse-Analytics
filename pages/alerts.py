import pandas as pd
import streamlit as st

from components.section_header import render_section_header
from providers.open_meteo_air_quality import fetch_city_snapshot
from config.constants import DEFAULT_CITIES, RISK_STATES
from utils.page_context import get_runtime_filters

def get_color_for_state(state):
    """Retorna un color según el nivel de riesgo."""
    mapping = {
        "good": "#2ecc71",      # Verde
        "moderate": "#f1c40f",  # Amarillo
        "poor": "#e67e22",      # Naranja
        "very_poor": "#e74c3c", # Rojo
        "hazardous": "#8e44ad"  # Morado
    }
    return mapping.get(state, "#95a5a6")

def render(filters: dict) -> None:
    render_section_header("¿Qué tan limpio está el aire?", "Un reporte sencillo para cuidar tu salud.")

    with st.spinner("Revisando la calidad del aire..."):
        city_alerts = []
        for city in DEFAULT_CITIES:
            try:
                response = fetch_city_snapshot(city, start_date=filters.get("date_from"), end_date=filters.get("date_to"))
                summary = response.data["summary"]
                city_alerts.append({"Ciudad": city, **summary})
            except:
                continue

    df = pd.DataFrame(city_alerts)
    if df.empty:
        st.warning("No se pudieron obtener los datos en este momento.")
        return

    # --- Resumen para el usuario ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Ciudades revisadas", len(df))
    col2.metric("En alerta", len(df[df["risk_state"].isin(["poor", "very_poor", "hazardous"])]))
    col3.metric("Ambiente saludable", len(df[df["risk_state"] == "good"]))

    st.markdown("---")

    # --- Tarjetas de estado ---
    st.subheader("📍 ¿Cómo está el aire en tu ciudad?")
    
    for _, row in df.iterrows():
        color = get_color_for_state(row["risk_state"])
        estado_label = RISK_STATES.get(row["risk_state"], {}).get("label", "Desconocido")
        
        with st.container():
            st.markdown(f"""
            <div style="border-left: 5px solid {color}; padding: 12px; background-color: #f9f9f9; margin-bottom: 10px; border-radius: 5px;">
                <h4 style="margin:0;">{row['Ciudad']}</h4>
                <p style="margin:0;"><strong>Situación:</strong> <span style="color:{color};">{estado_label}</span></p>
                <p style="margin:0; font-size: 0.9em;">Contaminante principal: <strong>{row.get('dominant_pollutant', 'N/A').upper()}</strong> | Niveles preocupantes detectados: <strong>{row.get('critical_indicators', 0)}</strong></p>
            </div>
            """, unsafe_allow_html=True)

    # --- Tabla de datos ---
    st.markdown("### Tabla de consulta rápida")
    # Traducimos las columnas de la tabla para el usuario
    df_display = df.rename(columns={
        "risk_state": "Situación actual", 
        "dominant_pollutant": "Contaminante principal", 
        "critical_indicators": "Nivel de peligro (cuenta)"
    })
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    render(get_runtime_filters())