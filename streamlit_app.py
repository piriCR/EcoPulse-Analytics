from __future__ import annotations

# pyrefly: ignore [missing-import]
import streamlit as st

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
load_dotenv()

from config.constants import APP_SUBTITLE, APP_TITLE, NAVIGATION_PAGES, PRIMARY_POLLUTANTS, DEFAULT_CITIES
from utils.filters import get_default_filters, normalize_filters
from components.chat_ui import render_global_chat

PAGE_PATHS = {
    "Inicio": "pages/overview.py",
    "Monitoreo en Vivo": "pages/monitoring.py",
    "Ciudad Comparativa": "pages/comparison.py",
    "Evolución Temporal": "pages/timeline.py",
    "Perfil de Ciudad": "pages/city_profile.py",
}



def build_sidebar_filters() -> dict:
    defaults = get_default_filters()
    st.sidebar.header("Filtros globales")

    date_from = st.sidebar.date_input("Desde", value=defaults["date_from"], help="Inicio del periodo analítico global.")
    date_to = st.sidebar.date_input("Hasta", value=defaults["date_to"], help="Fin del periodo analítico global.")
    return normalize_filters(
        {
            "date_from": date_from,
            "date_to": date_to,
        }
    )



def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=":material/public:", layout="wide")

    # CSS global para ocultar los íconos de enlace en los títulos (header anchors)
    st.markdown("""<style>
    /* Ocultar anclas (links) automáticas de los encabezados de Streamlit */
    .stMarkdown a.header-anchor {
        display: none !important;
    }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a {
        display: none !important;
    }
    /* Estilos generales para asegurar consistencia */
    * {
        scroll-behavior: smooth;
    }
    </style>""", unsafe_allow_html=True)

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

    # Render global chat in the sidebar (after pages have added their own sidebar elements)
    with st.sidebar:
        st.divider()
        render_global_chat()

if __name__ == "__main__":

    main()
