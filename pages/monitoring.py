# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd

from components.live_risk_semaphore import render_live_risk_semaphore
from components.section_header import render_section_header
from providers.open_meteo_air_quality import fetch_city_snapshot
from providers.openweather_air_quality import fetch_current_air_quality, fetch_current_weather
from config.constants import RISK_STATES
from config.cities import ALL_CITIES
from config.oms_thresholds import safe_threshold_for
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
    
    focus_city = st.sidebar.selectbox("Ciudad:", options=ALL_CITIES, index=ALL_CITIES.index("San José, CR") if "San José, CR" in ALL_CITIES else 0)
    
    with st.spinner("Consultando datos ambientales..."):
        response = fetch_city_snapshot(focus_city, start_date=filters.get("date_from"), end_date=filters.get("date_to"))
        ow_response = fetch_current_air_quality(focus_city)
        weather_response = fetch_current_weather(focus_city)
        
        summary = response.data["summary"]
        
        # Consenso de modelos
        consensus_status = None
        ow_aqi_val = None
        if ow_response.metadata.get("available") and ow_response.data:
            ow_risk = ow_response.data.get("risk_state", "unknown")
            ow_aqi_val = ow_response.data.get("aqi")
            om_risk = summary.get("risk_state", "unknown")
            
            risk_levels = {"good": 1, "fair": 2, "moderate": 3, "poor": 4, "very_poor": 5, "hazardous": 6}
            
            if om_risk in risk_levels and ow_risk in risk_levels:
                diff = abs(risk_levels[om_risk] - risk_levels[ow_risk])
                if diff <= 1:
                    consensus_status = "Alta Confianza"
                else:
                    consensus_status = "Divergente"
                    if risk_levels[ow_risk] > risk_levels[om_risk]:
                        summary["risk_state"] = ow_risk

        current_frame = response.data["current_frame"]
        full_trend_frame = response.data["trend_frame"].copy()
        
        # Separar el histórico del pronóstico (próximas 48h)
        current_time_str = response.raw_payload.get("current", {}).get("time")
        current_time = None
        trend_frame = full_trend_frame.copy()
        forecast_frame = pd.DataFrame()
        
        if current_time_str and not full_trend_frame.empty:
            current_time = pd.to_datetime(current_time_str)
            trend_frame = full_trend_frame[full_trend_frame["timestamp"] <= current_time]
            
            # Forecast frame para las siguientes 48 horas
            forecast_end_time = current_time + pd.Timedelta(hours=48)
            forecast_frame = full_trend_frame[(full_trend_frame["timestamp"] > current_time) & (full_trend_frame["timestamp"] <= forecast_end_time)].copy()

        dominant = summary.get("dominant_pollutant", "").lower()

        # Guardar contexto global para el chat de IA
        st.session_state["current_pollution_context"] = {
            "page_name": "Monitoreo en Vivo",
            "ciudad": focus_city,
            "resumen_estado": summary,
            "datos_contaminantes": current_frame,
            "consenso_modelos": consensus_status,
            "datos_openweather": ow_response.data if ow_response.metadata.get("available") else None,
            "clima_openweather": weather_response.data if weather_response.metadata.get("available") else None
        }

    if current_time_str:
        dt = pd.to_datetime(current_time_str)
        time_formatted = dt.strftime("%d/%m/%Y %H:%M")
        st.markdown(f"<div style='text-align: right; font-size: 0.8rem; color: var(--text-color); opacity: 0.6; margin-top: -1.5rem; margin-bottom: 1rem;'><svg style='width: 1rem; height: 1rem; display: inline-block; vertical-align: text-bottom; margin-right: 0.25rem;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'></path></svg>Última actualización: {time_formatted}</div>", unsafe_allow_html=True)

    # 1. Semáforo y Ubicación
    c1, c2 = st.columns([1.5, 1])
    with c1:
        render_live_risk_semaphore(summary["risk_state"], response.data["location"]["city_name"], summary["dominant_pollutant"], consensus_status)
    with c2:
        st.map(pd.DataFrame({'lat': [response.data["location"]['latitude']], 'lon': [response.data["location"]['longitude']]}))

    # 2. Métricas Clave (KPIs)
    aqi_val = summary.get("european_aqi")
    aqi_str = f"{int(aqi_val)}" if aqi_val is not None else "N/D"
    aqi_subtext = "Calidad de aire global"
    if ow_aqi_val is not None:
        aqi_str = f"{aqi_str} <span style='font-size:1rem;opacity:0.6'>OM</span>"
        aqi_subtext = f"Validado por OW (AQI: {ow_aqi_val})"
    
    sat_val = summary.get("dominant_ratio")
    sat_str = f"{(sat_val * 100):.1f}%" if sat_val is not None else "N/D"
    
    crit_val = summary.get("critical_indicators", 0)
    crit_str = f"{crit_val}"
    crit_color = "#ef4444" if crit_val > 0 else "#10b981"
    
    trend_24_html = '<span style="color: var(--text-color); opacity: 0.7;">N/D</span>'
    if not trend_frame.empty and dominant and dominant in trend_frame.columns:
        df_sorted = trend_frame.sort_values('timestamp')
        latest_time = df_sorted['timestamp'].iloc[-1]
        latest_val = df_sorted[dominant].iloc[-1]
        target_time = latest_time - pd.Timedelta(hours=24)
        closest_idx = (df_sorted['timestamp'] - target_time).abs().idxmin()
        old_val = df_sorted.loc[closest_idx, dominant]
        
        if pd.notna(latest_val) and pd.notna(old_val) and old_val > 0:
            diff_pct = ((latest_val - old_val) / old_val) * 100
            if diff_pct > 0:
                svg_up = '<svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>'
                trend_24_html = f'<span style="color: #ef4444; font-weight: 700; display: flex; align-items: center; gap: 0.25rem;">{svg_up} +{diff_pct:.1f}%</span>'
            elif diff_pct < 0:
                svg_down = '<svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6"></path></svg>'
                trend_24_html = f'<span style="color: #10b981; font-weight: 700; display: flex; align-items: center; gap: 0.25rem;">{svg_down} {diff_pct:.1f}%</span>'
            else:
                svg_flat = '<svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 12h14"></path></svg>'
                trend_24_html = f'<span style="color: var(--text-color); opacity: 0.7; display: flex; align-items: center; gap: 0.25rem;">{svg_flat} 0%</span>'

    kpis_html = f"""
    <style>
    .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1.5rem; margin-bottom: 2rem; }}
    .kpi-card {{ background-color: var(--secondary-background-color); border: 1px solid var(--border-color); border-radius: 1rem; padding: 1.25rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); transition: transform 0.2s; }}
    .kpi-card:hover {{ transform: translateY(-2px); }}
    .kpi-title {{ font-size: 0.75rem; color: var(--text-color); opacity: 0.8; margin-bottom: 0.5rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }}
    .kpi-value {{ font-size: 1.8rem; font-weight: 800; color: var(--text-color); line-height: 1.2; margin-bottom: 0.25rem; }}
    .kpi-subtext {{ font-size: 0.75rem; color: var(--text-color); opacity: 0.7; }}
    </style>
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Índice AQI Europeo</div>
            <div class="kpi-value">{aqi_str}</div>
            <div class="kpi-subtext">{aqi_subtext}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Saturación OMS</div>
            <div class="kpi-value">{sat_str}</div>
            <div class="kpi-subtext">Contaminante dominante</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Alertas Críticas</div>
            <div class="kpi-value" style="color: {crit_color};">{crit_str}</div>
            <div class="kpi-subtext">Indicadores fuera de límite</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Tendencia 24H</div>
            <div class="kpi-value" style="font-size: 1.6rem;">{trend_24_html}</div>
            <div class="kpi-subtext">Respecto a ayer</div>
        </div>
    </div>
    """
    st.markdown(kpis_html, unsafe_allow_html=True)

    if weather_response.metadata.get("available") and weather_response.data:
        w_data = weather_response.data
        temp = w_data.get("temperature", 0)
        hum = w_data.get("humidity", 0)
        wind = w_data.get("wind_speed", 0)
        
        pm_high = False
        if not current_frame.empty:
            pm_data = current_frame[current_frame['pollutant_code'].isin(['pm2_5', 'pm10'])]
            if (pm_data['ratio'] >= 1.0).any():
                pm_high = True
        
        if wind > 4:
            disp_msg = "Buena dispersión de contaminantes"
            disp_color = "#10b981"
            disp_icon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
        elif wind <= 4 and pm_high:
            disp_msg = "Las condiciones de poco viento impiden la dispersión de contaminantes"
            disp_color = "#ef4444"
            disp_icon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>'
        else:
            disp_msg = "Viento en calma (riesgo de estancamiento)"
            disp_color = "#f59e0b"
            disp_icon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>'
            
        svg_temp = '<svg style="width: 1.25rem; height: 1.25rem; margin-right: 0.25rem; color: #ef4444; vertical-align: text-bottom;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18a3 3 0 100-6 3 3 0 000 6z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 12V4a2 2 0 00-4 0v8a4 4 0 108 0V4a2 2 0 00-4 0v8z"></path></svg>'
        svg_hum = '<svg style="width: 1.25rem; height: 1.25rem; margin-right: 0.25rem; color: #3b82f6; vertical-align: text-bottom;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3c.132 0 .263.023.385.068C14.195 3.75 20 9.873 20 15c0 4.418-3.582 8-8 8s-8-3.582-8-8c0-5.127 5.805-11.25 7.615-11.932A.997.997 0 0112 3z"></path></svg>'
        svg_wind = '<svg style="width: 1.25rem; height: 1.25rem; margin-right: 0.25rem; color: #10b981; vertical-align: text-bottom;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.59 4.59A2 2 0 1111 8H2m10.59 11.41A2 2 0 1014 16H2m15.73-8.27A2.5 2.5 0 1119.5 12H2"></path></svg>'
            
        st.markdown(f"""
        <div style="display: flex; gap: 1rem; align-items: center; padding: 1.25rem; border-radius: 1rem; background-color: var(--secondary-background-color); border: 1px solid var(--border-color); margin-bottom: 2rem;">
            <div style="flex-shrink: 0; display: flex; align-items: center; justify-content: center; width: 3rem; height: 3rem; border-radius: 0.75rem; background-color: rgba(59, 130, 246, 0.1); color: #3b82f6;">
                <svg style="width: 1.75rem; height: 1.75rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"></path></svg>
            </div>
            <div style="flex-grow: 1;">
                <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-color); opacity: 0.7; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Condiciones Meteorológicas (OpenWeather)</div>
                <div style="display: flex; gap: 1.5rem; align-items: baseline;">
                    <div style="font-size: 1.25rem; font-weight: 800; color: var(--text-color);">{svg_temp}{temp:.1f}°C</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: var(--text-color);">{svg_hum}{hum}%</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: var(--text-color);">{svg_wind}{wind:.1f} m/s</div>
                </div>
            </div>
            <div style="flex-shrink: 0; display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 9999px; background-color: {disp_color}15; color: {disp_color}; border: 1px solid {disp_color}30; font-weight: 700; font-size: 0.85rem;">
                <svg style="width: 1.25rem; height: 1.25rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24">{disp_icon}</svg>
                {disp_msg}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Diagnóstico Visual Directo
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
        key = str(row["pollutant_code"]).lower().strip()
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
    
    st.write("---")
    
    # Evaluar alertas del pronóstico
    critical_forecasts = []
    if not forecast_frame.empty:
        pollutants_to_check = [col for col in forecast_frame.columns if col not in ['timestamp', 'european_aqi']]
        for idx, row in forecast_frame.iterrows():
            for p in pollutants_to_check:
                val = row[p]
                if pd.notna(val):
                    threshold = safe_threshold_for(p)
                    if threshold and val > threshold:
                        critical_forecasts.append({"timestamp": row["timestamp"], "pollutant": p, "val": val})

    # Mostrar tarjeta de recomendación preventiva si hay alertas en el futuro cercano
    if critical_forecasts:
        first_alert = critical_forecasts[0]
        alert_time = first_alert["timestamp"]
        p_name = GUIA_SALUD.get(first_alert["pollutant"].lower(), {}).get("nombre", first_alert["pollutant"].upper())
        st.markdown(f"""
        <div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 0.5rem; color: #d97706; font-weight: 700; margin-bottom: 0.25rem;">
                <svg style="width: 1.25rem; height: 1.25rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                Alerta Preventiva (Pronóstico a 48h)
            </div>
            <p style="color: #92400e; margin: 0; font-size: 0.9rem;">
                Se proyecta que los niveles de <strong>{p_name}</strong> superarán los límites seguros de la OMS 
                alrededor del <strong>{alert_time.strftime('%d/%m/%Y a las %H:%M')}</strong>. 
                Sugerimos planificar tus actividades al aire libre y tomar medidas precautorias.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    # 4. Evolución Histórica y Predictiva
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 3rem; margin-bottom: 1.5rem;">
        <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; background-color: rgba(59, 130, 246, 0.1); display: flex; align-items: center; justify-content: center; color: #3b82f6;">
            <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>
        </div>
        <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--text-color);">Evolución Histórica de Contaminantes</h3>
    </div>
    <p style="color: var(--text-color); opacity: 0.8; margin-top: -1rem; margin-bottom: 1.5rem;">Visualiza el impacto de la contaminación a lo largo del tiempo. Identifica picos y patrones de todos los contaminantes registrados.</p>
    """, unsafe_allow_html=True)
    
    if not trend_frame.empty or not forecast_frame.empty:
        pollutants_to_plot = [col for col in trend_frame.columns if col not in ['timestamp', 'european_aqi']]
        colors = px.colors.qualitative.Plotly
        fig = go.Figure()

        for i, p in enumerate(pollutants_to_plot):
            p_name = GUIA_SALUD.get(p.lower(), {}).get("nombre", p.upper())
            color = colors[i % len(colors)]
            
            # Línea Histórica
            hist_df = trend_frame.dropna(subset=[p])
            if not hist_df.empty:
                fig.add_trace(go.Scatter(
                    x=hist_df["timestamp"], y=hist_df[p], mode='lines',
                    name=p_name, line=dict(color=color, width=2.5, shape='spline'),
                    legendgroup=p_name
                ))
            
            # Línea de Pronóstico y Banda de Confianza
            if not forecast_frame.empty:
                fore_df = forecast_frame.dropna(subset=[p]).copy()
                if not fore_df.empty:
                    # Conectar historial con forecast
                    if not hist_df.empty:
                        last_hist = hist_df.iloc[-1:]
                        fore_df = pd.concat([last_hist, fore_df])
                    
                    # Línea principal (Punteada)
                    fig.add_trace(go.Scatter(
                        x=fore_df["timestamp"], y=fore_df[p], mode='lines',
                        name=f"{p_name} (Pronóstico)", line=dict(color=color, width=2.5, dash='dot', shape='spline'),
                        legendgroup=p_name, showlegend=False
                    ))
                    
                    # Intervalo de confianza (Aumenta hasta 20% a las 48h)
                    if current_time:
                        hours_diff = (fore_df["timestamp"] - current_time).dt.total_seconds() / 3600
                        error_margin = fore_df[p] * (hours_diff / 48) * 0.20
                    else:
                        error_margin = fore_df[p] * 0.1
                        
                    upper_bound = fore_df[p] + error_margin
                    lower_bound = fore_df[p] - error_margin
                    
                    # Relleno del intervalo
                    fill_color = color.replace('rgb', 'rgba').replace(')', ', 0.15)') if 'rgb' in color else 'rgba(128,128,128,0.2)'
                    fig.add_trace(go.Scatter(
                        x=fore_df["timestamp"], y=upper_bound, mode='lines', line=dict(width=0),
                        showlegend=False, legendgroup=p_name, hoverinfo='skip'
                    ))
                    fig.add_trace(go.Scatter(
                        x=fore_df["timestamp"], y=lower_bound, mode='lines', line=dict(width=0),
                        fill='tonexty', fillcolor=fill_color,
                        showlegend=False, legendgroup=p_name, hoverinfo='skip'
                    ))

        # Áreas de riesgo (Picos críticos proyectados)
        if critical_forecasts:
            critical_times = sorted(list(set([c["timestamp"] for c in critical_forecasts])))
            if critical_times:
                blocks, start, prev = [], critical_times[0], critical_times[0]
                for t in critical_times[1:]:
                    if (t - prev) <= pd.Timedelta(hours=1):
                        prev = t
                    else:
                        blocks.append((start, prev))
                        start, prev = t, t
                blocks.append((start, prev))
                
                for b_start, b_end in blocks:
                    fig.add_vrect(
                        x0=b_start, x1=b_end + pd.Timedelta(hours=1),
                        fillcolor="red", opacity=0.1, layer="below", line_width=0,
                        annotation_text="Peligro OMS", annotation_position="top left",
                        annotation_font_color="red", annotation_font_size=10
                    )

        # Línea divisoria de tiempo actual ("AHORA") vs "PRONÓSTICO"
        if current_time:
            fig.add_vline(x=current_time, line_width=2, line_dash="dash", line_color="rgba(156, 163, 175, 0.5)")
            fig.add_annotation(
                x=current_time,
                y=1.02,
                yref="paper",
                text="AHORA",
                showarrow=False,
                font=dict(size=10, color="rgba(156, 163, 175, 0.8)", weight="bold"),
                xanchor="right",
                xshift=-5
            )
            fig.add_annotation(
                x=current_time,
                y=1.02,
                yref="paper",
                text="PRONÓSTICO (48h)",
                showarrow=False,
                font=dict(size=10, color="#3b82f6", weight="bold"),
                xanchor="left",
                xshift=5
            )

        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5, title=None),
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="",
            yaxis_title="Concentración (µg/m³)"
        )
        # Ocultar CO por defecto
        fig.for_each_trace(lambda t: t.update(visible='legendonly') if t.name and 'Monóxido de Carbono' in t.name else ())
        
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    else:
        st.info("No hay datos históricos disponibles para mostrar la evolución.")
    
if __name__ == "__main__":
    render(get_runtime_filters())