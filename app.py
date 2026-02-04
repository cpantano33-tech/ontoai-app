import streamlit as st
from openai import OpenAI

# --- 1. CONFIGURACIÓN VISUAL (LOOK & FEEL) ---
st.set_page_config(
    page_title="OntoAI", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="collapsed" # Oculta la barra lateral por defecto
)

# CSS PROFESIONAL: Oculta marcas de agua, menús y bordes para "Efecto App"
hide_st_style = """
<style>
    #MainMenu {visibility: hidden;} /* Oculta menú hamburguesa */
    footer {visibility: hidden;}    /* Oculta 'Made with Streamlit' */
    header {visibility: hidden;}    /* Oculta barra superior de colores */
    
    /* Estilo para el input del chat */
    .stChatInput {
        border-radius: 20px;
    }
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. GESTIÓN DE SEGURIDAD AUTOMÁTICA ---
# El sistema busca la llave en la nube primero
if "OPENAI_API_KEY" in st.secrets:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
else:
    # Fallback: Si no está en la nube, la pide manual (útil para pruebas locales)
    openai_api_key = st.sidebar.text_input("🔑 API Key", type="password")

# --- 3. CEREBRO ONTOLÓGICO V3 (Validado) ---
SYSTEM_PROMPT = """
ROL: Eres un Coach Ontológico Senior.
OBJETIVO: Cuidar el SER antes de diseñar el HACER.

FASES DE INTERVENCIÓN:
1. DETECTAR: Si hay emoción intensa (miedo, ira, ansiedad), DETENTE. No pidas hechos todavía. Indaga la Columna Izquierda (Rumia mental).
2. MEDIR: Pregunta explícitamente "¿Del 1 al 10 cuanta [emoción] sientes?".
3. DECIDIR: 
   - Si > 6: STOP. Sugiere respiración, pausa o coach humano.
   - Si < 6: Avanza a diseñar la conversación distinguiendo HECHOS de JUICIOS.
"""

# --- 4. INTERFAZ DE USUARIO (UI) ---
st.title("🧠 OntoAI")
st.caption("Tu espacio de diseño conversacional.")

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hola. Soy tu espacio de reflexión. ¿Qué conversación difícil te está dando vueltas hoy?"}]

# Mostrar chat con Avatares
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.chat_message("assistant", avatar="🧠").write(msg["content"])
    else:
        st.chat_message("user", avatar="👤").write(msg["content"])

# --- 5. LÓGICA DEL CHAT ---
if prompt := st.chat_input("Escribe aquí lo que te pasa..."):
    # Validación de seguridad
    if not openai_api_key:
        st.info("💡 Configuración necesaria: Agrega tu API Key en los 'Secrets' del panel de control.")
        st.stop()
    
    # Procesamiento
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)

    client = OpenAI(api_key=openai_api_key)
    messages_for_ai = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
    
    with st.chat_message("assistant", avatar="🧠"):
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_for_ai,
            stream=True,
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
