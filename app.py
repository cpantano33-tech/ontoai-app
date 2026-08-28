import datetime
import tempfile
import os
from openai import OpenAI
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
st.set_page_config(
    page_title="DIALECTA - Simulador Conversacional", page_icon="💬", layout="wide"
)

# Estilos CSS avanzados para Tarjetas de Ejercicios y Look Inmersivo Claro
custom_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 1. FONDO ANIMADO LUMINOSO Y MODERNO */
    .stApp {
        background: linear-gradient(-45deg, #f0f4ff, #d9e2ec, #e0eafc, #cfdef3);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 2. EFECTO VIDRIO (GLASSMORPHISM) GENERAL */
    .module-card, .banner-legal {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        color: #1a1a1a;
    }

    /* 3. TARJETAS DE EJERCICIOS (MÓDULO 2) */
    .exercise-card-juicios {
        background: linear-gradient(135deg, rgba(255, 235, 238, 0.85), rgba(255, 205, 210, 0.6)) !important;
        border-left: 6px solid #e53935;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(229, 57, 53, 0.15);
    }
    .exercise-card-escucha {
        background: linear-gradient(135deg, rgba(227, 242, 253, 0.85), rgba(187, 222, 251, 0.6)) !important;
        border-left: 6px solid #1e88e5;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.15);
    }
    .exercise-card-relaciones {
        background: linear-gradient(135deg, rgba(232, 245, 233, 0.85), rgba(200, 230, 201, 0.6)) !important;
        border-left: 6px solid #43a047;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(67, 160, 71, 0.15);
    }

    /* 4. TARJETAS DE MÉTRICAS (B2B DASHBOARD) */
    .metric-card {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(0, 86, 179, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #0056b3;
    }

    /* 5. BOTONES MODERNOS */
    .stButton>button {
        background: linear-gradient(135deg, #0056b3, #00bfff) !important;
        border: none !important;
        color: #ffffff !important;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0, 191, 255, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 191, 255, 0.4);
    }
    
    /* 6. AJUSTES TEXTOS Y SIDEBAR */
    .banner-legal strong {
        color: #0056b3;
        font-size: 1.2em;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(240, 244, 255, 0.7) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.5);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 2. GESTIÓN DEL ESTADO DE SESIÓN (Enrutadores y Estados)
if "accepted_terms" not in st.session_state:
    st.session_state.accepted_terms = False
if "current_module" not in st.session_state:
    st.session_state.current_module = "Módulo 1: Diseño"
if "ejercicio_actual" not in st.session_state:
    st.session_state.ejercicio_actual = "Aprender a fundar juicios"
if "messages_mod1" not in st.session_state:
    st.session_state.messages_mod1 = []
if "messages_mod2_juicios" not in st.session_state:
    st.session_state.messages_mod2_juicios = []
if "messages_mod2_escucha" not in st.session_state:
    st.session_state.messages_mod2_escucha = []
if "messages_mod2_relaciones" not in st.session_state:
    st.session_state.messages_mod2_relaciones = []

# 3. PANTALLA DE BLOQUEO (BANNER OBLIGATORIO)
if not st.session_state.accepted_terms:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("LOGO DIALECTA OSCURO.jpeg", use_container_width=True) 

        st.markdown(
            """
        <div class="banner-legal">
            <strong>BIENVENIDO A DIALECTA,</strong><br><br>
            el simulador conversacional que te permite, a través del aprendizaje simulado, practicar y diseñar conversaciones de 1° orden, buscando mejorar tus habilidades genéricas conversacionales, mientras practicas diseños de indagaciones o armado de opiniones fundadas, monitoreando siempre tus emociones. El simulador podrá hacerte preguntas que buscan activar reflexiones, procurando que las tengas presentes, ya que éstas funcionan como condicionantes para la acción.<br><br>
            <strong>IMPORTANTE:</strong> DIALECTA NO BUSCA DIRIGIR TUS CONVERSACIONES YA QUE ESTAS SON RESPONSABILIDAD HUMANA Y/U ORGANIZACIONAL.<br><br>
            <strong>RECUERDA:</strong> ¡la práctica hace al maestro!
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("Comprendo y Acepto", type="primary"):
            st.session_state.accepted_terms = True
            st.rerun()
    st.stop()

# 4. CONFIGURACIÓN DEL CLIENTE OPENAI
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.warning("Por favor, configura tu OPENAI_API_KEY en los Secrets de Streamlit.")
    st.stop()

# Funciones auxiliares de Audio
def procesar_audio_usuario(audio_bytes):
    if not audio_bytes or len(audio_bytes) < 1000:
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
        fp.write(audio_bytes)
        fp_path = fp.name
        
    try:
        with open(fp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="es"
            )
        texto = transcript.text.strip()
        alucinaciones = ["Amara.org", "Subtítulos", "Subtitulos", "Traducido por"]
        if not texto or any(falso.lower() in texto.lower() for falso in alucinaciones):
            return None
        return texto
    except Exception:
        return None
    finally:
        os.remove(fp_path)

def generar_y_reproducir_voz(texto):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=texto
        )
        st.audio(response.content, format="audio/mp3", autoplay=True)
    except Exception:
        pass

# 5. PROMPTS DEL SISTEMA
PROMPT_MODULO_1 = """
Eres "Dialecta", un Coach Ontológico Experto y Entrenador de Competencias Conversacionales. Tu objetivo es facilitar un aprendizaje de segundo orden en el usuario (coachee) para que él mismo diseñe conversaciones efectivas. 
REGLAS DE ORO: 
1. Eres un facilitador, no un consultor. NUNCA entregues listas de preguntas prearmadas, guiones o sugerencias directas.
2. Tu rol es hacer reflexionar al usuario. Guíalo para que ÉL formule las preguntas y la estructura.
3. Avanza estrictamente paso a paso. Haz UNA sola intervención o pregunta por turno. Espera SIEMPRE la respuesta del usuario.
4. TONO HUMANO Y NATURAL: EVITA el tono mecánico. Sé directo, cálido, empático pero conversacional y profesional.
SECUENCIA DE INTERACCIÓN OBLIGATORIA (Paso a paso):
PASO 1: RECOPILACIÓN DE CONTEXTO INICIAL. ¿Con quién necesitas hablar y qué situación puntual generó esta necesidad?
PASO 2: EXPLORACIÓN DEL QUIEBRE. ¿Con qué frecuencia ocurre esta situación y qué has intentado hacer en el pasado que no funcionó?
PASO 3: EXPECTATIVAS Y EMOCIÓN. ¿Qué resultado concreto esperas de esta conversación y cómo te sientes respecto a la situación actual?
PASO 4: DIAGNÓSTICO Y ACUERDO. Sugiere el tipo de conversación basándote en la exploración y pregunta si está de acuerdo.
PASO 5: DISEÑO GUIADO (Iterativo). Guía la construcción pidiendo: A) Rompehielos B) Contexto sin juicios C) 3 Preguntas Core abiertas D) Cierre y seguimiento. Pide un elemento por vez.
PASO 6: FEEDBACK FINAL. Revisa de forma integral lo que construyó.
"""

REGLAS_COMUNES_MOD2 = """
REGLAS DE ORO: 
1. Sistema interactivo estrictamente secuencial. NO pases al siguiente paso hasta que el usuario complete el actual. UNA sola intervención por turno.
2. TONO HUMANO Y NATURAL: Conversacional, incisivo y directo. NUNCA resuelvas el ejercicio por el usuario.
"""

PROMPT_MOD2_JUICIOS = f"""
Eres "Dialecta", facilitando el ejercicio "Aprender a fundar juicios".
{REGLAS_COMUNES_MOD2}
SECUENCIA:
PASO 1: REVISIÓN DE JUICIOS. Pide al usuario 2 juicios positivos y 2 negativos sobre sí mismo o un tercero.
PASO 2: FUNDAMENTACIÓN. Dile que elija 1 que le cueste. Pídele que lo fundamente siguiendo esto: A) Propósito B) Estándar C) Dominio D) 3 afirmaciones/hechos E) Un hecho que funde el juicio contrario. (Hazlo paso a paso).
PASO 3: TAMIZ DEL DECÁLOGO. Evalúa su respuesta usando estos criterios: ¿Son etiquetas? ¿Tienen temporalidad del pasado? ¿Confunde lo que la persona 'hace' con lo que 'es'? Corrige amablemente.
PASO 4: CIERRE. Pregunta qué descubre de sí mismo tras este ejercicio.
"""

PROMPT_MOD2_ESCUCHA = f"""
Eres "Dialecta", facilitando el "Autodiagnóstico de la Escucha" (Basado en R. Echeverría).
{REGLAS_COMUNES_MOD2}
SECUENCIA:
PASO 1: LA BRECHA INEVITABLE. Pídele que piense en una reunión reciente donde el resultado no fue el esperado. Pregunta: ¿Consideras que tu habla fue efectiva si el resultado falló? (Recuérdale que la escucha valida el habla).
PASO 2: LA MÚSICA VS LA LETRA. Pregúntale: En esa reunión, ¿estuviste multitarea? ¿Cuánta información gestual o de tono ('la música') crees que perdiste?
PASO 3: LA INQUIETUD. Pídele que identifique a alguien de su equipo con quien la comunicación está bloqueada. Pregúntale: چه prejuicios tienes sobre esta persona antes de que hable?
PASO 4: EL RETO PRÁCTICO. Desafíalo para su próxima reunión: "Prohíbete dar soluciones los primeros 15 minutos. Tu único objetivo será descubrir su inquietud haciendo esta pregunta: 'Para entenderte mejor, ¿qué es lo que más te preocupa?'". Pídele que reflexione cómo se siente ante este reto.
"""

PROMPT_MOD2_RELACIONES = f"""
Eres "Dialecta", facilitando el ejercicio "Mapa de Relaciones Interpersonales".
{REGLAS_COMUNES_MOD2}
SECUENCIA:
PASO 1: ESPEJO. Pregúntale: ¿Hace cuánto no te miras realmente al espejo? ¿Qué cosas mejorarías de ti a nivel actitudinal?
PASO 2: EL MAPA. Pídele que liste mentalmente a 3 colegas clave. Para el primero, pídele que califique del 1 al 5: 1) Calidad de conversaciones, 2) Confianza, 3) Cuánto los escucha, 4) Cuánto siente que lo escuchan. Haz esto uno por uno.
PASO 3: ANÁLISIS. Pregúntale: Al ver estas métricas, ¿qué dice eso de ti mismo como líder?
PASO 4: PLAN DE ACERCAMIENTO. Pídele que elija al colega con peor puntuación y diseñen juntos una estrategia para acercarse explorando un punto de vista distinto.
"""

# 6. BARRA LATERAL (NAVEGACIÓN Y MARCA)
with st.sidebar:
    st.image("LOGO DIALECTA OSCURO.jpeg", use_container_width=True)

    st.markdown("### Navegación Principal")
    st.session_state.current_module = st.radio(
        "",
        [
            "Módulo 1: Diseño",
            "Módulo 2: Autodesarrollo",
            "Módulo 3: Coach en Línea",
            "Administración de Tableros (B2B)",
            "Exploraciones Autodiagnósticas",
            "Biblioteca",
        ],
        label_visibility="collapsed",
        key="menu_navegacion_principal"
    )

    st.divider()
    if st.button("Reiniciar Sesión Total"):
        st.session_state.messages_mod1 = []
        st.session_state.messages_mod2_juicios = []
        st.session_state.messages_mod2_escucha = []
        st.session_state.messages_mod2_relaciones = []
        st.rerun()

# 7. ENRUTADOR DE VISTAS PRINCIPALES

if st.session_state.current_module == "Módulo 1: Diseño":
    st.header("Módulo 1: Diseño de la Conversación")
    st.markdown("Entrenamiento inmersivo para estructurar tus conversaciones críticas.")

    if not st.session_state.messages_mod1:
        st.session_state.messages_mod1.append(
            {"role": "system", "content": PROMPT_MODULO_1}
        )
        mensaje_inicial = "¡Hola!, soy tu coach virtual. Para comenzar a diseñar nuestra conversación, es importante que me des el contexto y me cuentes qué te inquieta hoy y qué esperas lograr."
        st.session_state.messages_mod1.append(
            {"role": "assistant", "content": mensaje_inicial}
        )
        generar_y_reproducir_voz(mensaje_inicial)

    for msg in st.session_state.messages_mod1:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    col_input1, col_input2 = st.columns([1, 10])
    with col_input1:
        audio_bytes = audio_recorder(text="", icon_size="2x")
    with col_input2:
        prompt_text = st.chat_input("Escribe tu respuesta aquí...")

    prompt = procesar_audio_usuario(audio_bytes) if audio_bytes else prompt_text

    if prompt:
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
                full_response += response.choices[0].delta.content or ""
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            generar_y_reproducir_voz(full_response)
            
        st.session_state.messages_mod1.append(
            {"role": "assistant", "content": full_response}
        )

elif st.session_state.current_module == "Módulo 2: Autodesarrollo":
    st.header("Módulo 2: Gimnasio de Autodesarrollo")
    st.markdown("Selecciona una habilidad para entrenar de forma interactiva con Dialecta o descarga su plantilla de apoyo.")

    # TARJETAS DE EJERCICIOS ESTÉTICAS (SELECCIÓN)
    col_card1, col_card2, col_card3 = st.columns(3)

    with col_card1:
        st.markdown("""
        <div class="exercise-card-juicios">
            <h4>⚖️ Fundar Juicios</h4>
            <p>Evalúa tus opiniones, distingue hechos de etiquetas y aprende el decálogo ontológico.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Entrenar Juicios", key="btn_juicios"):
            st.session_state.ejercicio_actual = "Aprender a fundar juicios"
            st.rerun()

    with col_card2:
        st.markdown("""
        <div class="exercise-card-escucha">
            <h4>🎧 Mejorar la Escucha</h4>
            <p>Diagnostica tu brecha interpretativa y entrena la escucha de inquietudes genuinas.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Entrenar Escucha", key="btn_escucha"):
            st.session_state.ejercicio_actual = "Mejorar la escucha"
            st.rerun()

    with col_card3:
        st.markdown("""
        <div class="exercise-card-relaciones">
            <h4>🌐 Mapa de Relaciones</h4>
            <p>Analiza tu vínculo con colegas clave y diseña estrategias efectivas de acercamiento.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Entrenar Relaciones", key="btn_relaciones"):
            st.session_state.ejercicio_actual = "Mapa de relaciones interpersonales"
            st.rerun()

    st.divider()
    st.subheader(f"Entrenamiento Activo: {st.session_state.ejercicio_actual}")

    # Configuración de historial y prompt según la tarjeta activa
    if st.session_state.ejercicio_actual == "Aprender a fundar juicios":
        prompt_activo = PROMPT_MOD2_JUICIOS
        historial_activo = st.session_state.messages_mod2_juicios
        bienvenida_activa = "Bienvenido al ejercicio de fundamentación. Para empezar nuestra revisión, por favor escribe o graba 2 juicios positivos y 2 juicios negativos que tengas sobre ti mismo o sobre alguien de tu equipo."
    elif st.session_state.ejercicio_actual == "Mejorar la escucha":
        prompt_activo = PROMPT_MOD2_ESCUCHA
        historial_activo = st.session_state.messages_mod2_escucha
        bienvenida_activa = "Bienvenido al Autodiagnóstico de la Escucha. Piensa en una reunión reciente donde el resultado operativo no fue el que esperabas. ¿Consideras que tu forma de hablar fue efectiva si el resultado falló?"
    else:
        prompt_activo = PROMPT_MOD2_RELACIONES
        historial_activo = st.session_state.messages_mod2_relaciones
        bienvenida_activa = "Bienvenido al diseño de tu Mapa de Relaciones. Antes de evaluar a otros, hagamos un ejercicio de espejo: ¿Hace cuánto tiempo no te miras a nivel actitudinal para evaluarte internamente?"

    if not historial_activo:
        historial_activo.append({"role": "system", "content": prompt_activo})
        historial_activo.append({"role": "assistant", "content": bienvenida_activa})
        generar_y_reproducir_voz(bienvenida_activa)

    for msg in historial_activo:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Controles de entrada de voz y texto para el Gimnasio
    col_input1, col_input2 = st.columns([1, 10])
    with col_input1:
        audio_bytes_mod2 = audio_recorder(text="", icon_size="2x", key="mic_mod2")
    with col_input2:
        prompt_text_mod2 = st.chat_input("Escribe tu respuesta aquí...", key="input_mod2")

    prompt_mod2 = procesar_audio_usuario(audio_bytes_mod2) if audio_bytes_mod2 else prompt_text_mod2

    if prompt_mod2:
        historial_activo.append({"role": "user", "content": prompt_mod2})
        with st.chat_message("user"):
            st.markdown(prompt_mod2)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": m["role"], "content": m["content"]} for m in historial_activo],
                stream=True,
            ):
                full_response += response.choices[0].delta.content or ""
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            generar_y_reproducir_voz(full_response)
            
        historial_activo.append({"role": "assistant", "content": full_response})

elif st.session_state.current_module == "Administración de Tableros (B2B)":
    st.header("Panel de Control Organizacional (B2B)")
    st.markdown("Monitoreo ejecutivo de licencias corporativas, métricas de uso y retroalimentación de la red de observadores.")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown('<div class="metric-card"><p>Licencias Activas</p><div class="metric-value">48 / 50</div></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown('<div class="metric-card"><p>Tasa de Uso Semanal</p><div class="metric-value">84%</div></div>', unsafe_allow_html=True)
    with col_m3:
        st.markdown('<div class="metric-card"><p>Conversaciones Diseñadas</p><div class="metric-value">312</div></div>', unsafe_allow_html=True)
    with col_m4:
        st.markdown('<div class="metric-card"><p>Feedback de Red</p><div class="metric-value">4.8 / 5</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.subheader("👥 Progreso de Colaboradores")
        st.markdown("""
        * **María Gómez (Gerente de Operaciones):** Módulo 1 completado (4 simulaciones). *Tendencia positiva en gestión de quiebres.*
        * **Carlos Ruiz (Team Leader Comercial):** Gimnasio de Juicios activo. *Progreso: 75%*.
        * **Lucía Fernández (People Partner):** Mapa de Relaciones finalizado. *Pendiente feedback 360°*.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_tab2:
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.subheader("🔔 Red de Observadores y Solicitudes")
        st.markdown("Permite solicitar a pares o líderes de la red que califiquen las mejoras conversacionales del coachee.")
        
        with st.form("form_solicitud_red"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                colab_sel = st.selectbox("Colaborador evaluado", ["María Gómez", "Carlos Ruiz", "Lucía Fernández"])
            with col_s2:
                observador_email = st.text_input("Email del observador externo")
            
            mensaje_inv = st.text_area("Mensaje de solicitud de evaluación de desempeño conversacional")
            enviar_sol = st.form_submit_button("Enviar Solicitud a la Red")
            if enviar_sol:
                st.success(f"¡Solicitud enviada con éxito a {observador_email} para evaluar a {colab_sel}!")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_module == "Módulo 3: Coach en Línea":
    st.header("Módulo 3: Coach en Línea")
    st.markdown("Agenda tu sesión personalizada con un experto humano para profundizar en tus resultados del simulador.")

    st.markdown('<div class="module-card">', unsafe_allow_html=True)
    with st.form("agendamiento_form"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha preferida", min_value=datetime.date.today())
            horario = st.selectbox("Franja horaria", ["Mañana (9:00 - 12:00)", "Tarde (14:00 - 18:00)"])
        with col2:
            foco = st.selectbox("Tema principal a trabajar", ["Diseño de Conversación Crítica", "Gestión de Juicios", "Desarrollo de Escucha Activa", "Liderazgo y Relaciones"])
            comentarios = st.text_area("Comentarios adicionales")

        submitted = st.form_submit_button("Agendar Sesión")
        if submitted:
            st.success(f"¡Solicitud enviada! Nos pondremos en contacto para confirmar tu sesión el {fecha.strftime('%d/%m/%Y')} en el horario de {horario}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_module == "Exploraciones Autodiagnósticas":
    st.header("Exploraciones Autodiagnósticas")
    st.markdown("Evalúa tu punto de partida antes de iniciar el diseño de tus conversaciones.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="module-card">
            <h4>1. Cuestionario de Escucha Reactiva</h4>
            <p>Descubre tu brecha interpretativa en reuniones críticas y cómo afecta a tu equipo.</p>
            <button style="width:100%; padding:8px; border-radius:5px; background-color:#f0f2f6; border:1px solid #ccc; color: #333;">Iniciar Evaluación</button>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="module-card">
            <h4>2. Evaluación de Roles (Belbin)</h4>
            <p>Comprende cómo tus percepciones impactan en la dinámica de trabajo de tu equipo.</p>
            <button style="width:100%; padding:8px; border-radius:5px; background-color:#f0f2f6; border:1px solid #ccc; color: #333;">Iniciar Evaluación</button>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_module == "Biblioteca":
    st.header("Biblioteca de Distinciones")
    st.markdown("Material teórico y lecturas recomendadas para anclar los conceptos clave.")

    st.markdown("""
    <div class="module-card">
        <h3>📚 Lecturas Sugeridas</h3>
        <ul>
            <li><strong>Ontología del Lenguaje</strong> - Rafael Echeverría. <em>Capítulo sobre La Escucha como criterio de validación del habla.</em></li>
            <li><strong>Decálogo de Juicios:</strong> Los juicios hablan de lo que hace una persona y no de lo que es. Acción mata juicio.</li>
            <li><strong>El Mapa de la Inquietud:</strong> Herramientas para transformar la escucha reactiva en escucha generativa.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.download_button(
        label="Descargar Guía Rápida de Distinciones",
        data="Guía Rápida DIALECTA\n\n1. La Escucha valida el habla.\n2. Los Juicios pertenecen a quien los emite.\n3. Buscar la Inquietud del otro es el primer paso para coordinar acciones.",
        file_name="Distinciones_Dialecta.txt",
        mime="text/plain",
    )
