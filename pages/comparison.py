import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
                
                city_data_list.append({
                    "city_name": location["city_name"], "country_code": location["country_code"],
                    "lat": location["latitude"], "lon": location["longitude"],
                    "AQI": pd.to_numeric(summary.get("european_aqi", 0), errors="coerce"),
                    "Riesgo": RISK_STATES.get(summary.get("risk_state", "unknown"), RISK_STATES["unknown"])["label"],
                    "Dominante": summary.get("dominant_pollutant", "—"),
                    "Severidad": pd.to_numeric(summary.get("dominant_ratio", 0), errors="coerce"),
                    **pollutants_dict
                })
            except Exception as exc: errors.append(f"{city_key}: {exc}")

    if not city_data_list:
        st.error("Error al obtener datos.")
        return

    frame = pd.DataFrame(city_data_list).fillna(0)

    # --- Tabs de Visualización ---
    tab1, tab2, tab3 = st.tabs(["📊 Gráficas", "🗺️ Mapa", "📋 Reporte Detallado"])

    with tab1:
        st.subheader("Comparativa de Indicadores")
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
        st.subheader("Ubicación Geográfica")
        map_fig = px.density_mapbox(frame, lat="lat", lon="lon", z="AQI", radius=50, center=dict(lat=frame["lat"].mean(), lon=frame["lon"].mean()), zoom=3.5,
                                   hover_name="city_name", color_continuous_scale="Turbo")
        map_fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(map_fig, use_container_width=True)

    with tab3:
        st.subheader("Ficha Técnica por Ciudad")
        for _, row in frame.iterrows():
            risk_color = next((s["color"] for s in RISK_STATES.values() if s["label"] == row["Riesgo"]), "gray")
            
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-left: 6px solid {risk_color}; border-radius: 10px; padding: 20px; margin-bottom: 15px;">
                <h3 style="margin: 0;">{row['city_name']} <small style="color: gray;">({row['country_code']})</small></h3>
                <p><strong>Nivel de Riesgo:</strong> {row['Riesgo']}</p>
                <div style="display: flex; gap: 20px;">
                    <div><small>CALIDAD DEL AIRE (AQI)</small><br><span style="font-size: 24px; font-weight: bold;">{row['AQI']:.1f}</span></div>
                    <div><small>CONTAMINANTE PRINCIPAL</small><br><span style="font-size: 24px; font-weight: bold;">{row['Dominante']}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.session_state["current_pollution_context"] = {
        "page_name": "Ciudad Comparativa",
        "ciudades_seleccionadas": selected_cities,
        "datos_comparativos": frame
    }

if __name__ == "__main__":
    render(get_runtime_filters())