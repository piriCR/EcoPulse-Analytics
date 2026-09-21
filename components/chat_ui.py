import streamlit as st
from utils.gemini_service import generate_chat_response

@st.dialog("Asistente EcoPulse IA — Modo Amplio", icon=":material/smart_toy:", width="large")
def show_chat_dialog(context: dict = None):
    """Renders the AI Assistant in a spacious, full-width modal for comfortable reading."""
    if context is None:
        context = st.session_state.get("current_pollution_context", {})

    # Contenedor amplio con altura generosa (480px)
    dialog_chat_container = st.container(height=480)
    with dialog_chat_container:
        for message in st.session_state.get("chat_history", []):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Preguntas rápidas en 3 columnas
    c1, c2, c3 = st.columns(3)
    quick_prompt = None
    with c1:
        if st.button("¿Cómo está el aire?", icon=":material/air:", key="dlg_chip_aire", use_container_width=True):
            quick_prompt = "¿Cómo está la calidad del aire según los datos actuales en pantalla?"
    with c2:
        if st.button("Riesgos a la salud", icon=":material/health_and_safety:", key="dlg_chip_salud", use_container_width=True):
            quick_prompt = "¿Cuáles son los principales riesgos de salud con los contaminantes actuales?"
    with c3:
        if st.button("Mortalidad y ciudades", icon=":material/public:", key="dlg_chip_mortalidad", use_container_width=True):
            quick_prompt = "¿Cuáles son las estimaciones de mortalidad atribuible a la contaminación en grandes ciudades como Nueva Delhi o Santiago?"

    # Entrada de texto en el modal amplio
    user_prompt = st.chat_input("Pregunta sobre calidad del aire, salud o cualquier ciudad del mundo...", key="dlg_chat_input")
    active_prompt = quick_prompt if quick_prompt else user_prompt

    if active_prompt:
        st.session_state["chat_history"].append({"role": "user", "content": active_prompt})
        with dialog_chat_container:
            with st.chat_message("user"):
                st.markdown(active_prompt)

            with st.chat_message("assistant"):
                loader = st.empty()
                loader.caption(":material/hourglass_top: Consultando datos...")

                def stream_with_loader():
                    cleared = False
                    try:
                        for chunk in generate_chat_response(
                            messages=st.session_state["chat_history"],
                            context_data=context
                        ):
                            if not cleared:
                                loader.empty()
                                cleared = True
                            yield chunk
                    finally:
                        loader.empty()

                response_text = st.write_stream(stream_with_loader())
                if not response_text:
                    response_text = "No se pudo obtener una respuesta en este momento. Por favor reintenta tu pregunta."
                    st.markdown(response_text)
        
        st.session_state["chat_history"].append({"role": "assistant", "content": response_text})

    # Barra inferior con botón de limpiar
    if len(st.session_state.get("chat_history", [])) > 1:
        if st.button("Limpiar historial de conversación", icon=":material/delete:", key="dlg_clear_chat", use_container_width=True):
            st.session_state["chat_history"] = [
                {"role": "assistant", "content": "Historial reiniciado. ¿En qué puedo ayudarte con los datos ambientales y de salud?"}
            ]
            st.rerun(scope="fragment")


def render_global_chat():
    """Renders a persistent, fast, and responsive chat interface with option for full-width view."""
    
    # CSS para mejorar la legibilidad, ampliar el sidebar y evitar scroll horizontal molesto
    st.markdown(
        """
        <style>
        /* Mejorar ancho del sidebar para que no quede tan apretado */
        section[data-testid="stSidebar"] {
            min-width: 360px !important;
        }
        /* Eliminar scroll horizontal en los mensajes y forzar ajuste de palabra */
        div[data-testid="stChatMessage"] {
            word-break: break-word !important;
            overflow-wrap: anywhere !important;
            padding: 0.8rem !important;
        }
        div[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] {
            overflow-x: hidden !important;
        }
        div[data-testid="stChatMessage"] p, 
        div[data-testid="stChatMessage"] li {
            font-size: 0.88rem !important;
            line-height: 1.5 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Inicializar historial en session_state si no existe
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "assistant", "content": "Soy tu asistente de **EcoPulse**. Estoy conectado a los datos en pantalla y a conocimientos de salud ambiental global. ¿En qué puedo ayudarte?"}
        ]

    # Contexto dinámico actual
    context = st.session_state.get("current_pollution_context", {})

    with st.expander("**Asistente EcoPulse IA**", icon=":material/smart_toy:", expanded=True):
        # Botón destacado para abrir el modo de pantalla amplia
        if st.button("Abrir en Pantalla Amplia (Modo Lectura)", icon=":material/open_in_full:", key="open_large_chat_btn", use_container_width=True, help="Abre el asistente en una ventana ancha para leer cómodamente sin barras de desplazamiento estrechas."):
            show_chat_dialog(context)

        # Contenedor de mensajes con altura mejorada
        chat_container = st.container(height=390)
        
        with chat_container:
            for message in st.session_state["chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Preguntas sugeridas de 1 clic (chips)
        chip_col1, chip_col2 = st.columns(2)
        chip_prompt = None
        with chip_col1:
            if st.button("¿Cómo está el aire?", icon=":material/air:", key="chip_aire", use_container_width=True):
                chip_prompt = "¿Cómo está la calidad del aire según los datos actuales en pantalla?"
        with chip_col2:
            if st.button("Riesgos a la salud", icon=":material/health_and_safety:", key="chip_salud", use_container_width=True):
                chip_prompt = "¿Cuáles son los principales riesgos de salud con los contaminantes actuales?"

        # Entrada del usuario en la barra lateral
        user_input = st.chat_input("Pregunta sobre los datos...", key="chat_user_input")
        active_prompt = chip_prompt if chip_prompt else user_input

        if active_prompt:
            # 1. Guardar mensaje del usuario
            st.session_state["chat_history"].append({"role": "user", "content": active_prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(active_prompt)
                    
            # 2. Generar y transmitir respuesta con feedback visual inmediato
            with chat_container:
                with st.chat_message("assistant"):
                    loading_placeholder = st.empty()
                    loading_placeholder.caption(":material/hourglass_top: Consultando datos...")
                    
                    def stream_with_loader():
                        cleared = False
                        try:
                            for chunk in generate_chat_response(
                                messages=st.session_state["chat_history"],
                                context_data=context
                            ):
                                if not cleared:
                                    loading_placeholder.empty()
                                    cleared = True
                                yield chunk
                        finally:
                            loading_placeholder.empty()

                    response_text = st.write_stream(stream_with_loader())
                    if not response_text:
                        response_text = "No se pudo obtener una respuesta en este momento. Por favor reintenta tu pregunta."
                        st.markdown(response_text)
            
            # 3. Guardar respuesta del asistente en el historial
            st.session_state["chat_history"].append({"role": "assistant", "content": response_text})

        # Botón para limpiar conversación
        if len(st.session_state["chat_history"]) > 1:
            if st.button("Limpiar historial", icon=":material/delete:", key="clear_chat_history", use_container_width=True):
                st.session_state["chat_history"] = [
                    {"role": "assistant", "content": "Historial reiniciado. ¿En qué más puedo ayudarte con los datos de EcoPulse?"}
                ]
                st.rerun()
