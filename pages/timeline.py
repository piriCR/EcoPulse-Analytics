from __future__ import annotations

import streamlit as st

from components.section_header import render_section_header
from utils.page_context import get_runtime_filters



def render(filters: dict) -> None:
    render_section_header("Evolución Temporal", "Serie temporal para análisis histórico y tendencia.")
    st.info("La visualización temporal real se añadirá cuando exista el provider de datos.")
    st.write("Filtros activos:", filters)
    
    st.session_state["current_pollution_context"] = {
        "page_name": "Evolución Temporal",
        "estado": "Página en construcción, aún no hay datos históricos inyectados.",
        "filtros_activos": filters
    }

if __name__ == "__main__":
    render(get_runtime_filters())
