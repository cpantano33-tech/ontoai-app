import streamlit as st
from openai import OpenAI

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
st.set_page_config(page_title="OntoAI - Coachee", page_icon="🧠", layout="centered")

# Ocultar marcas de agua por defecto de Streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 2. CONFIGURACIÓN DEL CLIENTE OPENAI
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.warning("Por favor, configura tu OPENAI_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 3. GESTIÓN DEL ESTADO DE SESIÓN (Enrutador Lógico)
if "current_module" not in st.session_state:
    st.session_state.current_module = "Módulo 1"
if "tipo_conversacion" not in st.session_state:
    st.session_state.tipo_conversacion = "No definido"
if "messages_mod1" not in st.session_state:
    st.session_state.messages_mod1 = []
if "messages_mod2" not in st.session_state:
    st.session_state.messages_mod2 = []

# 4. DEFINICIÓN DE LOS SYSTEM PROMPTS MAESTROS

PROMPT_MODULO_1 = """
Eres "OntoAI", un Coach Ontológico Experto y Entrenador de Competencias Conversacionales. Tu objetivo es facilitar un aprendizaje de segundo orden en el usuario (coachee) para que él mismo diseñe conversaciones efectivas. 

REGLAS DE ORO: 
1. Eres un facilitador, no un consultor. NUNCA entregues listas de preguntas prearmadas, guiones o sugerencias directas de primera instancia.
2. Tu rol es hacer reflexionar al usuario. Debes guiarlo para que ÉL formule las preguntas y la estructura.
3. Avanza estrictamente paso a paso. Haz UNA sola intervención o pregunta por turno. Espera SIEMPRE la respuesta del usuario antes de avanzar.

PROTOCOLO DE SEGURIDAD:
En CUALQUIER momento de la interacción, si detectas lenguaje de ira extrema, desesperación o insultos (Intensidad > 6.5), DETÉN el proceso y responde ÚNICAMENTE: "Percibo una intensidad emocional alta. Para diseñar una conversación efectiva, primero necesitamos regular la emoción. Te sugiero un ejercicio de respiración consciente o contactar a tu coach mediante la plataforma."

SECUENCIA DE INTERACCIÓN OBLIGATORIA (Paso a paso):
PASO 1: RECOPILACIÓN DE CONTEXTO. Haz máximo 3 preguntas cortas: 1) ¿Con quién necesitas hablar y qué situación lo generó? 2) ¿Qué resultado concreto esperas? 3) ¿Cómo te sientes respecto a esta situación (del 1 al 10)? Espera la respuesta.
PASO 2: DIAGNÓSTICO Y ACUERDO. Sugiere el tipo de conversación (Juicios, Coordinación de Acciones, Posibles Acciones, Posibles Conversaciones) y pregúntale si está de acuerdo. Espera validación.
PASO 3: DISEÑO GUIADO (Iterativo). Guía la construcción de la estructura pidiéndole al usuario que redacte cada parte. Pídelo de a UN elemento por vez:
  A) Rompehielos: Pregúntale cómo iniciaría la conversación para generar confianza. Espera su respuesta y pule su idea si es necesario.
  B) Contexto: Pregúntale cómo le plantearía el tema al otro sin emitir juicios. Espera su respuesta y dale feedback.
  C) Preguntas Core: Pídele que formule él mismo 3 preguntas abiertas para explorar la perspectiva del otro. Espera su respuesta.
  D) Cierre: Pregúntale cómo le gustaría cerrar y qué seguimiento propone. Espera su respuesta.
PASO 4: FEEDBACK FINAL. Revisa de forma integral lo que el usuario construyó, asegurándote de que no haya juicios disfrazados de preguntas, y felicítalo por el diseño.
"""

PROMPT_MODULO_2 = """
Eres "OntoAI", un Coach Ontológico Experto. Estás a cargo del Módulo 2: Autodesarrollo. 
REGLA DE ORO: Sistema interactivo estrictamente secuencial. NO pases al siguiente paso hasta que el usuario complete el actual. UNA sola intervención por turno.

PROTOCOLO DE SEGURIDAD:
Si en el Paso 5 el usuario indica una intensidad emocional > 6.5, DETÉN el proceso: "Percibo una intensidad emocional alta que puede comprometer el resultado. Pausamos el diseño aquí. Te sugiero respiración consciente, revisar corporalidad, o solicitar asistencia a tu coach."

SECUENCIA OBLIGATORIA:
PASO 1: VACIADO MENTAL. Pídele 3 juicios positivos y 3 negativos cortos sobre la persona/situación. Espera.
PASO 2: SELECCIÓN ESTRATÉGICA. Pídele que elija 1 positivo y 1 negativo críticos. Espera.
PASO 3: FUNDAMENTACIÓN. Toma el negativo y haz las 5 preguntas (Propósito, Estándar, Dominio, 3 Hechos, Juicio contrario) de a UNA por vez. Luego repite con el positivo.
PASO 4: TAMIZ DEL DECÁLOGO. Evalúa si violó reglas (Etiquetado, Generalización, Adscripción de intenciones). Si hay error, hazlo notar empáticamente. Si no, avanza.
PASO 5: TERMÓMETRO EMOCIONAL. Pídele que nombre su emoción actual y la califique del 1 al 10. Evalúa con el umbral 6.5.
PASO 6: CIERRE. Si <= 6.5, indícale que su dominio es óptimo y puede exportar el resumen.
"""

# 5. BARRA LATERAL (NAVEGACIÓN)
with st.sidebar:
    st.title("🧠 OntoAI App")
    st.session_state.current_module = st.radio("Navegación:", ["Módulo 1: Diseño", "Módulo 2: Autodesarrollo"])
    
    st.divider()
    st.markdown("**Panel de Control Temporal (Admin)**")
    # Este selector manual simula la detección de la IA para cambiar el decálogo
    st.session_state.tipo_conversacion = st.selectbox(
        "Tipo de Conversación Definida:", 
        ["No definido", "Conversación de Juicios", "Coordinación de Acciones", "Posibles Acciones", "Posibles Conversaciones", "Relaciones"]
    )
    
    if st.button("Reiniciar Sesión"):
        st.session_state.messages_mod1 = []
        st.session_state.messages_mod2 = []
        st.rerun()

# 6. INTERFAZ MÓDULO 1: DISEÑO
if st.session_state.current_module == "Módulo 1: Diseño":
    st.header("Módulo 1: Diseño de la Conversación")
    
    # Inicializar prompt de sistema si el chat está vacío
    if not st.session_state.messages_mod1:
        st.session_state.messages_mod1.append({"role": "system", "content": PROMPT_MODULO_1})
        st.session_state.messages_mod1.append({"role": "assistant", "content": "¡Hola! Soy tu coach de OntoAI. Para comenzar a diseñar nuestra conversación, ¿con quién necesitas hablar y qué situación puntual generó esta necesidad?"})

    # Mostrar historial (omitiendo el system prompt)
    for msg in st.session_state.messages_mod1:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("Escribe tu respuesta aquí..."):
        st.session_state.messages_mod1.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            # Llamada a la API de OpenAI
            for response in client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages_mod1],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages_mod1.append({"role": "assistant", "content": full_response})

# 7. INTERFAZ MÓDULO 2: AUTODESARROLLO
elif st.session_state.current_module == "Módulo 2: Autodesarrollo":
    st.header("Módulo 2: Preparación y Autodesarrollo")
    
    # Lógica de inyección del decálogo correcto
    decalogo_contexto = ""
    if st.session_state.tipo_conversacion in ["Conversación de Juicios", "Coordinación de Acciones"]:
        decalogo_contexto = "REGLA ADICIONAL: Utiliza los principios del DECÁLOGO PARA ENTREGAR JUICIOS."
    elif st.session_state.tipo_conversacion in ["Posibles Acciones", "Posibles Conversaciones", "Relaciones"]:
        decalogo_contexto = "REGLA ADICIONAL: Utiliza los principios del DECÁLOGO PARA RECIBIR JUICIOS."

    prompt_dinamico_mod2 = PROMPT_MODULO_2 + "\n" + decalogo_contexto

    # Inicializar prompt de sistema si el chat está vacío
    if not st.session_state.messages_mod2:
        st.session_state.messages_mod2.append({"role": "system", "content": prompt_dinamico_mod2})
        st.session_state.messages_mod2.append({"role": "assistant", "content": "Bienvenido al espacio de autodesarrollo. Para empezar nuestro vaciado mental, por favor escribe 3 juicios positivos y 3 juicios negativos (frases cortas) sobre la persona o situación."})

    # Mostrar historial
    for msg in st.session_state.messages_mod2:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("Escribe tus juicios aquí..."):
        st.session_state.messages_mod2.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages_mod2],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages_mod2.append({"role": "assistant", "content": full_response})
