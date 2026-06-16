# pyrefly: ignore [missing-import]

import pandas as pd
import streamlit as st

from components.section_header import render_section_header
from providers.open_meteo_air_quality import fetch_city_snapshot
from config.constants import DEFAULT_CITIES, RISK_STATES
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

    with st.spinner("Evaluando ciudades disponibles..."):

        for city in DEFAULT_CITIES:

            try:

                response = fetch_city_snapshot(
                    city,
                    start_date=filters.get("date_from"),
                    end_date=filters.get("date_to")
                )

                summary = response.data["summary"]

                city_alerts.append(
                    {
                        "Ciudad": city,
                        "Estado": summary.get("risk_state", "unknown"),
                        "Contaminante": summary.get("dominant_pollutant", "—"),
                        "Indicadores críticos": summary.get("critical_indicators", 0),
                    }
                )

            except Exception as exc:

                city_alerts.append(
                    {
                        "Ciudad": city,
                        "Estado": "unknown",
                        "Contaminante": "—",
                        "Indicadores críticos": 0,
                    }
                )

    if not city_alerts:
        st.warning("No se pudieron evaluar ciudades.")
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
        "Ciudades evaluadas",
        len(city_alerts)
    )

    col2.metric(
        "Alertas activas",
        len(alerts)
    )

    col3.metric(
        "Ciudades seguras",
        len(city_alerts) - len(alerts)
    )

    st.markdown("---")

    if alerts:

        st.error(
            f"Se detectaron {len(alerts)} ciudades que superan los límites recomendados por la OMS."
        )

        for alert in alerts:

            state = RISK_STATES.get(
                alert["Estado"],
                RISK_STATES["unknown"]
            )

            st.warning(
                f"""
                🚨 {alert['Ciudad']}

                Estado OMS: {state['label']}

                Contaminante dominante: {alert['Contaminante']}

                Indicadores críticos: {alert['Indicadores críticos']}
                """
            )

    else:

        st.success(
            "Todas las ciudades evaluadas cumplen actualmente con los niveles recomendados por la OMS."
        )

    st.markdown("### Resumen General")

    df = pd.DataFrame(city_alerts)

    df["Estado OMS"] = df["Estado"].map(
        lambda state: RISK_STATES.get(
            state,
            RISK_STATES["unknown"]
        )["label"]
    )

    st.dataframe(
        df[
            [
                "Ciudad",
                "Estado OMS",
                "Contaminante",
                "Indicadores críticos",
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


if __name__ == "__main__":
    render(get_runtime_filters())