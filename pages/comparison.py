from __future__ import annotations

import streamlit as st

from components.section_header import render_section_header
from utils.page_context import get_runtime_filters



def render(filters: dict) -> None:
    render_section_header("Ciudad Comparativa", "Comparación inicial entre ciudades seleccionadas.")
    st.info("Esta vista se conectará al provider normalizado y a barras comparativas en la siguiente iteración.")
    st.write("Filtros activos:", filters)


if __name__ == "__main__":
    render(get_runtime_filters())
