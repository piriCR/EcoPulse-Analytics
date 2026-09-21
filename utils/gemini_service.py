import os
import streamlit as st
import google.generativeai as genai

def init_gemini():
    """Initializes the Gemini API client using the key from environment or secrets."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        try:
            if hasattr(st, "secrets"):
                api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None
            
    if not api_key:
        st.error("No se encontró la API Key de Gemini. Por favor configura GEMINI_API_KEY en tu archivo .env", icon=":material/warning:")
        return False
        
    genai.configure(api_key=api_key)
    return True

def build_system_instruction(context_data: dict) -> str:
    """Builds an optimized, compact system instruction prompt for fast response times."""
    page_name = context_data.get("page_name", "General") if context_data else "General"
    
    context_str = f"PÁGINA ACTUAL: {page_name}\n"
    if context_data:
        context_str += "DATOS CLAVE EN PANTALLA:\n"
        for key, value in context_data.items():
            if key in ("page_name", "critical_pollutants"):
                continue
            if hasattr(value, "to_dict"):
                try:
                    if "city_name" in value.columns and "AQI" in value.columns:
                        summary_items = []
                        for _, r in value.head(5).iterrows():
                            summary_items.append(f"- {r.get('city_name', '')}: AQI={r.get('AQI', '')}, Riesgo={r.get('Riesgo', '')}, Dominante={r.get('Dominante', '')}")
                        context_str += "- Resumen ciudades:\n" + "\n".join(summary_items) + "\n"
                        continue
                except Exception:
                    pass
            val_str = str(value)
            if len(val_str) > 300:
                val_str = val_str[:300] + "..."
            context_str += f"- {key}: {val_str}\n"

    instruction = f"""
    Eres un Científico de Datos Ambientales y Especialista en Salud Pública Global en 'EcoPulse-Analytics'.

    DIRECTIVAS DE RESPUESTA:
    1. SÉ DIRECTO Y CONCISO: Prohibidas introducciones ceremoniosas, despedidas o disclaimers repetitivos. Ve directo al dato y a las conclusiones.
    2. FORMATO EN VIÑETAS: Responde en 2 a 4 viñetas breves y claras con palabras clave y cifras en **negrita** (máximo 120 palabras).
    3. RIESGOS A LA SALUD: Si preguntan sobre riesgos de salud de contaminantes (PM2.5, PM10, NO2, O3, SO2, CO), detalla directamente los efectos respiratorios, cardiovasculares y grupos de riesgo para cada contaminante relevante.
    4. MORTALIDAD Y CIUDADES: Si preguntan sobre salud, mortalidad o ciudades del mundo (ej. Nueva Delhi, Santiago, etc.), responde directamente con las estimaciones reconocidas (OMS / GBD). NUNCA digas que no tienes datos por no estar en pantalla.
    5. MEDICIONES EN PANTALLA: Si preguntan específicamente por datos del dashboard ("hoy", "en pantalla", "actual"), usa DATOS CLAVE EN PANTALLA.

    {context_str}
    """
    return instruction

def _extract_chunk_text(chunk) -> str:
    """Safely extracts text from a streaming chunk, handling candidates, parts, and filtering thoughts."""
    texts = []
    if hasattr(chunk, "candidates") and chunk.candidates:
        for cand in chunk.candidates:
            if hasattr(cand, "content") and hasattr(cand.content, "parts"):
                for part in cand.content.parts:
                    if getattr(part, "thought", False):
                        continue
                    t = getattr(part, "text", None)
                    if t:
                        texts.append(t)
    if texts:
        return "".join(texts)
    try:
        return chunk.text or ""
    except Exception:
        return ""

def generate_chat_response(messages: list, context_data: dict):
    """Generates a rapid streaming response from Gemini using direct generate_content and low-latency models."""
    if not init_gemini():
        yield "**Error:** No se encontró la clave de API `GEMINI_API_KEY` en el archivo `.env` o en los secretos de Streamlit."
        return

    # Modelos ultrarrápidos: Flash-Lite primero (sin latencia de pensamiento)
    models_to_try = [
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash"
    ]
    system_instruction = build_system_instruction(context_data)
    
    generation_config = {
        "temperature": 0.2,
        "max_output_tokens": 400,
    }
    
    # Configurar filtros de seguridad permisivos para salud pública
    safety_settings = {
        genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
        genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
        genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
        genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
    }
    
    # Limpiar y formatear el historial asegurando alternancia usuario/modelo
    history_to_format = messages[:-1] if messages else []
    first_user_idx = next((i for i, m in enumerate(history_to_format) if m.get("role") == "user"), None)
    if first_user_idx is not None:
        history_to_format = history_to_format[first_user_idx:]
    else:
        history_to_format = []
        
    formatted_contents = []
    last_role = None
    for msg in history_to_format:
        content = msg.get("content", "").strip()
        if not content or content.startswith("**Error") or content.startswith("No se pudo") or content.startswith("Has alcanzado"):
            continue
        role = "model" if msg["role"] == "assistant" else "user"
        if role != last_role:
            formatted_contents.append({
                "role": role,
                "parts": [content]
            })
            last_role = role

    if formatted_contents and formatted_contents[-1]["role"] == "user":
        formatted_contents = formatted_contents[:-1]

    latest_message = messages[-1]["content"] if messages else ""
    formatted_contents.append({
        "role": "user",
        "parts": [latest_message]
    })

    response_yielded = False
    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            response = model.generate_content(formatted_contents, stream=True)
            
            for chunk in response:
                text_piece = _extract_chunk_text(chunk)
                if text_piece:
                    response_yielded = True
                    yield text_piece
                    
            if response_yielded:
                return
        except Exception as e:
            last_error = e
            continue

    if not response_yielded:
        err_msg = str(last_error) if last_error else "Error de conexión con la IA"
        if "429" in err_msg or "ResourceExhausted" in err_msg:
            yield "Has alcanzado temporalmente el límite de consultas de la cuota gratuita de Gemini. Por favor espera un minuto y vuelve a intentarlo."
        else:
            yield f"No se pudo completar la consulta: {err_msg}"



