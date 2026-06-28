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
    "Glosario": "pages/glossary.py",
}



def build_sidebar_filters() -> dict:
    defaults = get_default_filters()
    
    st.sidebar.markdown("""
        <div class="flex items-center gap-2 mb-2 mt-4">
            <svg class="text-emerald-500" style="width: 24px; height: 24px; flex-shrink: 0;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path></svg>
            <h2 class="text-xl font-bold m-0 p-0" style="color: var(--text-color);">Filtros globales</h2>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""
        <div class="flex items-center gap-2 mb-[-1rem] mt-2">
            <svg class="text-emerald-400" style="width: 20px; height: 20px; flex-shrink: 0;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            <span class="text-sm font-semibold" style="color: var(--text-color);">Desde</span>
        </div>
    """, unsafe_allow_html=True)
    date_from = st.sidebar.date_input("Desde_hidden", value=defaults["date_from"], help="Inicio del periodo analítico global.", label_visibility="collapsed")
    
    st.sidebar.markdown("""
        <div class="flex items-center gap-2 mb-[-1rem] mt-2">
            <svg class="text-emerald-400" style="width: 20px; height: 20px; flex-shrink: 0;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            <span class="text-sm font-semibold" style="color: var(--text-color);">Hasta</span>
        </div>
    """, unsafe_allow_html=True)
    date_to = st.sidebar.date_input("Hasta_hidden", value=defaults["date_to"], help="Fin del periodo analítico global.", label_visibility="collapsed")
    return normalize_filters(
        {
            "date_from": date_from,
            "date_to": date_to,
        }
    )



def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=":material/public:", layout="wide")

    # CSS global para ocultar los íconos de enlace en los títulos (header anchors)
    st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
    tailwind.config = {
        corePlugins: {
            preflight: false,
        }
    }
    </script>
    <style>
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
