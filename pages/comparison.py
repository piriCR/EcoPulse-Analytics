import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
import streamlit as st

from components.section_header import render_section_header
from config.constants import RISK_STATES, PRIMARY_POLLUTANTS, COMPARISON_DEFAULT_CITIES
from config.cities import ALL_CITIES
from providers.open_meteo_air_quality import fetch_city_snapshot
from providers.openweather_air_quality import fetch_current_weather
from utils.page_context import get_runtime_filters

def render(filters: dict) -> None:
    render_section_header("Análisis Comparativo de Calidad del Aire", "Módulo de visualización intuitiva para la gestión ambiental.")
    st.caption("Selecciona las ciudades y compara su impacto ambiental mediante indicadores simplificados y mapas geográficos.")

    # --- Sidebar ---
    st.sidebar.header("Configuración")
    selected_cities = st.sidebar.multiselect(
        "Ciudades a comparar",
        options=ALL_CITIES,
        default=COMPARISON_DEFAULT_CITIES,
        help="Selecciona hasta 8 ciudades para obtener una comparativa clara."
    )

    if not selected_cities:
        st.warning("Por favor, selecciona al menos una ciudad para iniciar el análisis.")
        return

    # --- Carga de datos ---
    date_from, date_to = filters.get("date_from"), filters.get("date_to")
    date_from_str, date_to_str = (d.isoformat() if hasattr(d, "isoformat") else None for d in [date_from, date_to])

    city_data_list, errors = [], []
    with st.container(): # Reemplazado st.spinner para evitar el reseteo de los tabs (DOM refresh issue)
        for city_key in selected_cities:
            try:
                response = fetch_city_snapshot(city_key, start_date=date_from_str, end_date=date_to_str)
                weather_res = fetch_current_weather(city_key)
                
                temp, hum, wind = None, None, None
                if weather_res.metadata.get("available") and weather_res.data:
                    temp = weather_res.data.get("temperature")
                    hum = weather_res.data.get("humidity")
                    wind = weather_res.data.get("wind_speed")
                    
                summary, location, current_frame = response.data["summary"], response.data["location"], response.data["current_frame"]
                trend_frame = response.data.get("trend_frame")
                
                # Dynamic aggregation based on date filter
                if trend_frame is not None and not trend_frame.empty:
                    numeric_means = trend_frame.select_dtypes(include='number').mean().to_dict()
                    from providers.normalization import build_current_frame, summarize_current_frame
                    current_frame = build_current_frame(numeric_means)
                    new_summary = summarize_current_frame(current_frame)
                    new_summary["european_aqi"] = numeric_means.get("european_aqi", summary.get("european_aqi"))
                    # Maintain static city info in summary
                    for k in ["city_key", "city_name", "country_code", "region_name"]:
                        if k in summary:
                            new_summary[k] = summary[k]
                    summary = new_summary

                pollutants_dict = {row["pollutant_name"]: row["value"] for _, row in current_frame.iterrows()} if not current_frame.empty else {}
                codes_dict = {str(row["pollutant_code"]).lower().strip(): row["value"] for _, row in current_frame.iterrows()} if not current_frame.empty else {}
                
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
                    "temp": temp, "hum": hum, "wind": wind,
                    **pollutants_dict,
                    **codes_dict
                })
            except Exception as exc: errors.append(f"{city_key}: {exc}")

    if not city_data_list:
        st.error("Error al obtener datos.")
        return

    frame = pd.DataFrame(city_data_list).fillna(0)
    if not frame.empty and "AQI" in frame.columns:
        frame = frame.sort_values(by="AQI", ascending=False).reset_index(drop=True)

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

    # --- Tabs de Visualización ---
    tab1, tab2, tab3 = st.tabs(["Análisis", "Mapa", "Reporte Detallado"])

    with tab1:
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
            
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 3rem 0;'>", unsafe_allow_html=True)
        st.markdown("""<div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem; margin-bottom: 1.5rem;">
    <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; background-color: rgba(59, 130, 246, 0.1); display: flex; align-items: center; justify-content: center; color: #3b82f6;">
        <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
    </div>
    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--text-color);">Panel Analítico Comparativo</h3>
</div>
<p style="color: var(--text-color); opacity: 0.8; margin-bottom: 2rem;">Explora los datos ambientales a través de múltiples dimensiones visuales para un análisis profundo y comparativo.</p>
""", unsafe_allow_html=True)
        
        # 1. Heatmap (Top full width)
        st.markdown("""<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <svg style="width: 1.25rem; height: 1.25rem; color: #f59e0b;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
            <h4 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: var(--text-color);">Mapa de Calor (Ciudades vs Contaminantes)</h4>
        </div>""", unsafe_allow_html=True)
        st.caption("Visualiza rápidamente qué contaminantes son más problemáticos en qué ciudades (valores normalizados del 0 al 100%).")
        
        # Filtrar solo contaminantes que tengan algún valor real reportado (>0)
        heat_cols = [p for p in PRIMARY_POLLUTANTS if p in frame.columns and frame[p].fillna(0).max() > 0]
        if heat_cols:
            heat_df = frame.set_index("city_name")[heat_cols]
            heat_df_norm = heat_df.apply(lambda x: (x / x.max() * 100).fillna(0) if x.max() > 0 else x)
            fig_heat = px.imshow(heat_df_norm, text_auto=".0f", aspect="auto", 
                                 color_continuous_scale=["#1e293b", "#3b82f6", "#8b5cf6", "#f43f5e"], 
                                 labels=dict(x="Contaminante", y="Ciudad", color="Severidad Relativa (%)"))
            fig_heat.update_xaxes(showgrid=False, zeroline=False)
            fig_heat.update_yaxes(showgrid=False, zeroline=False)
            fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=80, r=20))
            st.plotly_chart(fig_heat, use_container_width=True, theme=None)
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)

        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("""<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <svg style="width: 1.25rem; height: 1.25rem; color: #10b981;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                <h4 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: var(--text-color);">Perfil Ambiental General</h4>
            </div>""", unsafe_allow_html=True)
            st.caption("Compara la 'huella' de todos los gases combinados.")
            radar_all_data = []
            for _, row in frame.iterrows():
                for p in heat_cols:
                    if pd.notna(row.get(p)):
                        radar_all_data.append({
                            "Ciudad": row["city_name"], "Contaminante": str(p).upper(), "Valor": float(row[p])
                        })
            if radar_all_data:
                radar_all_df = pd.DataFrame(radar_all_data)
                radar_all_df['Valor_Norm'] = radar_all_df.groupby('Contaminante')['Valor'].transform(lambda x: (x / x.max()) * 100 if x.max() > 0 else 0)
                chart_radar_all = px.line_polar(radar_all_df, r="Valor_Norm", theta="Contaminante", color="Ciudad", line_close=True, markers=True, color_discrete_sequence=px.colors.qualitative.Set3)
                chart_radar_all.update_traces(fill='toself', opacity=0.5)
                chart_radar_all.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor="rgba(0,0,0,0)"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=40, r=40), legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
                st.plotly_chart(chart_radar_all, use_container_width=True, theme=None)

        with col_right:
            st.markdown("""<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <svg style="width: 1.25rem; height: 1.25rem; color: #ef4444;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                <h4 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: var(--text-color);">Distribución de Criticidad</h4>
            </div>""", unsafe_allow_html=True)
            st.caption("Distribución del peso exclusivo de gases que exceden límites OMS.")
            
            if alerts_list:
                sunburst_data = []
                for alert in alerts_list:
                    for c in alert["crits_data"]:
                        sunburst_data.append({"Ciudad": alert["Ciudad"], "Contaminante": f"{str(c['pollutant_name']).upper()}", "Valor": float(c["value"])})
                
                sunburst_df = pd.DataFrame(sunburst_data)
                sunburst_df['Peso'] = sunburst_df.groupby('Contaminante')['Valor'].transform(lambda x: (x / x.max()) * 100 if x.max() > 0 else 0)
                chart_sunburst_new = px.sunburst(sunburst_df, path=['Ciudad', 'Contaminante'], values='Peso', color='Ciudad', color_discrete_sequence=px.colors.qualitative.Pastel)
                chart_sunburst_new.update_traces(textinfo="label+percent parent", marker=dict(line=dict(color='rgba(255,255,255,0.1)', width=1)))
                chart_sunburst_new.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(chart_sunburst_new, use_container_width=True, theme=None)
            else:
                st.success("Sin alertas críticas activas.")

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)

        # 5. Análisis Dinámico y Correlación Climática
        st.markdown("""<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <svg style="width: 1.25rem; height: 1.25rem; color: #3b82f6;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
            <h4 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: var(--text-color);">Análisis Dinámico y Dispersión Climática</h4>
        </div>""", unsafe_allow_html=True)
        st.caption("Selecciona un indicador. Ambos gráficos inferiores se actualizarán automáticamente para mostrar variaciones y correlaciones con el clima (OpenWeather).")
        
        available_metrics = ["AQI", "Severidad"] + [p for p in PRIMARY_POLLUTANTS if p in frame.columns]
        metric_labels = {"AQI": "Calidad del Aire (AQI)", "Severidad": "Índice de Severidad", "pm2_5": "Partículas PM2.5", "pm10": "Partículas PM10"}
        compare_metric = st.selectbox("Indicador Dinámico a Analizar", options=available_metrics, format_func=lambda x: metric_labels.get(x, x), key="metric_select_tab1")
        
        plot_frame = frame.sort_values(by=compare_metric, ascending=False)
        
        col_bar, col_scatter = st.columns(2)
        
        with col_bar:
            st.markdown(f"**Comparativa Base: {metric_labels.get(compare_metric, compare_metric)}**")
            chart_bar = px.bar(plot_frame, x="city_name", y=compare_metric, color="Riesgo",
                           color_discrete_map={state["label"]: state["color"] for state in RISK_STATES.values()},
                           text_auto='.1f', labels={"city_name": "Ciudad", compare_metric: metric_labels.get(compare_metric, compare_metric)})
            chart_bar.update_layout(xaxis={'categoryorder': 'total descending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20))
            st.plotly_chart(chart_bar, use_container_width=True, theme=None)

        with col_scatter:
            st.markdown(f"**Correlación: {metric_labels.get(compare_metric, compare_metric)} vs Temperatura (OW)**")
            if 'temp' in plot_frame.columns and not plot_frame['temp'].isna().all():
                chart_scatter = px.scatter(
                    plot_frame, 
                    x=compare_metric, 
                    y="temp", 
                    color="Riesgo",
                    size="AQI",
                    hover_name="city_name",
                    color_discrete_map={state["label"]: state["color"] for state in RISK_STATES.values()},
                    labels={"temp": "Temperatura (°C)", compare_metric: metric_labels.get(compare_metric, compare_metric), "AQI": "AQI General"},
                    size_max=25
                )
                chart_scatter.update_traces(marker=dict(line=dict(width=1, color='rgba(255,255,255,0.5)')))
                chart_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20))
                st.plotly_chart(chart_scatter, use_container_width=True, theme=None)
            else:
                st.info("Datos de temperatura de OpenWeather no disponibles en este momento.")

    with tab2:
        st.markdown("""<div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem; margin-bottom: 1.5rem;">
    <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; background-color: rgba(16, 185, 129, 0.1); display: flex; align-items: center; justify-content: center; color: #10b981;">
        <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
    </div>
    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--text-color);">Ubicación Geográfica</h3>
</div>""", unsafe_allow_html=True)
        lat_diff = frame["lat"].max() - frame["lat"].min()
        lon_diff = frame["lon"].max() - frame["lon"].min()
        max_diff = max(lat_diff, lon_diff) if not frame.empty else 0
        
        if max_diff == 0: zoom_level = 10
        elif max_diff < 2: zoom_level = 7
        elif max_diff < 5: zoom_level = 6
        elif max_diff < 20: zoom_level = 4
        else: zoom_level = 2.5

        map_fig = px.scatter_mapbox(
            frame, lat="lat", lon="lon", color="AQI", text="city_name",
            center=dict(lat=frame["lat"].mean(), lon=frame["lon"].mean()), zoom=zoom_level,
            hover_name="city_name", hover_data={"lat": False, "lon": False, "AQI": True},
            color_continuous_scale=[
                [0.0, "#2E7D32"],  # Good (0-20)
                [0.2, "#C0CA33"],  # Fair (20-40)
                [0.4, "#FB8C00"],  # Moderate (40-60)
                [0.6, "#E53935"],  # Poor (60-80)
                [0.8, "#8E24AA"],  # Very Poor (80-100)
                [1.0, "#4A148C"]   # Hazardous (100+)
            ],
            range_color=[0, 100]
        )
        map_fig.update_traces(
            marker=dict(size=16, opacity=1.0),
            textposition='top center',
            textfont=dict(color='white', size=13, weight='bold')
        )
        
        # Efecto de Aura / Glow (Magia UI)
        import copy
        glow = copy.deepcopy(map_fig.data[0])
        glow.marker.size = 45
        glow.marker.opacity = 0.2
        glow.text = None  # Remove text from aura to avoid overlapping/blurring
        glow.hoverinfo = 'skip'
        glow.hovertemplate = None
        map_fig.add_trace(glow)
        
        map_fig.update_layout(
            mapbox_style="carto-darkmatter", 
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        
        st.markdown('<div style="border-radius: 1rem; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5), 0 10px 10px -5px rgba(0,0,0,0.2); background-color: #111;">', unsafe_allow_html=True)
        st.plotly_chart(map_fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("""<div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem; margin-bottom: 0.5rem;">
    <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; background-color: rgba(168, 85, 247, 0.1); display: flex; align-items: center; justify-content: center; color: #a855f7;">
        <svg style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
    </div>
    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--text-color);">Fichas Técnicas (Ranking: Peor a Mejor)</h3>
</div>
<p style="color: var(--text-color); opacity: 0.8; margin-bottom: 1.5rem;">Las siguientes fichas detallan el estado de cada ciudad, ordenadas de mayor a menor riesgo ambiental (comenzando por las de peor calidad del aire).</p>
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
.eco-city-pollutants { display: grid; grid-template-columns: repeat(auto-fit, minmax(60px, 1fr)); gap: 0.75rem; padding-left: 0.5rem; border-top: 1px dashed var(--border-color); padding-top: 1rem; }
.eco-pollutant-box { display: flex; flex-direction: column; gap: 0.15rem; }
.eco-pollutant-name { font-size: 0.65rem; font-weight: 700; color: var(--text-color); opacity: 0.7; text-transform: uppercase; letter-spacing: 0.05em; }
.eco-pollutant-val { font-size: 1.1rem; font-weight: 700; color: var(--text-color); }
</style>
<div class="eco-city-grid">""", unsafe_allow_html=True)
        svg_temp = '<svg style="width: 1.1rem; height: 1.1rem; color: #ef4444;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18a3 3 0 100-6 3 3 0 000 6z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 12V4a2 2 0 00-4 0v8a4 4 0 108 0V4a2 2 0 00-4 0v8z"></path></svg>'
        svg_hum = '<svg style="width: 1.1rem; height: 1.1rem; color: #3b82f6;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3c.132 0 .263.023.385.068C14.195 3.75 20 9.873 20 15c0 4.418-3.582 8-8 8s-8-3.582-8-8c0-5.127 5.805-11.25 7.615-11.932A.997.997 0 0112 3z"></path></svg>'
        svg_wind = '<svg style="width: 1.1rem; height: 1.1rem; color: #10b981;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.59 4.59A2 2 0 1111 8H2m10.59 11.41A2 2 0 1014 16H2m15.73-8.27A2.5 2.5 0 1119.5 12H2"></path></svg>'
        
        # Opciones de exportación
        columns_to_keep = ['city_name', 'country_code', 'lat', 'lon', 'AQI', 'Riesgo', 'Dominante', 'Severidad', 'temp', 'hum', 'wind']
        columns_to_keep += [p for p in PRIMARY_POLLUTANTS if p in frame.columns]
        
        # Filtramos para no tener información duplicada (pollutants_dict vs codes_dict)
        report_df = frame[[c for c in columns_to_keep if c in frame.columns]].copy()
        
        # Renombramos para mejor lectura
        report_df = report_df.rename(columns={
            'city_name': 'Ciudad',
            'country_code': 'Código_País',
            'lat': 'Latitud',
            'lon': 'Longitud',
            'temp': 'Temperatura_C',
            'hum': 'Humedad_Pct',
            'wind': 'Viento_m_s'
        })
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_data = report_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Reporte CSV",
                data=csv_data,
                file_name="reporte_calidad_aire.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with col_dl2:
            import io
            excel_buffer = io.BytesIO()
            try:
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    report_df.to_excel(writer, index=False, sheet_name='Reporte')
                st.download_button(
                    label="📥 Descargar Reporte Excel",
                    data=excel_buffer.getvalue(),
                    file_name="reporte_calidad_aire.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generando Excel. Verifica si openpyxl está instalado.")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Ordenar de peor a mejor AQI (mayor a menor AQI)
        frame_sorted = frame.sort_values(by="AQI", ascending=False)
        
        for _, row in frame_sorted.iterrows():
            risk_color = next((s["color"] for s in RISK_STATES.values() if s["label"] == row["Riesgo"]), "gray")
            
            temp_val = f"{row.get('temp', 0):.1f}°C" if pd.notna(row.get('temp')) else "N/D"
            hum_val = f"{row.get('hum', 0):.0f}%" if pd.notna(row.get('hum')) else "N/D"
            wind_val = f"{row.get('wind', 0):.1f}m/s" if pd.notna(row.get('wind')) else "N/D"
            
            def get_val(code):
                val = row.get(code)
                return f"{val:.1f}" if pd.notna(val) and val is not None else "N/D"
            
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
        <div class="eco-city-metric">
            <span class="eco-city-metric-label">Condiciones Climáticas (OW)</span>
            <span class="eco-city-metric-value" style="font-size: 1.1rem; display: flex; gap: 0.8rem; align-items: center; padding-top: 0.35rem;">
                <span style="display:flex; align-items:center; gap:0.25rem;" title="Temperatura">{svg_temp} {temp_val}</span>
                <span style="display:flex; align-items:center; gap:0.25rem;" title="Humedad">{svg_hum} {hum_val}</span>
                <span style="display:flex; align-items:center; gap:0.25rem;" title="Viento">{svg_wind} {wind_val}</span>
            </span>
        </div>
    </div>
    <div class="eco-city-pollutants">
        <div class="eco-pollutant-box"><span class="eco-pollutant-name">PM2.5</span><span class="eco-pollutant-val">{get_val('pm2_5')}</span></div>
        <div class="eco-pollutant-box"><span class="eco-pollutant-name">PM10</span><span class="eco-pollutant-val">{get_val('pm10')}</span></div>
        <div class="eco-pollutant-box"><span class="eco-pollutant-name">O3</span><span class="eco-pollutant-val">{get_val('o3')}</span></div>
        <div class="eco-pollutant-box"><span class="eco-pollutant-name">NO2</span><span class="eco-pollutant-val">{get_val('no2')}</span></div>
        <div class="eco-pollutant-box"><span class="eco-pollutant-name">SO2</span><span class="eco-pollutant-val">{get_val('so2')}</span></div>
        <div class="eco-pollutant-box"><span class="eco-pollutant-name">CO</span><span class="eco-pollutant-val">{get_val('co')}</span></div>
    </div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.session_state["current_pollution_context"] = {
        "page_name": "Ciudad Comparativa",
        "ciudades_seleccionadas": selected_cities,
        "datos_comparativos": frame.drop(columns=['critical_pollutants']) if 'critical_pollutants' in frame.columns else frame,
        "alertas_oms_activas": bool(alerts_list)
    }

if __name__ == "__main__":
    render(get_runtime_filters())