from __future__ import annotations

import streamlit as st

from components.section_header import render_section_header
from utils.page_context import get_runtime_filters



def render(filters: dict) -> None:
    render_section_header("Alertas OMS", "Incumplimientos y estados de riesgo.")
    st.warning("Todavía no hay cálculo de umbrales ni alerta derivada; esta página es un marcador de implementación.")
    st.write("Filtros activos:", filters)


if __name__ == "__main__":
    render(get_runtime_filters())
