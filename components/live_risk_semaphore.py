import streamlit as st
from config.constants import RISK_STATES

def render_live_risk_semaphore(risk_state: str, city_name: str, dominant_pollutant: str | None, consensus_status: str | None = None) -> None:
    state = RISK_STATES.get(risk_state, RISK_STATES["unknown"])
    color = state['color']

    # SVG Icon based on risk level
    if risk_state in ["good", "fair"]:
        icon_svg = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
    elif risk_state in ["moderate", "poor"]:
        icon_svg = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>'
    else:
        icon_svg = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>'

    consensus_html = ""
    if consensus_status == "Alta Confianza":
        consensus_html = '<div style="margin-top: 1rem; display: inline-flex; align-items: center; gap: 0.5rem; background-color: rgba(16, 185, 129, 0.15); color: #10b981; padding: 0.35rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3);"><svg style="width: 1rem; height: 1rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg> Consenso de Modelos: Alta Confianza</div>'
    elif consensus_status:
        consensus_html = f'<div style="margin-top: 1rem; display: inline-flex; align-items: center; gap: 0.5rem; background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; padding: 0.35rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; border: 1px solid rgba(245, 158, 11, 0.3);"><svg style="width: 1rem; height: 1rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg> Consenso de Modelos: {consensus_status}</div>'

    html_content = f"""<style>
.eco-semaphore-container {{ display: flex; flex-direction: column; gap: 1.5rem; }}
.eco-semaphore-main {{ position: relative; overflow: hidden; padding: 2rem; border-radius: 1.5rem; border: 1px solid {color}40; background: linear-gradient(135deg, var(--secondary-background-color) 0%, {color}15 100%); transition: all 0.3s; }}
.eco-semaphore-main:hover {{ transform: translateY(-3px); box-shadow: 0 15px 30px -10px {color}30; }}
.eco-semaphore-glow {{ position: absolute; top: -50%; right: -20%; width: 300px; height: 300px; background: radial-gradient(circle, {color}40 0%, transparent 70%); filter: blur(40px); pointer-events: none; }}
.eco-semaphore-header {{ display: flex; justify-content: space-between; align-items: flex-start; z-index: 1; position: relative; }}
.eco-semaphore-title-group {{ display: flex; flex-direction: column; gap: 0.25rem; }}
.eco-semaphore-subtitle {{ font-size: 0.875rem; font-weight: 600; color: var(--text-color); opacity: 0.7; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; }}
.eco-semaphore-city {{ font-size: 2rem; font-weight: 800; color: var(--text-color); margin: 0; line-height: 1.2; }}
.eco-semaphore-icon-box {{ width: 4rem; height: 4rem; border-radius: 1rem; background-color: {color}20; color: {color}; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px {color}20; }}
.eco-semaphore-status {{ margin-top: 1.5rem; z-index: 1; position: relative; }}
.eco-semaphore-badge {{ display: inline-flex; align-items: center; padding: 0.5rem 1rem; border-radius: 9999px; background-color: {color}; color: #ffffff; font-weight: 700; font-size: 1.25rem; letter-spacing: 0.025em; text-shadow: 0 1px 2px rgba(0,0,0,0.2); box-shadow: 0 4px 10px {color}40; }}
.eco-legend-container {{ display: flex; flex-direction: column; gap: 0.75rem; padding: 1.5rem; border-radius: 1rem; border: 1px solid var(--border-color); background-color: var(--secondary-background-color); }}
.eco-legend-title {{ font-size: 1rem; font-weight: 700; color: var(--text-color); margin: 0; display: flex; align-items: center; gap: 0.5rem; }}
.eco-legend-grid {{ display: flex; flex-wrap: wrap; gap: 0.75rem; }}
.eco-legend-item {{ display: flex; align-items: center; gap: 0.5rem; padding: 0.35rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; color: var(--text-color); background-color: rgba(128, 128, 128, 0.05); border: 1px solid var(--border-color); transition: all 0.2s; }}
.eco-metrics-grid {{ display: grid; grid-template-columns: 1fr; gap: 1rem; }}
.eco-metric-card {{ padding: 1.25rem; border-radius: 1rem; border: 1px solid var(--border-color); background-color: var(--secondary-background-color); display: flex; flex-direction: column; gap: 0.5rem; }}
.eco-metric-label {{ font-size: 0.75rem; font-weight: 600; color: var(--text-color); opacity: 0.6; text-transform: uppercase; letter-spacing: 0.05em; }}
.eco-metric-value {{ font-size: 1.25rem; font-weight: 700; color: var(--text-color); line-height: 1.2; word-break: break-word; }}
</style>
<div class="eco-semaphore-container">
<div class="eco-semaphore-main">
<div class="eco-semaphore-glow"></div>
<div class="eco-semaphore-header">
<div class="eco-semaphore-title-group">
<p class="eco-semaphore-subtitle">Riesgo Climático en Vivo</p>
<h2 class="eco-semaphore-city">{city_name}</h2>
</div>
<div class="eco-semaphore-icon-box">
<svg style="width: 2.5rem; height: 2.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">{icon_svg}</svg>
</div>
</div>
<div class="eco-semaphore-status">
<span class="eco-semaphore-badge">{state["label"]}</span>
<br>
{consensus_html}
</div>
</div>
<div class="eco-metrics-grid">
<div class="eco-metric-card">
<span class="eco-metric-label">Contaminante Dominante (OMS)</span>
<span class="eco-metric-value">{dominant_pollutant.upper() if dominant_pollutant else "—"}</span>
</div>
</div>
<div class="eco-legend-container">
<h4 class="eco-legend-title">
<svg style="width: 1.25rem; height: 1.25rem; color: #3b82f6;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
Escala de Referencia OMS
</h4>
<div class="eco-legend-grid">"""

    levels = [
        ("good", "Bueno"),
        ("fair", "Aceptable"),
        ("moderate", "Moderado"),
        ("poor", "Malo"),
        ("very_poor", "Muy malo"),
        ("hazardous", "Peligroso"),
    ]

    for key, label in levels:
        lvl_color = RISK_STATES[key]["color"]
        highlight = f"border-color: {lvl_color}; background-color: {lvl_color}15; transform: scale(1.05); box-shadow: 0 0 10px {lvl_color}40;" if key == risk_state else ""
        dot_shadow = f"box-shadow: 0 0 8px {lvl_color};" if key == risk_state else ""
        html_content += f"""<div class="eco-legend-item" style="{highlight}">
<div style="width: 10px; height: 10px; border-radius: 50%; background-color: {lvl_color}; {dot_shadow}"></div>
{label}
</div>"""
        
    html_content += """</div>
</div>
</div>"""

    st.markdown(html_content, unsafe_allow_html=True)
