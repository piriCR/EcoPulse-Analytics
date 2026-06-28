import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
import streamlit as st

from components.section_header import render_section_header
from config.constants import DEFAULT_CITIES, RISK_STATES, PRIMARY_POLLUTANTS
from providers.open_meteo_air_quality import fetch_city_snapshot
from utils.page_context import get_runtime_filters

def render(filters: dict) -> None:
    render_section_header("Análisis Comparativo de Calidad del Aire", "Módulo de visualización intuitiva para la gestión ambiental.")
    st.caption("Selecciona las ciudades y compara su impacto ambiental mediante indicadores simplificados y mapas geográficos.")

    # --- Sidebar ---
    st.sidebar.header("Configuración")
    selected_cities = st.sidebar.multiselect(
        "Ciudades a comparar",
        options=DEFAULT_CITIES,
        default=DEFAULT_CITIES[:4],
        help="Selecciona hasta 5 ciudades para obtener una comparativa clara."
    )

    if not selected_cities:
        st.warning("Por favor, selecciona al menos una ciudad para iniciar el análisis.")
        return

    # --- Carga de datos ---
    date_from, date_to = filters.get("date_from"), filters.get("date_to")
    date_from_str, date_to_str = (d.isoformat() if hasattr(d, "isoformat") else None for d in [date_from, date_to])

    city_data_list, errors = [], []
    with st.spinner("Analizando calidad del aire en tiempo real..."):
        for city_key in selected_cities:
            try:
                response = fetch_city_snapshot(city_key, start_date=date_from_str, end_date=date_to_str)
                summary, location, current_frame = response.data["summary"], response.data["location"], response.data["current_frame"]
                
                pollutants_dict = {row["pollutant_name"]: row["value"] for _, row in current_frame.iterrows()} if not current_frame.empty else {}
                
                critical_pollutants = []
                if not current_frame.empty:
                    critical_pollutants = current_frame[current_frame["risk_state"].isin(["poor", "very_poor", "hazardous"])].to_dict('records')
                
                city_data_list.append({
                    "city_name": location["city_name"], "country_code": location["country_code"],
                    "lat": location["latitude"], "lon": location["longitude"],
                    "AQI": pd.to_numeric(summary.get("european_aqi", 0), errors="coerce"),
                    "Riesgo": RISK_STATES.get(summary.get("risk_state", "unknown"), RISK_STATES["unknown"])["label"],
                    "Dominante": summary.get("dominant_pollutant", "—"),
                    "Severidad": pd.to_numeric(summary.get("dominant_ratio", 0), errors="coerce"),
                    "critical_pollutants": critical_pollutants,
                    **pollutants_dict
                })
            except Exception as exc: errors.append(f"{city_key}: {exc}")

    if not city_data_list:
        st.error("Error al obtener datos.")
        return

    frame = pd.DataFrame(city_data_list).fillna(0)

    # --- Tabs de Visualización ---
    tab1, tab2, tab3, tab4 = st.tabs(["Gráficas", "Mapa", "Reporte Detallado", "Alertas OMS"])

    with tab1:
        st.markdown("""<div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem; margin-bottom: 1.5rem;">
    <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; background-color: rgba(59, 130, 246, 0.1); display: flex; align-items: center; justify-content: center; color: #3b82f6;">
        <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
    </div>
    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--text-color);">Comparativa de Indicadores</h3>
</div>""", unsafe_allow_html=True)
        available_metrics = ["AQI", "Severidad"] + [p for p in PRIMARY_POLLUTANTS if p in frame.columns]
        
        # Mapeo para nombres amigables
        metric_labels = {"AQI": "Calidad del Aire (AQI)", "Severidad": "Índice de Toxicidad", "pm2_5": "Partículas PM2.5", "pm10": "Partículas PM10"}
        
        compare_metric = st.selectbox("Indicador a analizar", options=available_metrics, format_func=lambda x: metric_labels.get(x, x))
        
        plot_frame = frame.sort_values(by=compare_metric, ascending=False)
        chart = px.bar(plot_frame, x="city_name", y=compare_metric, color="Riesgo",
                       color_discrete_map={state["label"]: state["color"] for state in RISK_STATES.values()},
                       text_auto='.1f', labels={"city_name": "Ciudad", compare_metric: metric_labels.get(compare_metric, compare_metric)})
        
        chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(chart, use_container_width=True)

    with tab2:
        st.markdown("""<div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem; margin-bottom: 1.5rem;">
    <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; background-color: rgba(16, 185, 129, 0.1); display: flex; align-items: center; justify-content: center; color: #10b981;">
        <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
    </div>
    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--text-color);">Ubicación Geográfica</h3>
</div>""", unsafe_allow_html=True)
        map_fig = px.density_mapbox(frame, lat="lat", lon="lon", z="AQI", radius=50, center=dict(lat=frame["lat"].mean(), lon=frame["lon"].mean()), zoom=3.5,
                                   hover_name="city_name", color_continuous_scale="Turbo")
        map_fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(map_fig, use_container_width=True)

    with tab3:
        st.markdown("""<div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem; margin-bottom: 1.5rem;">
    <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; background-color: rgba(168, 85, 247, 0.1); display: flex; align-items: center; justify-content: center; color: #a855f7;">
        <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
    </div>
    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--text-color);">Ficha Técnica por Ciudad</h3>
</div>
<style>
.eco-city-card { padding: 1.5rem; border: 1px solid var(--border-color); border-radius: 1rem; background-color: var(--secondary-background-color); margin-bottom: 1.25rem; position: relative; overflow: hidden; transition: all 0.3s; display: flex; flex-direction: column; gap: 1rem; }
.eco-city-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
.eco-city-indicator { position: absolute; left: 0; top: 0; bottom: 0; width: 6px; }
.eco-city-header { display: flex; justify-content: space-between; align-items: flex-start; padding-left: 0.5rem; }
.eco-city-title { font-size: 1.5rem; font-weight: 700; color: var(--text-color); margin: 0; display: flex; align-items: baseline; gap: 0.5rem; }
.eco-city-code { font-size: 0.875rem; color: var(--text-color); opacity: 0.5; font-weight: 600; }
.eco-city-risk-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.eco-city-metrics { display: flex; gap: 2rem; padding-left: 0.5rem; }
.eco-city-metric { display: flex; flex-direction: column; gap: 0.25rem; }
.eco-city-metric-label { font-size: 0.75rem; font-weight: 600; color: var(--text-color); opacity: 0.6; text-transform: uppercase; letter-spacing: 0.05em; }
.eco-city-metric-value { font-size: 1.5rem; font-weight: 700; color: var(--text-color); line-height: 1; }
</style>
<div class="eco-city-grid">""", unsafe_allow_html=True)
        for _, row in frame.iterrows():
            risk_color = next((s["color"] for s in RISK_STATES.values() if s["label"] == row["Riesgo"]), "gray")
            
            st.markdown(f"""<div class="eco-city-card">
    <div class="eco-city-indicator" style="background-color: {risk_color};"></div>
    <div class="eco-city-header">
        <h3 class="eco-city-title">{row['city_name']} <span class="eco-city-code">{row['country_code']}</span></h3>
        <span class="eco-city-risk-badge" style="background-color: {risk_color}20; color: {risk_color}; border: 1px solid {risk_color}40;">{row['Riesgo']}</span>
    </div>
    <div class="eco-city-metrics">
        <div class="eco-city-metric">
            <span class="eco-city-metric-label">Calidad del Aire (AQI)</span>
            <span class="eco-city-metric-value">{row['AQI']:.1f}</span>
        </div>
        <div class="eco-city-metric">
            <span class="eco-city-metric-label">Contaminante Principal</span>
            <span class="eco-city-metric-value">{row['Dominante']}</span>
        </div>
    </div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown("""
        <style>
        .oms-alerts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.25rem; margin-top: 1rem; }
        .oms-alert-card { padding: 1.5rem; border: 1px solid #f3f4f6; border-radius: 1rem; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05); background-color: #ffffff; position: relative; overflow: hidden; transition: all 0.3s; }
        .oms-alert-card:hover { box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); }
        .oms-alert-indicator { position: absolute; top: 0; left: 0; width: 6px; height: 100%; }
        .oms-alert-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; padding-left: 0.5rem; }
        .oms-alert-title { font-size: 1.25rem; font-weight: 700; color: #1f2937; margin: 0; line-height: 1.2; }
        .oms-alert-subtitle { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }
        .oms-alert-icon-container { padding: 0.5rem; border-radius: 9999px; background-color: #f9fafb; color: #9ca3af; }
        .oms-alert-icon { width: 1.25rem; height: 1.25rem; }
        .oms-pollutants-container { display: flex; flex-wrap: wrap; gap: 0.5rem; padding-left: 0.5rem; }
        .oms-pollutant-badge { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.375rem 0.75rem; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 600; background-color: #fef2f2; color: #b91c1c; border: 1px solid #fee2e2; }
        .oms-pollutant-icon { width: 1rem; height: 1rem; opacity: 0.7; }
        .oms-header-icon { width: 1.75rem; height: 1.75rem; color: #ef4444; }
        .oms-success-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; text-align: center; background-color: #f0fdf4; border: 1px solid #dcfce3; border-radius: 1rem; }
        .oms-success-icon-bg { width: 4rem; height: 4rem; background-color: #dcfce3; border-radius: 9999px; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; color: #22c55e; }
        .oms-success-icon { width: 2rem; height: 2rem; }
        </style>
        
        <div style="margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.5rem; font-weight: 700; color: #1f2937; display: flex; align-items: center; gap: 0.5rem; margin: 0;">
                <svg class="oms-header-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                Evaluación Sanitaria OMS
            </h2>
            <p style="color: #6b7280; font-size: 0.875rem; margin-top: 0.25rem;">Análisis de contaminantes críticos que exceden los límites de seguridad recomendados.</p>
        </div>
        """, unsafe_allow_html=True)
        
        alerts_list = []
        for _, row in frame.iterrows():
            crits = row.get("critical_pollutants", [])
            if crits:
                alerts_list.append({
                    "Ciudad": row['city_name'],
                    "Estado": row['Riesgo'],
                    "Indicadores críticos": len(crits),
                    "Contaminantes": ", ".join([str(c["pollutant_name"]).upper() for c in crits]),
                    "crits_data": crits,
                    "color": next((s["color"] for s in RISK_STATES.values() if s["label"] == row['Riesgo']), "#757575")
                })
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Ciudades Evaluadas", len(frame))
        col2.metric("Alertas Activas", len(alerts_list))
        col3.metric("Ciudades Seguras", len(frame) - len(alerts_list))
        
        st.markdown("---")
        
        if not alerts_list:
            st.markdown("""
<div class="oms-success-container">
    <div class="oms-success-icon-bg">
        <svg class="oms-success-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
    </div>
    <h3 style="font-size: 1.125rem; font-weight: 700; color: #166534; margin: 0 0 0.25rem 0;">¡Todo en orden!</h3>
    <p style="color: #15803d; font-size: 0.875rem; margin: 0;">Ninguna de las ciudades comparadas excede los límites críticos de la OMS.</p>
</div>
            """, unsafe_allow_html=True)
        else:
            alerts_html = '<div class="oms-alerts-grid">'
            for alert in alerts_list:
                pollutants_html = "".join([
                    f'<span class="oms-pollutant-badge">'
                    f'<svg class="oms-pollutant-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>'
                    f'{str(c["pollutant_name"]).upper()}: {c["value"]} {c["unit"]}</span>'
                    for c in alert["crits_data"]
                ])
                
                alerts_html += f"""
<div class="oms-alert-card">
    <div class="oms-alert-indicator" style="background-color: {alert['color']};"></div>
    <div class="oms-alert-header">
        <div>
            <h4 class="oms-alert-title">{alert['Ciudad']}</h4>
            <div class="oms-alert-subtitle" style="color: {alert['color']};">{alert['Estado']}</div>
        </div>
        <div class="oms-alert-icon-container">
            <svg class="oms-alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
        </div>
    </div>
    <div class="oms-pollutants-container">
        {pollutants_html}
    </div>
</div>"""
            alerts_html += '</div>'
            st.markdown(alerts_html, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""<div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 1.5rem; margin-bottom: 0.5rem;">
    <svg style="width: 1.5rem; height: 1.5rem; color: #f59e0b;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: var(--text-color);">Ranking de Riesgo Ambiental</h3>
</div>""", unsafe_allow_html=True)
            alerts_df = pd.DataFrame(alerts_list)
            alerts_df = alerts_df.sort_values(by="Indicadores críticos", ascending=False)
            
            chart_alerts = px.bar(
                alerts_df,
                x="Indicadores críticos",
                y="Ciudad",
                color="Estado",
                orientation="h",
                text="Indicadores críticos",
                color_discrete_map={state["label"]: state["color"] for state in RISK_STATES.values()}
            )
            chart_alerts.update_layout(height=400, yaxis_title="Ciudad", xaxis_title="Contaminantes fuera de norma OMS", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(chart_alerts, use_container_width=True)
            
            st.markdown("""<div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 2rem; margin-bottom: 0.5rem;">
    <svg style="width: 1.5rem; height: 1.5rem; color: #ef4444;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: var(--text-color);">Huella de Toxicidad (Contaminantes Críticos)</h3>
</div>""", unsafe_allow_html=True)
            radar_data = []
            for alert in alerts_list:
                for c in alert["crits_data"]:
                    radar_data.append({
                        "Ciudad": alert["Ciudad"],
                        "Contaminante": str(c["pollutant_name"]).upper(),
                        "Valor": c["value"]
                    })
            if radar_data:
                radar_df = pd.DataFrame(radar_data)
                chart_radar = px.line_polar(
                    radar_df,
                    r="Valor",
                    theta="Contaminante",
                    color="Ciudad",
                    line_close=True,
                    markers=True,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                chart_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, showticklabels=False)
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=40, r=40, t=20, b=20),
                )
                st.plotly_chart(chart_radar, use_container_width=True)

    st.session_state["current_pollution_context"] = {
        "page_name": "Ciudad Comparativa",
        "ciudades_seleccionadas": selected_cities,
        "datos_comparativos": frame.drop(columns=['critical_pollutants']) if 'critical_pollutants' in frame.columns else frame,
        "alertas_oms_activas": bool(alerts_list)
    }

if __name__ == "__main__":
    render(get_runtime_filters())