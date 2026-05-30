from __future__ import annotations

import streamlit as st

from utils.filters import get_default_filters, normalize_filters


def get_runtime_filters() -> dict:
    filters = st.session_state.get("global_filters")
    if not isinstance(filters, dict):
        return normalize_filters(get_default_filters())
    return normalize_filters(filters)
