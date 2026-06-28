from __future__ import annotations

import streamlit as st



def render_section_header(title: str, subtitle: str | None = None) -> None:
    html_content = f"""<div style="margin-bottom: 2rem;">
<h1 style="font-size: 2.25rem; font-weight: 800; color: var(--text-color); margin: 0 0 0.5rem 0; letter-spacing: -0.025em; line-height: 1.2;">
{title}
</h1>"""
    
    if subtitle:
        html_content += f"""<p style="font-size: 1.1rem; color: var(--text-color); opacity: 0.7; margin: 0; font-weight: 400;">
{subtitle}
</p>"""
        
    html_content += "</div>"
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Adicionalmente, inyectamos el CSS para ocultar globalmente cualquier otro link de ancla residual en markdown
    st.markdown("""<style>
.stMarkdown a.header-anchor { display: none !important; }
.stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a { display: none !important; }
</style>""", unsafe_allow_html=True)
