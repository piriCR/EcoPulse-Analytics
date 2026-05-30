from __future__ import annotations

import streamlit as st

from components.section_header import render_section_header
from utils.page_context import get_runtime_filters



def render(filters: dict) -> None:
    render_section_header("Monitoreo en Vivo", "Vista operativa para detectar cambios recientes y estados críticos.")

    st.caption("Los ajustes de granularidad y modo comparativo se mantienen aquí porque solo cambian esta vista.")

    local_col1, local_col2 = st.columns(2)
    granularity = local_col1.selectbox("Granularidad", options=["hora", "día", "semana"], index=1)
    comparison_mode = local_col2.selectbox("Modo", options=["única ciudad", "comparar"], index=0)
    page_filters = {**filters, "granularity": granularity, "comparison_mode": comparison_mode}

    col1, col2, col3 = st.columns(3)
    col1.metric("Ciudad foco", filters.get("focus_city", "-"))
    col2.metric("Granularidad", granularity)
    col3.metric("Modo", comparison_mode)

    st.info("La integración con providers y series reales se añadirá en la siguiente iteración.")
    st.write("Filtros activos:", page_filters)


if __name__ == "__main__":
    render(get_runtime_filters())
