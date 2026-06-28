import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
import streamlit as st

def init_gemini():
    """Initializes the Gemini API client using the key from environment or secrets."""
    # Attempt to get API key from os.environ (loaded via python-dotenv) or st.secrets
    api_key = os.environ.get("GEMINI_API_KEY") or (st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None)
    
    if not api_key:
        st.error("⚠️ No se encontró la API Key de Gemini. Por favor configura GEMINI_API_KEY en tu archivo .env")
        return False
        
    genai.configure(api_key=api_key)
    return True

def build_system_instruction(context_data: dict) -> str:
    """Builds the system instruction prompt using the current application context."""
    if not context_data:
        return "Eres un experto ambiental analizando datos de calidad del aire. Responde de manera profesional, clara y concisa."

    page_name = context_data.get("page_name", "Desconocida")
    
    # Construir un resumen dinámico del contexto actual
    context_str = f"PÁGINA ACTUAL DEL USUARIO: {page_name}\n"
    context_str += "DATOS EN PANTALLA:\n"
    
    for key, value in context_data.items():
        if key == "page_name":
            continue
        
        if hasattr(value, "to_string"):
            # Es un DataFrame o Series
            val_str = value.to_string(index=False)
        elif isinstance(value, list) or isinstance(value, dict):
            val_str = str(value)
        else:
            val_str = str(value)
            
        context_str += f"- {key.replace('_', ' ').title()}:\n{val_str}\n\n"

    instruction = f"""
    Eres un Científico de Datos Ambientales Senior y asistente de IA en el dashboard 'EcoPulse-Analytics'.
    Tu objetivo es responder a las consultas del usuario basándote EXACTAMENTE en los datos que el usuario está viendo actualmente en la pantalla.
    
    {context_str}
    
    INSTRUCCIONES:
    1. Si el usuario te pregunta por datos, estadísticas o recomendaciones, básate EXCLUSIVAMENTE en la información proporcionada arriba (DATOS EN PANTALLA).
    2. Realiza un análisis profundo, estructurado y altamente experto. No des respuestas vagas o excesivamente cortas. Justifica tus conclusiones utilizando las cifras exactas del DataFrame y extrae insights valiosos (patrones, alertas, comparaciones).
    3. Usa formato Markdown avanzado (viñetas, negritas, tablas si es necesario) para darle estructura ejecutiva a tu respuesta.
    4. Explica el impacto en la salud de forma médica y detallada si es relevante según los niveles de contaminantes.
    5. Traduce siempre los acrónimos e indicadores a palabras sencillas que cualquier usuario entienda. Coloca primero la palabra clara y luego el indicador técnico original entre paréntesis (por ejemplo: "Partículas Finas (PM2.5)", "Calidad Buena (good)", "Monóxido de Carbono (CO)").
    """
    return instruction

def generate_chat_response(messages: list, context_data: dict):
    """Generates a response from Gemini using the chat history and dynamic context."""
    if not init_gemini():
        return "Error de configuración de la API."

    # Volvemos a "Flash" estándar, que ofrece excelente razonamiento y cuenta con cuota gratuita generosa.
    model_name = "gemini-2.5-flash"
    
    system_instruction = build_system_instruction(context_data)
    
    # Initialize the model with the system instruction
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction
    )
    
    # Convert Streamlit chat history format to Gemini format
    # Streamlit format: [{"role": "user"/"assistant", "content": "..."}]
    # Gemini format: [{"role": "user"/"model", "parts": ["..."]}]
    formatted_history = []
    # We exclude the last message which is the current prompt, to pass it to send_message
    history_to_format = messages[:-1] if messages else []
    
    for msg in history_to_format:
        role = "model" if msg["role"] == "assistant" else "user"
        formatted_history.append({
            "role": role,
            "parts": [msg["content"]]
        })

    try:
        # Start a chat session with history
        chat = model.start_chat(history=formatted_history)
        
        # Send the latest message
        latest_message = messages[-1]["content"] if messages else ""
        response = chat.send_message(latest_message, stream=True)
        
        for chunk in response:
            try:
                if chunk.text:
                    yield chunk.text
            except Exception:
                # Some chunks might not have text (e.g. safety blocks)
                pass
    except Exception as e:
        yield f"Ocurrió un error al consultar a Gemini: {str(e)}"

