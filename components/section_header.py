from __future__ import annotations

import streamlit as st



def render_section_header(title: str, subtitle: str | None = None) -> None:
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)
