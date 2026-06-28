# pyrefly: ignore [missing-import]
import streamlit as st
import re
import os
import base64

def get_base64_of_bin_file(bin_file):
    if not os.path.exists(bin_file):
        return ""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render() -> None:
    # 1. Configuración de estilos y Tailwind CSS (con preflight desactivado para no romper Streamlit)
    st.markdown("""<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
    corePlugins: {
        preflight: false,
    }
}
</script>
<style>
/* Asegurar que las clases de tailwind funcionen en el markdown */
.glossary-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.glossary-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    border-color: #4ade80 !important;
}
input[type="text"] {
    font-size: 1.1rem;
}
</style>""", unsafe_allow_html=True)

    # 2. BANNER HERO PROFESIONAL CON CSS Y HTML (Consistente con Overview)
    img_path = r"C:\Users\Sanch\.gemini\antigravity\brain\e884dfb5-82af-4887-b6d3-88e60311a4b3\climate_action_hero_bg_1781581238331.png"
    img_base64 = get_base64_of_bin_file(img_path)
    
    bg_style = f"background-image: linear-gradient(rgba(10, 40, 20, 0.65), rgba(5, 20, 10, 0.85)), url('data:image/png;base64,{img_base64}');" if img_base64 else "background-color: #0f2a1a;"

    st.markdown(f"""<div style="{bg_style} background-size: cover; background-position: center; border-radius: 16px; padding: 60px 40px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem; margin-top: -2rem; border: 1px solid rgba(255,255,255,0.1);">
<h1 style="color: #ffffff; font-size: 3rem; font-weight: 800; margin-bottom: 5px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); font-family: 'Inter', sans-serif;">
Glosario Ambiental
</h1>
<h2 style="color: #4ade80; font-size: 1.8rem; font-weight: 600; margin-bottom: 20px; text-shadow: 0 1px 3px rgba(0,0,0,0.5);">
ODS 13: Acción por el Clima
</h2>
<p style="font-size: 1.15rem; font-weight: 300; max-width: 850px; margin: 0 auto; line-height: 1.6; color: #f1f5f9; text-shadow: 0 1px 2px rgba(0,0,0,0.8);">
Definiciones técnicas, unidades de medida y umbrales de riesgo establecidos por la Organización Mundial de la Salud. Útil para interpretar correctamente el impacto ambiental en las zonas de estudio.
</p>
</div>""", unsafe_allow_html=True)

    # Base de datos del glosario
    glossary_data = [
        {
            "term": "Material Particulado Fino",
            "acronym": "PM2.5",
            "definition": "Partículas sólidas o líquidas suspendidas en el aire con un diámetro aerodinámico igual o menor a 2.5 micrómetros. Penetran profundamente en los pulmones y el torrente sanguíneo, representando el mayor riesgo de mortalidad cardiovascular y respiratoria.",
            "unit": "μg/m³",
            "threshold": "15 μg/m³ (media de 24h)"
        },
        {
            "term": "Material Particulado",
            "acronym": "PM10",
            "definition": "Partículas con un diámetro aerodinámico igual o menor a 10 micrómetros. Incluye polvo, cenizas y hollín. Pueden penetrar y alojarse en las regiones profundas de los pulmones.",
            "unit": "μg/m³",
            "threshold": "45 μg/m³ (media de 24h)"
        },
        {
            "term": "Dióxido de Nitrógeno",
            "acronym": "NO2",
            "definition": "Gas altamente reactivo proveniente principalmente de la combustión a altas temperaturas en vehículos y plantas eléctricas. Incrementa la inflamación de las vías respiratorias y reduce la función pulmonar.",
            "unit": "μg/m³",
            "threshold": "25 μg/m³ (media de 24h)"
        },
        {
            "term": "Ozono Troposférico",
            "acronym": "O3",
            "definition": "Contaminante secundario formado a nivel del suelo por reacciones fotoquímicas entre óxidos de nitrógeno (NOx) y compuestos orgánicos volátiles (COV) en presencia de luz solar. Desencadena asma y enfermedades pulmonares.",
            "unit": "μg/m³",
            "threshold": "100 μg/m³ (media de 8h)"
        },
        {
            "term": "Dióxido de Azufre",
            "acronym": "SO2",
            "definition": "Gas incoloro con olor penetrante generado principalmente por la quema de combustibles fósiles ricos en azufre. Causa broncoconstricción y agrava el asma.",
            "unit": "μg/m³",
            "threshold": "40 μg/m³ (media de 24h)"
        },
        {
            "term": "Monóxido de Carbono",
            "acronym": "CO",
            "definition": "Gas tóxico, incoloro e inodoro producto de la combustión incompleta. Reduce la capacidad de la sangre para transportar oxígeno a los tejidos vitales.",
            "unit": "mg/m³",
            "threshold": "4 mg/m³ (media de 24h)"
        },
        {
            "term": "Índice de Calidad del Aire",
            "acronym": "AQI",
            "definition": "Indicador cuantitativo estandarizado que transforma concentraciones complejas de múltiples contaminantes en un valor único fácil de interpretar por el público general.",
            "unit": "Adimensional",
            "threshold": "> 100 (Grupos sensibles)"
        }
    ]

    # Barra de Búsqueda Predictiva (Filtro) con SVG y Tailwind inline
    st.markdown("""<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; margin-top: 1rem;">
<svg style="width: 1.5rem; height: 1.5rem; color: #34d399;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
<span style="color: #e5e7eb; font-size: 1.125rem; font-weight: 600;">Buscador de Términos Ambientales</span>
</div>""", unsafe_allow_html=True)
    search_query = st.text_input("Oculto", "", label_visibility="collapsed", placeholder="Buscar término, acrónimo o concepto...")
    
    # Lógica de filtrado predictivo
    filtered_data = []
    if search_query:
        query = search_query.lower()
        for item in glossary_data:
            if (query in item['term'].lower() or 
                query in item['acronym'].lower() or 
                query in item['definition'].lower()):
                filtered_data.append(item)
    else:
        filtered_data = glossary_data

    # Renderizar resultados usando estructura de CSS (SIN INDENTACIÓN PARA EVITAR MARKDOWN CODEBLOCKS)
    if filtered_data:
        html_content = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; margin-top: 1rem;">'
        
        for item in filtered_data:
            acronym_display = re.sub(r'(\d+\.?\d*)', r'<sub>\1</sub>', item['acronym'])
            
            html_content += f"""<div class="glossary-card" style="background-color: var(--secondary-background-color); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; display: flex; flex-direction: column; height: 100%;">
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 0.75rem;">
<div>
<h3 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: var(--text-color);">{acronym_display}</h3>
<span style="font-size: 0.85rem; font-weight: 600; color: #4ade80; text-transform: uppercase; letter-spacing: 0.05em;">{item['term']}</span>
</div>
</div>
<p style="font-size: 0.95rem; line-height: 1.6; color: var(--text-color); opacity: 0.85; flex-grow: 1; margin-bottom: 1.5rem;">
{item['definition']}
</p>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; background-color: rgba(128,128,128,0.05); padding: 1rem; border-radius: 8px;">
<div>
<div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-color); opacity: 0.6; font-weight: 600; margin-bottom: 0.25rem;">Unidad Estándar</div>
<div style="font-size: 1rem; font-weight: 700; color: var(--text-color);">{item['unit']}</div>
</div>
<div>
<div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-color); opacity: 0.6; font-weight: 600; margin-bottom: 0.25rem;">Umbral de Riesgo (OMS)</div>
<div style="font-size: 1rem; font-weight: 700; color: #ef4444;">{item['threshold']}</div>
</div>
</div>
</div>"""
            
        html_content += '</div>'
        st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.info("No se encontraron resultados para tu búsqueda.")

    # Contexto para el chat de IA
    st.session_state["current_pollution_context"] = {
        "page_name": "Glosario (Buscador Activo)",
        "context": f"El usuario está consultando el glosario. Búsqueda actual: '{search_query}'. Contiene {len(filtered_data)} resultados visibles."
    }

if __name__ == "__main__":
    render()
