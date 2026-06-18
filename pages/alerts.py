# pyrefly: ignore [missing-import]

import pandas as pd
import plotly.express as px
import streamlit as st

from components.section_header import render_section_header
from providers.open_meteo_air_quality import fetch_city_snapshot
from config.constants import DEFAULT_CITIES, RISK_STATES
from config.cities import get_city_location
from utils.page_context import get_runtime_filters


def render(filters: dict) -> None:

    render_section_header(
        "Alertas OMS",
        "Evaluación automática de la calidad del aire según los límites de seguridad de la OMS."
    )

    st.caption(
        "El sistema analiza los contaminantes detectados y determina si existen condiciones de riesgo para la salud."
    )

    city_alerts = []
    alert_details = []

    with st.spinner("Evaluando ciudades disponibles..."):

        for city in DEFAULT_CITIES:

            try:

                response = fetch_city_snapshot(
                    city,
                    start_date=filters.get("date_from"),
                    end_date=filters.get("date_to")
                )

                summary = response.data["summary"]
                current_frame = response.data["current_frame"]

                critical_pollutants = current_frame[
                    current_frame["risk_state"].isin(
                        ["poor", "very_poor", "hazardous"]
                    )
                ]

                pollutants = critical_pollutants[
                    "pollutant_name"
                ].tolist()

                city_alerts.append(
                    {
                        "Ciudad": city,
                        "Estado": summary.get(
                            "risk_state",
                            "unknown"
                        ),
                        "Contaminantes": (
                            ", ".join(pollutants)
                            if pollutants
                            else "Ninguno"
                        ),
                        "Indicadores críticos": len(
                            pollutants
                        ),
                    }
                )

                for _, row in critical_pollutants.iterrows():

                    alert_details.append(
                        {
                            "Ciudad": city,
                            "Contaminante": row[
                                "pollutant_name"
                            ],
                            "Estado": RISK_STATES.get(
                                row["risk_state"],
                                RISK_STATES["unknown"]
                            )["label"],
                            "Valor": row.get("value"),
                            "Unidad": row.get("unit"),
                        }
                    )

            except Exception:

                city_alerts.append(
                    {
                        "Ciudad": city,
                        "Estado": "unknown",
                        "Contaminantes": "—",
                        "Indicadores críticos": 0,
                    }
                )

    if not city_alerts:
        st.warning(
            "No se pudieron evaluar ciudades."
        )
        return

    danger_states = [
        "poor",
        "very_poor",
        "hazardous",
    ]

    alerts = [
        city
        for city in city_alerts
        if city["Estado"] in danger_states
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🌎 Ciudades evaluadas",
        len(city_alerts)
    )

    col2.metric(
        "🚨 Alertas OMS",
        len(alerts)
    )

    col3.metric(
        "✅ Ciudades seguras",
        len(city_alerts) - len(alerts)
    )

    st.markdown("### 🚦 Estado Regional OMS")

    if len(alerts) == 0:

        st.success(
            "🟢 Todas las ciudades cumplen los límites OMS."
        )

    elif len(alerts) <= 2:

        st.warning(
            "🟡 Algunas ciudades presentan riesgo ambiental."
        )

    else:

        st.error(
            "🔴 Varias ciudades presentan niveles preocupantes de contaminación."
        )

    st.markdown("### 🗺️ Ciudades Monitoreadas")

    map_data = []

    for city in DEFAULT_CITIES:

        location = get_city_location(city)

        map_data.append(
            {
                "lat": location["latitude"],
                "lon": location["longitude"],
            }
        )

    st.map(
        pd.DataFrame(map_data),
        use_container_width=True
    )

    df = pd.DataFrame(city_alerts)

    df["Estado OMS"] = df["Estado"].map(
        lambda state: RISK_STATES.get(
            state,
            RISK_STATES["unknown"]
        )["label"]
    )

    df = df.sort_values(
        by="Indicadores críticos",
        ascending=False
    )

    st.markdown(
        "### 📊 Ranking de Riesgo Ambiental"
    )

    chart = px.bar(
        df,
        x="Indicadores críticos",
        y="Ciudad",
        color="Estado OMS",
        orientation="h",
        text="Indicadores críticos"
    )

    chart.update_layout(
        height=500,
        yaxis_title="Ciudad",
        xaxis_title="Contaminantes fuera de norma OMS"
    )

    st.plotly_chart(
        chart,
        use_container_width=True
    )

    st.markdown("---")

    if alerts:

        st.markdown(
            "### 🚨 Alertas Activas"
        )

        for alert in alerts:

            state = RISK_STATES.get(
                alert["Estado"],
                RISK_STATES["unknown"]
            )

            with st.container(border=True):

                st.subheader(
                    f"🚨 {alert['Ciudad']}"
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Estado OMS",
                        state["label"]
                    )

                with col2:
                    st.metric(
                        "Indicadores críticos",
                        alert["Indicadores críticos"]
                    )

                st.write(
                    f"**Contaminantes críticos:** {alert['Contaminantes']}"
                )

    else:

        st.success(
            "No existen alertas activas."
        )

    st.markdown("### 📋 Resumen General")

    st.dataframe(
        df[
            [
                "Ciudad",
                "Estado OMS",
                "Contaminantes",
                "Indicadores críticos",
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "### 🔬 Detalle de Contaminantes en Alerta"
    )

    if alert_details:

        detail_df = pd.DataFrame(
            alert_details
        )

        st.dataframe(
            detail_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No se detectaron contaminantes por encima de los límites OMS."
        )


if __name__ == "__main__":
    render(get_runtime_filters())