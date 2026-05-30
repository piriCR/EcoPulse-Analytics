from __future__ import annotations

import streamlit as st

from components.section_header import render_section_header
from utils.page_context import get_runtime_filters



def render(filters: dict) -> None:
    render_section_header("Perfil de Ciudad", "Vista integral de una ciudad seleccionada.")
    st.info("La ficha de ciudad se conectará con series, ranking y alertas en la siguiente fase.")
    st.write("Filtros activos:", filters)


if __name__ == "__main__":
    render(get_runtime_filters())
