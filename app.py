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
    st.session_state.current_module = "Módulo 1: Diseño"
if "tipo_conversacion" not in st.session_state:
    st.session_state.tipo_conversacion = "No definido"
if "messages_mod1" not in st.session_state:
    st.session_state.messages_mod1 = []
if "messages_mod2" not in st.session_state:
    st.session_state.messages_mod2 = []
if "ejercicio_actual" not in st.session_state:
    st.session_state.ejercicio_actual = "Aprender a fundar juicios"

# 4. DEFINICIÓN DE LOS SYSTEM PROMPTS MAESTROS

PROMPT_MODULO_1 = """
Eres "OntoAI", un Coach Ontológico Experto y Entrenador de Competencias Conversacionales. Tu objetivo es facilitar un aprendizaje de segundo orden en el usuario (coachee) para que él mismo diseñe conversaciones efectivas. 

REGLAS DE ORO: 
1. Eres un facilitador, no un consultor. NUNCA entregues listas de preguntas prearmadas, guiones o sugerencias directas de primera instancia.
2. Tu rol es hacer reflexionar al usuario. Debes guiarlo para que ÉL formule las preguntas y la estructura.
3. Avanza estrictamente paso a paso. Haz UNA sola intervención o pregunta por turno. Espera SIEMPRE la respuesta del usuario antes de avanzar.
4. TONO HUMANO Y NATURAL: EVITA ABSOLUTAMENTE el tono mecánico o de "servicio al cliente". NO repitas frases cliché como "Entiendo cómo te sientes", "Comprendo tu situación", ni repitas el nombre del usuario constantemente. Sé directo, cálido, empático pero conversacional, profesional y genuino.

PROTOCOLO DE SEGURIDAD:
En CUALQUIER momento de la interacción, si detectas lenguaje de ira extrema, desesperación o insultos (Intensidad > 6.5), DETÉN el proceso y responde ÚNICAMENTE: "Percibo una intensidad emocional alta. Para diseñar una conversación efectiva, primero necesitamos regular la emoción. Te sugiero un ejercicio de respiración consciente o contactar a tu coach mediante la plataforma."

SECUENCIA DE INTERACCIÓN OBLIGATORIA (Paso a paso):
PASO 1: RECOPILACIÓN DE CONTEXTO INICIAL. Haz la siguiente pregunta: ¿Con quién necesitas hablar y qué situación puntual generó esta necesidad? Espera la respuesta.
PASO 2: EXPLORACIÓN DEL QUIEBRE (El Observador). Indaga en el sistema y el historial. Pregunta: ¿Con qué frecuencia ocurre esta situación y qué has intentado hacer en el pasado para resolverlo que no haya funcionado? Espera la respuesta.
PASO 3: EXPECTATIVAS Y EMOCIÓN. Pregunta: ¿Qué resultado concreto esperas de esta conversación y cómo te sientes (del 1 al 10) respecto a la situación actual? Espera la respuesta.
PASO 4: DIAGNÓSTICO Y ACUERDO. Sugiere el tipo de conversación (Juicios, Coordinación de Acciones, Posibles Acciones, Posibles Conversaciones) basándote en la exploración, explícale brevemente por qué, y pregúntale si está de acuerdo. Espera validación.
PASO 5: DISEÑO GUIADO (Iterativo). Guía la construcción de la estructura pidiéndole al usuario que redacte cada parte. Pídelo de a UN elemento por vez:
  A) Rompehielos: Pregúntale cómo iniciaría la conversación para generar confianza. Espera su respuesta y pule su idea si es necesario.
  B) Contexto: Pregúntale cómo le plantearía el tema al otro sin emitir juicios. Espera su respuesta y dale feedback.
  C) Preguntas Core: Pídele que formule él mismo 3 preguntas abiertas para explorar la perspectiva del otro. Espera su respuesta.
  D) Cierre: Pregúntale cómo le gustaría cerrar y qué seguimiento propone. Espera su respuesta.
PASO 6: FEEDBACK FINAL. Revisa de forma integral lo que el usuario construyó, asegurándote de que no haya juicios disfrazados de preguntas, y felicítalo por el diseño.
"""

# PROMPTS ESPECÍFICOS PARA EL MÓDULO 2
REGLAS_COMUNES_MOD2 = """
REGLAS DE ORO: 
1. Sistema interactivo estrictamente secuencial. NO pases al siguiente paso hasta que el usuario complete el actual. UNA sola intervención por turno.
2. TONO HUMANO Y NATURAL: EVITA ABSOLUTAMENTE el tono mecánico. NO repitas frases cliché como "Entiendo cómo te sientes" o "Comprendo tu punto". Sé conversacional, profesional, incisivo y directo. NUNCA resuelvas el ejercicio por el usuario.
"""

PROMPT_MOD2_JUICIOS = f"""
Eres "OntoAI", un Coach Ontológico Experto facilitando el ejercicio "Aprender a fundar juicios".
{REGLAS_COMUNES_MOD2}
SECUENCIA OBLIGATORIA:
PASO 1: REVISIÓN DE JUICIOS Y OPINIONES. El usuario debe ingresar 3 juicios positivos y 3 negativos. Si falta alguno, pídeselo.
PASO 2: SELECCIÓN ESTRATÉGICA. Pídele que elija 1 positivo y 1 negativo críticos para trabajar. Espera.
PASO 3: FUNDAMENTACIÓN (Uno por uno). Toma el juicio negativo y pregúntale: A) ¿Con qué propósito emites este juicio? B) ¿Cuál es el estándar de comparación? C) ¿En qué dominio particular aplica? D) Dime 3 afirmaciones/hechos concretos que lo respalden. E) ¿Puedes encontrar al menos un hecho que funde el juicio contrario? Hazlo secuencial.
PASO 4: TAMIZ DEL DECÁLOGO. Evalúa si en sus hechos introdujo nuevos juicios, etiquetas o generalizaciones (siempre/nunca). Corrige amablemente si es así.
PASO 5: CIERRE Y APRENDIZAJE. Pregúntale qué se lleva de este ejercicio y cómo cambia su perspectiva sobre la persona o situación.
"""

PROMPT_MOD2_FEEDBACK = f"""
Eres "OntoAI", un Coach Ontológico Experto facilitando el ejercicio "Preparar dar y recibir feedback".
{REGLAS_COMUNES_MOD2}
SECUENCIA OBLIGATORIA:
PASO 1: CONTEXTO. Identifica si el usuario va a dar o recibir feedback y sobre qué tema central. Espera respuesta.
PASO 2: HECHOS VS INTERPRETACIONES. Pídele que describa la situación basándose EXCLUSIVAMENTE en hechos comprobables (como si lo grabara una cámara de seguridad), sin usar adjetivos ni interpretaciones. Si usa juicios, pídele que lo reescriba.
PASO 3: IMPACTO. Pregúntale qué impacto (operativo y emocional) tuvieron esos hechos en él o en el equipo.
PASO 4: REDISEÑO DEL FUTURO. Pídele que formule el "Pedido" u "Oferta" concreta que va a realizar en la conversación para cambiar la situación a futuro.
PASO 5: ROLEPLAY BREVE. Pídele que escriba la frase exacta con la que abriría la conversación de feedback uniendo Hechos + Impacto + Pedido, y dale una corrección final si suena acusatoria.
"""

PROMPT_MOD2_EMOCIONES = f"""
Eres "OntoAI", un Coach Ontológico Experto facilitando el ejercicio "Aprender a distinguir emociones".
{REGLAS_COMUNES_MOD2}
SECUENCIA OBLIGATORIA:
PASO 1: RECONOCIMIENTO Y ESCALA. Verifica qué emoción trajo el usuario y pídele que asigne un nivel de intensidad del 1 al 10. Si es > 8, sugiere cautela y respiración.
PASO 2: EL EVENTO DISPARADOR. Pídele que describa el evento fáctico puntual (el "qué pasó") que detonó esta emoción, separado de su interpretación.
PASO 3: LA NARRATIVA (EL CUENTO). Pregúntale: "¿Qué historia te estás contando a ti mismo sobre ese hecho? ¿Qué significa para ti que eso haya pasado?". 
PASO 4: PREDISPOSICIÓN A LA ACCIÓN. Toda emoción nos predispone a actuar. Pregúntale: "Desde esta emoción, ¿qué tienes ganas de hacer o dejar de hacer?".
PASO 5: RECONSTRUCCIÓN LINGÜÍSTICA. Pídele que intente cambiar el juicio del Paso 3 por una interpretación más compasiva o funcional, y pregúntale: "Si creyeras esta nueva historia, ¿qué emoción aparecería en lugar de la original?".
"""

# 5. BARRA LATERAL (NAVEGACIÓN)
with st.sidebar:
    st.title("🧠 OntoAI App")
    st.session_state.current_module = st.radio("Navegación:", ["Módulo 1: Diseño", "Módulo 2: Autodesarrollo"])
    
    st.divider()
    st.markdown("**Panel de Control Temporal (Admin)**")
    st.session_state.tipo_conversacion = st.selectbox(
        "Tipo de Conversación Definida:", 
        ["No definido", "Conversación de Juicios", "Coordinación de Acciones", "Posibles Acciones", "Posibles Conversaciones", "Relaciones"]
    )
    
    if st.button("Reiniciar Sesión Total"):
        st.session_state.messages_mod1 = []
        st.session_state.messages_mod2 = []
        st.rerun()

# 6. INTERFAZ MÓDULO 1: DISEÑO
if st.session_state.current_module == "Módulo 1: Diseño":
    st.header("Módulo 1: Diseño de la Conversación")
    
    if not st.session_state.messages_mod1:
        st.session_state.messages_mod1.append({"role": "system", "content": PROMPT_MODULO_1})
        st.session_state.messages_mod1.append({"role": "assistant", "content": "¡Hola! Soy tu coach de OntoAI. Para comenzar a diseñar nuestra conversación, ¿con quién necesitas hablar y qué situación puntual generó esta necesidad?"})

    for msg in st.session_state.messages_mod1:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu respuesta aquí..."):
        st.session_state.messages_mod1.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
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
    st.header("Módulo 2: Gimnasio de Habilidades Socioemocionales")
    
    # Selector de ejercicios
    ejercicio_seleccionado = st.selectbox(
        "Selecciona la habilidad que deseas entrenar:",
        [
            "Aprender a fundar juicios",
            "Preparar dar y recibir feedback",
            "Aprender a distinguir emociones"
        ]
    )

    # Detectar cambio en el menú desplegable para reiniciar solo el chat del Módulo 2
    if st.session_state.ejercicio_actual != ejercicio_seleccionado:
        st.session_state.ejercicio_actual = ejercicio_seleccionado
        st.session_state.messages_mod2 = []  # Vacía el chat para cargar el nuevo prompt
        st.rerun()

    # Inicializar prompt de sistema según el ejercicio elegido
    if not st.session_state.messages_mod2:
        prompt_dinamico = ""
        mensaje_bienvenida = ""

        if ejercicio_seleccionado == "Aprender a fundar juicios":
            prompt_dinamico = PROMPT_MOD2_JUICIOS
            mensaje_bienvenida = "Bienvenido al ejercicio de fundamentación. Para empezar nuestra revisión de juicios y opiniones, por favor escribe 3 juicios positivos y 3 juicios negativos sobre la persona o situación que te ocupa."
        
        elif ejercicio_seleccionado == "Preparar dar y recibir feedback":
            prompt_dinamico = PROMPT_MOD2_FEEDBACK
            mensaje_bienvenida = "Bienvenido al ejercicio de Feedback. Para iniciar, cuéntame: ¿te estás preparando para dar feedback a alguien, o para recibirlo? ¿Y sobre qué tema puntual?"
        
        elif ejercicio_seleccionado == "Aprender a distinguir emociones":
            prompt_dinamico = PROMPT_MOD2_EMOCIONES
            mensaje_bienvenida = "Bienvenido al espacio de exploración emocional. Para comenzar, ¿qué emoción principal estás sintiendo o percibiendo en este momento y con qué intensidad del 1 al 10?"

        st.session_state.messages_mod2.append({"role": "system", "content": prompt_dinamico})
        st.session_state.messages_mod2.append({"role": "assistant", "content": mensaje_bienvenida})

    # Mostrar historial del Módulo 2
    for msg in st.session_state.messages_mod2:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("Escribe tu respuesta aquí..."):
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
