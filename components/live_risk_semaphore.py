import streamlit as st
from config.constants import RISK_STATES

def render_live_risk_semaphore(risk_state: str, city_name: str, dominant_pollutant: str | None) -> None:
    state = RISK_STATES.get(risk_state, RISK_STATES["unknown"])

    st.markdown("---")

    # Bloque principal con fondo dinámico
    st.markdown(
        f"""
        <div style="
            background:{state['color']};
            padding:25px;
            border-radius:12px;
            text-align:center;
            color:white;
            font-family:Segoe UI, sans-serif;
        ">
            <h2 style="margin:0;">Riesgo Climático en Vivo</h2>
            <h3 style="margin-top:10px;">{city_name}</h3>
            <h1 style="margin-top:15px; font-size:2.2em;">{state["label"]}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Semáforo OMS con círculos de color
    st.markdown("### Semáforo OMS")
    levels = [
        ("good", "Bueno"),
        ("fair", "Aceptable"),
        ("moderate", "Moderado"),
        ("poor", "Malo"),
        ("very_poor", "Muy malo"),
        ("hazardous", "Peligroso"),
        ("unknown", "Desconocido"),
    ]

    html_levels = ""
    for key, label in levels:
        color = RISK_STATES[key]["color"]
        highlight = "box-shadow:0 0 10px rgba(0,0,0,0.4);" if key == risk_state else ""
        html_levels += f"""
        <div style="display:flex;align-items:center;margin:6px 0;">
        <div style="width:20px;height:20px;border-radius:50%;background:{color};{highlight}"></div>
        <span style="margin-left:10px;">{label}</span>
        </div>
        """
        
    st.markdown(html_levels, unsafe_allow_html=True)

    # Estado actual
    st.markdown("### Estado actual")
    col1, col2 = st.columns(2)
    col1.metric("Estado OMS", state["label"])
    col2.metric("Contaminante dominante", dominant_pollutant.upper() if dominant_pollutant else "-")
