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
    render_section_header("Ciudad Comparativa", "Módulo analítico para comparar múltiples ciudades.")
    st.caption("Visualiza y contrasta el impacto ambiental entre diferentes regiones mediante mapas de calor y gráficas detalladas.")

    st.sidebar.header("Filtros de Comparación")
    selected_cities = st.sidebar.multiselect(
        "Ciudades a comparar",
        options=DEFAULT_CITIES,
        default=DEFAULT_CITIES[:4],
        help="Agrega o elimina ciudades dinámicamente para compararlas."
    )

    if not selected_cities:
        st.warning("Por favor, selecciona al menos una ciudad en el menú lateral para comparar.")
        return

    date_from = filters.get("date_from")
    date_to = filters.get("date_to")
    date_from_str = date_from.isoformat() if hasattr(date_from, "isoformat") else None
    date_to_str = date_to.isoformat() if hasattr(date_to, "isoformat") else None

    # Vamos a guardar el snapshot completo por ciudad
    city_data_list = []
    errors: list[str] = []

    with st.spinner("Obteniendo datos comparativos multivariables..."):
        for city_key in selected_cities:
            try:
                response = fetch_city_snapshot(city_key, start_date=date_from_str, end_date=date_to_str)
                
                # Extraemos summary, location y current_frame
                summary = response.data["summary"]
                location = response.data["location"]
                current_frame = response.data["current_frame"]
                
                # Convertimos current_frame (formato largo) a un diccionario de contaminantes (formato ancho)
                pollutants_dict = {}
                if not current_frame.empty:
                    for _, row in current_frame.iterrows():
                        pollutants_dict[row["pollutant_name"]] = row["value"]
                        
                # Consolidamos toda la info de la ciudad
                city_info = {
                    "city_name": location["city_name"],
                    "country_code": location["country_code"],
                    "lat": location["latitude"],
                    "lon": location["longitude"],
                    "AQI": pd.to_numeric(summary.get("european_aqi", 0), errors="coerce"),
                    "Riesgo": RISK_STATES.get(summary.get("risk_state", "unknown"), RISK_STATES["unknown"])["label"],
                    "Dominante": summary.get("dominant_pollutant", "—"),
                    "Severidad": pd.to_numeric(summary.get("dominant_ratio"), errors="coerce"),
                    **pollutants_dict # Expandimos los contaminantes como columnas (pm2_5, pm10, etc.)
                }
                city_data_list.append(city_info)
            except Exception as exc:  # pragma: no cover
                errors.append(f"{city_key}: {exc}")

    if not city_data_list:
        st.error("No se pudieron cargar los datos de las ciudades seleccionadas.")
        if errors:
            for error in errors: st.write(error)
        return

    # DataFrame maestro consolidado
    frame = pd.DataFrame(city_data_list)
    # Llenamos NaN del AQI con 0 para evitar errores visuales
    frame["AQI"] = frame["AQI"].fillna(0)

    tab1, tab2, tab3 = st.tabs(["Análisis Gráfico", "Mapa de Calor (Heatmap)", "Datos Detallados"])

    with tab1:
        st.markdown("### Comparación Dinámica de Indicadores")
        
        # Ofrecer opciones basadas en las columnas que realmente extrajimos (AQI + contaminantes encontrados)
        available_metrics = ["AQI", "Severidad"] + [p for p in PRIMARY_POLLUTANTS if p in frame.columns]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            compare_metric = st.selectbox("Métrica a comparar", options=available_metrics, index=0)
            st.info(f"Mostrando niveles de **{compare_metric}**. Valores más altos representan mayor contaminación/riesgo.")
            
        with col2:
            # Asegurar que la métrica seleccionada no tenga NaNs que rompan el gráfico
            plot_frame = frame.copy()
            plot_frame[compare_metric] = pd.to_numeric(plot_frame[compare_metric], errors="coerce").fillna(0)
            
            # Ordenar para mejor visualización
            plot_frame = plot_frame.sort_values(by=compare_metric, ascending=False)
            
            chart = px.bar(
                plot_frame,
                x="city_name",
                y=compare_metric,
                color="Riesgo",
                color_discrete_map={state["label"]: state["color"] for state in RISK_STATES.values()},
                text_auto='.1f',
                labels={"city_name": "Ciudad", compare_metric: compare_metric},
                title=f"Niveles de {compare_metric} por Ciudad"
            )
            chart.update_traces(textposition='outside')
            chart.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(chart, use_container_width=True)

    with tab2:
        st.markdown("### Mapa de Impacto Ambiental")
        st.caption("Visualización geográfica en alta resolución. Las esferas indican la ubicación de cada ciudad y su color refleja el nivel de alerta.")
        
        if frame["AQI"].sum() == 0:
            st.warning("No hay suficientes datos numéricos de AQI en este momento para generar zonas de calor.")
        else:
            # Restauramos el mapa de calor (density_mapbox) que incluye la barra vertical de colores
            map_fig = px.density_mapbox(
                frame, 
                lat="lat", 
                lon="lon", 
                z="AQI", # El peso de la contaminación
                radius=50, # Radio amplio para que las zonas de calor sean muy notorias
                center=dict(lat=frame["lat"].mean(), lon=frame["lon"].mean()), 
                zoom=3.5,
                hover_name="city_name",
                hover_data={"lat": False, "lon": False, "AQI": True, "Riesgo": True, "Dominante": True},
                color_continuous_scale="Turbo" # Escala 'Turbo' es muy vibrante y fácil de leer
            )
            
            # Añadimos una capa superior con los nombres de las ciudades fijos
            map_fig.add_trace(go.Scattermapbox(
                lat=frame["lat"],
                lon=frame["lon"],
                mode="text+markers",
                text=frame["city_name"],
                textfont=dict(size=14, color="black", family="Arial Black"),
                textposition="top center",
                marker=dict(size=8, color="black", opacity=0.6),
                hoverinfo="skip", # Para que no estorbe el hover interactivo original del calor
                showlegend=False
            ))
            # 'open-street-map' muestra el terreno real, océanos y los nombres de las ciudades/países en texto oscuro muy claro
            map_fig.update_layout(mapbox_style="open-street-map") 
            map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
            
            with st.container(border=True):
                st.plotly_chart(map_fig, use_container_width=True)

    with tab3:
        st.markdown("### :material/assignment: Reporte Analítico Detallado")
        st.caption("Auditoría ambiental profunda por ciudad. Desglose de concentración de partículas y gases (μg/m³).")
        
        if frame.empty:
            st.info("No hay datos disponibles para generar el reporte.")
        else:
            # Identificar qué columnas son realmente gases buscando aquellos que no son metadatos fijos
            fixed_cols = {"city_name", "country_code", "lat", "lon", "AQI", "Riesgo", "Dominante", "Severidad", "european_aqi"}
            gas_columns = [col for col in frame.columns if col not in fixed_cols]

            # Icono SVG de alerta (Material Design) para reemplazar el emoji
            alert_svg = '''<svg xmlns="http://www.w3.org/2000/svg" height="14" viewBox="0 -960 960 960" width="14" fill="currentColor" style="vertical-align: middle; margin-right: 2px;"><path d="m40-120 440-760 440 760H40Zm104-80h672L480-780 144-200Zm340-120q17 0 28.5-11.5T524-360q0-17-11.5-28.5T484-400q-17 0-28.5 11.5T444-360q0 17 11.5 28.5T484-320Zm-40-120h80v-200h-80v200Zm40-100Z"/></svg>'''
            
            # Icono SVG de ubicación
            location_svg = '''<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor" style="vertical-align: bottom; margin-right: 4px;"><path d="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 294q122-112 181-203.5T720-552q0-109-75.5-184.5T480-812q-89 0-164.5 75.5T240-552q0 71 59 162.5T480-186Zm0 106Q319-217 239.5-334.5T160-552q0-150 96.5-239T480-880q127 0 223.5 89T800-552q0 100-79.5 217.5T480-80Zm0-480Z"/></svg>'''

            for _, row in frame.iterrows():
                risk_label = row["Riesgo"]
                color = next((s["color"] for s in RISK_STATES.values() if s["label"] == risk_label), "gray")
                
                # Generar "píldoras" (pills) para los contaminantes detectados
                gases_html = ""
                for gas in gas_columns:
                    if pd.notna(row[gas]):
                        val = row[gas]
                        is_dom = False
                        if row["Dominante"] and str(row["Dominante"]).lower().replace("_", "").replace(".", "") in gas.lower().replace("_", "").replace(".", ""):
                            is_dom = True
                        
                        bg_col = f"{color}22" if is_dom else "rgba(128,128,128,0.08)"
                        text_col = color if is_dom else "inherit"
                        border = f"1px solid {color}" if is_dom else "1px solid rgba(128,128,128,0.2)"
                        
                        gases_html += f"""
<div style="display: inline-block; background-color: {bg_col}; color: {text_col}; border: {border}; padding: 6px 14px; border-radius: 20px; margin: 4px; font-size: 0.85rem; font-weight: 600;">
    {gas}: <span style="font-size: 1rem;">{val:.1f}</span>
    {' <span style="font-size:0.75rem; margin-left: 4px;">' + alert_svg + 'Principal Causante</span>' if is_dom else ''}
</div>"""
    
                html_card = f"""
<div style="border: 1px solid rgba(128,128,128,0.2); border-left: 6px solid {color}; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; border-bottom: 1px solid rgba(128,128,128,0.1); padding-bottom: 15px;">
        <div>
            <h4 style="margin: 0; font-size: 1.4rem; font-weight: 700; display: flex; align-items: center;">
                <span style="color: {color};">{location_svg}</span> {row['city_name']} <span style="font-size: 0.9rem; font-weight: normal; color: gray; margin-left: 6px;">{row['country_code']}</span>
            </h4>
        </div>
        <div style="text-align: right; background-color: {color}; color: white; padding: 4px 16px; border-radius: 30px;">
            <strong style="font-size: 1rem; text-transform: uppercase;">Estado: {risk_label}</strong>
        </div>
    </div>
    <div style="display: flex; gap: 40px; margin-bottom: 20px;">
        <div>
            <div style="font-size: 0.8rem; color: gray; text-transform: uppercase;">Calidad del Aire (AQI)</div>
            <div style="font-size: 2rem; font-weight: 800;">{row['AQI']:.1f} <span style="font-size: 0.9rem; font-weight: normal; color: gray;">/ 500</span></div>
            <div style="font-size: 0.75rem; color: gray; max-width: 150px;">Valores menores son más saludables.</div>
        </div>
        <div>
            <div style="font-size: 0.8rem; color: gray; text-transform: uppercase;">Índice de Toxicidad</div>
            <div style="font-size: 2rem; font-weight: 800;">{row['Severidad']:.2f} <span style="font-size: 0.9rem; font-weight: normal; color: gray;">x</span></div>
            <div style="font-size: 0.75rem; color: gray; max-width: 150px;">Multiplicador sobre el límite seguro de la OMS. (>1.0 es peligroso)</div>
        </div>
    </div>
    <div style="font-size: 0.85rem; color: gray; margin-bottom: 10px; text-transform: uppercase;">Desglose de Gases y Partículas (μg/m³):</div>
    <div style="display: flex; flex-wrap: wrap; gap: 4px;">
        {gases_html}
    </div>
</div>
"""
                st.markdown(html_card, unsafe_allow_html=True)

    if errors:
        with st.expander("Información de diagnóstico (Errores)"):
            for error in errors:
                st.write(f"- {error}")

if __name__ == "__main__":
    render(get_runtime_filters())
