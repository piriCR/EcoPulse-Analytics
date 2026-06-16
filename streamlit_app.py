from __future__ import annotations

import streamlit as st

from config.constants import APP_SUBTITLE, APP_TITLE, NAVIGATION_PAGES, PRIMARY_POLLUTANTS, DEFAULT_CITIES
from utils.filters import get_default_filters, normalize_filters

PAGE_PATHS = {
    "Inicio": "pages/overview.py",
    "Monitoreo en Vivo": "pages/monitoring.py",
    "Ciudad Comparativa": "pages/comparison.py",
    "Evolución Temporal": "pages/timeline.py",
    "Alertas OMS": "pages/alerts.py",
    "Perfil de Ciudad": "pages/city_profile.py",
}



def build_sidebar_filters() -> dict:
    defaults = get_default_filters()
    st.sidebar.header("Filtros globales")

    date_from = st.sidebar.date_input("Desde", value=defaults["date_from"], help="Inicio del periodo analítico global.")
    date_to = st.sidebar.date_input("Hasta", value=defaults["date_to"], help="Fin del periodo analítico global.")
    cities = st.sidebar.multiselect(
        "Ciudades",
        options=DEFAULT_CITIES,
        default=defaults["cities"],
        help="Ciudades que definen el contexto común entre pantallas.",
    )
    focus_city = st.sidebar.selectbox(
        "Ciudad foco",
        options=cities or DEFAULT_CITIES,
        index=0,
        help="Ciudad principal para las páginas que usan un foco único.",
    )
    primary_pollutant = st.sidebar.selectbox(
        "Contaminante principal",
        options=PRIMARY_POLLUTANTS,
        index=0,
        help="Contaminante de referencia compartido por el contexto general.",
    )

    return normalize_filters(
        {
            "date_from": date_from,
            "date_to": date_to,
            "cities": cities,
            "focus_city": focus_city,
            "primary_pollutant": primary_pollutant,
        }
    )



def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=":material/public:", layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    filters = build_sidebar_filters()
    st.session_state["global_filters"] = filters

    # Navegación superior única (sin navegación duplicada dentro del contenido)
    pages_spec = []
    for name in NAVIGATION_PAGES:
        page_path = PAGE_PATHS.get(name)
        if page_path is None:
            continue
        pages_spec.append(
            st.Page(
                page_path,
                title=name,
                default=(name == NAVIGATION_PAGES[0]),
            )
        )

    if not pages_spec:
        st.error("No hay páginas configuradas para la navegación.")
        return

    pg = st.navigation({"": pages_spec}, position="top")
    pg.run()


if __name__ == "__main__":
    main()
