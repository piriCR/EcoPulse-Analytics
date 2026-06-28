import streamlit as st
from utils.gemini_service import generate_chat_response

def render_global_chat():
    """Renders the chat interface using a native Streamlit popover button."""
    
    st.markdown(
        """
        <style>
        /* Desconecta la ventana del popover de su botón y la fuerza a la esquina inferior derecha */
        div[data-testid="stPopoverBody"] {
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            top: auto !important;
            left: auto !important;
            transform: none !important;
            width: 420px !important;
            max-width: 90vw !important;
            border-radius: 20px !important;
            box-shadow: 0 15px 40px rgba(0,0,0,0.4) !important;
            border: 1px solid rgba(128,128,128,0.2) !important;
            z-index: 999999 !important;
        }
        /* Estilos para el botón del Asistente IA */
        button[data-testid="baseButton-popover"] {
            background: linear-gradient(135deg, #10b981, #047857) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.4) !important;
            transition: all 0.3s ease !important;
            border-radius: 8px !important;
        }
        button[data-testid="baseButton-popover"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.5) !important;
            background: linear-gradient(135deg, #34d399, #059669) !important;
        }
        button[data-testid="baseButton-popover"] p {
            color: white !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
        }
        button[data-testid="baseButton-popover"] span.material-symbols-rounded {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize chat history in session state if it doesn't exist

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "assistant", "content": "Hola. Soy tu asistente de EcoPulse. ¿En qué te puedo ayudar analizando los datos actuales?"}
        ]

    # Create the native popover button with a Streamlit material icon and short text
    with st.popover("Asistente IA", icon=":material/auto_awesome:", width="stretch"):
        # Use HTML to avoid Streamlit's auto-generated anchor links on markdown headers
        st.html("<h3 style='margin-bottom:0; font-size:1.4rem;'>Asistente EcoPulse</h3>")
        st.caption("Consulta sobre los datos ambientales actuales.")
        
        # Container for chat messages to allow scrolling inside the panel
        chat_container = st.container(height=350)
        
        with chat_container:
            for message in st.session_state["chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Pregunta algo..."):
            # 1. Add user message to state and display
            st.session_state["chat_history"].append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
            # 2. Get dynamic context from session state (updated by monitoring.py)
            context = st.session_state.get("current_pollution_context", {})
            
            # 3. Fetch response from Gemini
            with chat_container:
                with st.chat_message("assistant"):
                    # El spinner ya no es tan necesario gracias al streaming, pero lo dejamos brevemente antes de la conexión
                    response_generator = generate_chat_response(
                        messages=st.session_state["chat_history"],
                        context_data=context
                    )
                    # st.write_stream consume el generador y devuelve el string final concatenado
                    response_text = st.write_stream(response_generator)
            
            # 4. Save response to state
            st.session_state["chat_history"].append({"role": "assistant", "content": response_text})

