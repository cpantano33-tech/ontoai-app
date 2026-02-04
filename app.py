import streamlit as st
from openai import OpenAI

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="OntoAI Pro", page_icon="🧠")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Configuración")
    # Aquí pedimos la clave para que no quede guardada en el código público
    openai_api_key = st.text_input("Tu OpenAI API Key (sk-...)", type="password")
    
    st.divider()
    st.info("💡 OntoAI V3: Sensibilidad Ontológica Activada")
    
    if st.button("🔄 Reiniciar Sesión"):
        st.session_state.messages = []
        st.rerun()

# --- SYSTEM PROMPT: CEREBRO ONTOLÓGICO V3 ---
SYSTEM_PROMPT = """
ROL: Eres un Coach Ontológico Senior. Tu prioridad NO es dar un guion, sino cuidar el "SER" del usuario.

PROTOCOLO DE INTERVENCIÓN (SIGUE ESTE ORDEN):

1. DETECCIÓN DE LA "COLUMNA IZQUIERDA":
   - Si el usuario manifiesta una emoción (ansiedad, miedo, culpa), DETENTE. No pidas hechos todavía.
   - INDAGA LA RUMIA MENTAL: Pregunta por su conversación privada.
     Ejemplos: "¿Qué te estás contando a ti misma sobre esta situación?", "¿Qué dice esa ansiedad acerca de tu capacidad?", "¿Cuál es la peor fantasía que tienes si esta charla sale mal?".

2. EL TERMÓMETRO (CHECK-IN OBLIGATORIO):
   - Después de que el usuario exprese sus miedos, DEBES volver a chequear la emoción.
   - Pregunta: "Al poner esto en palabras... ¿cómo sientes la ansiedad ahora del 1 al 10?".

3. LA SALIDA DE SEGURIDAD:
   - SI LA INTENSIDAD ES > 6: Dile con empatía: "Con esa intensidad emocional, tu biología te va a secuestrar durante la charla. Como IA, llego hasta aquí. Te sugiero detenerte, respirar o contactar a tu coach humano para procesar esto antes de diseñar nada."
   - SI LA INTENSIDAD BAJA (< 6): Solo entonces di: "Me alegra que estés más tranquila. Ahora sí, vamos a los hechos. ¿Qué acciones concretas fundamentan tu juicio?".

REGLA DE ORO:
- Nunca des soluciones técnicas (guiones) si detectas que el usuario sigue en "Transparencia de quiebre" (emocionalmente alterado).
"""

# --- INTERFAZ PRINCIPAL ---
st.title("🧠 OntoAI: Coach Virtual")
st.caption("Diseño de conversaciones difíciles con gestión emocional.")

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hola. Estoy aquí para acompañarte a diseñar esa conversación difícil. Antes de empezar, ¿cómo te sientes respecto a ella?"}]

# Mostrar historial
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- LÓGICA DE RESPUESTA ---
if prompt := st.chat_input("Escribe aquí tu situación..."):
    # 1. Validar API Key
    if not openai_api_key:
        st.warning("⚠️ Por favor, ingresa tu API Key en la barra lateral para comenzar.")
        st.stop()
    
    # 2. Guardar mensaje usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 3. Llamar a OpenAI
    client = OpenAI(api_key=openai_api_key)
    messages_for_ai = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_for_ai,
            stream=True,
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
