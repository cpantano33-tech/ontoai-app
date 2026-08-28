import datetime
from openai import OpenAI
import streamlit as st

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
st.set_page_config(
    page_title="DIALECTA - Simulador Conversacional", page_icon="💬", layout="wide"
)

# Estilos CSS personalizados para Dialecta (Tarjetas, botones y limpieza visual)
custom_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #0056b3;
        color: #0056b3;
    }
    .banner-legal {
        background-color: #f8f9fa;
        border-left: 5px solid #0056b3;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        font-size: 1.1em;
        color: #333;
    }
    .module-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 2. GESTIÓN DEL ESTADO DE SESIÓN (Enrutador y Banner)
if "accepted_terms" not in st.session_state:
    st.session_state.accepted_terms = False
if "current_module" not in st.session_state:
    st.session_state.current_module = "Módulo 1: Diseño"
if "ejercicio_actual" not in st.session_state:
    st.session_state.ejercicio_actual = "Aprender a fundar juicios"
if "messages_mod1" not in st.session_state:
    st.session_state.messages_mod1 = []
if "messages_mod2" not in st.session_state:
    st.session_state.messages_mod2 = []

# 3. PANTALLA DE BLOQUEO (BANNER OBLIGATORIO)
if not st.session_state.accepted_terms:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("LOGO DIALECTA OSCURO.jpeg", use_column_width=True)
        except:
            st.title("DIALECTA")

        st.markdown(
            """
        <div class="banner-legal">
            <strong>BIENVENIDO A DIALECTA,</strong><br><br>
            el simulador conversacional que te permite, a traves del aprendizaje simulado, practicar y diseñar conversaciones de 1° orden, buscando mejorar tus habilidades genericas conversacionaels, al mismo tiempo que podras practicar diseñarlas buscando impactar en los resultados.<br><br>
            <strong>IMPORTANTE:</strong> DIALECTA NO BUSCA DIRIGIR TUS CONVERSACIONES YA QUE ESTAS SON RESPONSABILIDAD HUMANA Y U ORGANIZACIONAL.<br><br>
            <strong>RECUERDA:</strong> la practica hace al maestro!
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("Comprendo y Acepto", type="primary"):
            st.session_state.accepted_terms = True
            st.rerun()
    st.stop()  # Detiene la ejecución del resto de la app hasta aceptar

# 4. CONFIGURACIÓN DEL CLIENTE OPENAI
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.warning("Por favor, configura tu OPENAI_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 5. DEFINICIÓN DE LOS SYSTEM PROMPTS MAESTROS
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
PASO 3: LA INQUIETUD. Pídele que identifique a alguien de su equipo con quien la comunicación está bloqueada. Pregúntale: ¿Qué prejuicios tienes sobre esta persona antes de que hable?
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
    try:
        st.image("LOGO DIALECTA CLARO.jpeg", use_column_width=True)
    except:
        st.title("DIALECTA")

    st.markdown("### Navegación Principal")
    st.session_state.current_module = st.radio(
        "",
        [
            "Módulo 1: Diseño",
            "Módulo 2: Autodesarrollo",
            "Módulo 3: Coach en Línea",
            "Exploraciones Autodiagnósticas",
            "Biblioteca",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    if st.button("Reiniciar Sesión Total"):
        st.session_state.messages_mod1 = []
        st.session_state.messages_mod2 = []
        st.rerun()

# 7. ENRUTADOR DE VISTAS PRINCIPALES

if st.session_state.current_module == "Módulo 1: Diseño":
    st.header("Módulo 1: Diseño de la Conversación")
    st.markdown("Entrenamiento inmersivo para estructurar tus conversaciones críticas.")

    if not st.session_state.messages_mod1:
        st.session_state.messages_mod1.append(
            {"role": "system", "content": PROMPT_MODULO_1}
        )
        st.session_state.messages_mod1.append(
            {
                "role": "assistant",
                "content": "Hola!, soy tu coach virtual. Para comenzar a diseñar nuestra conversación, es importante que me de el contexto y me cuentes que te inquieta hoy y que esperas lograr.",
            }
        )

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
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages_mod1
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.content or ""
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages_mod1.append(
            {"role": "assistant", "content": full_response}
        )

elif st.session_state.current_module == "Módulo 2: Autodesarrollo":
    st.header("Módulo 2: Gimnasio de Autodesarrollo")
    st.markdown(
        "Selecciona un ejercicio, complétalo en línea con Dialecta o descarga la plantilla para tu reflexión personal."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        ejercicio_seleccionado = st.selectbox(
            "Selecciona la habilidad que deseas entrenar:",
            [
                "Aprender a fundar juicios",
                "Mejorar la escucha",
                "Mapa de relaciones interpersonales",
            ],
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        # Generar plantillas descargables según el ejercicio
        if ejercicio_seleccionado == "Aprender a fundar juicios":
            plantilla = "# Plantilla: Aprender a fundar juicios\n\n1. Escribe 2 juicios positivos y 2 negativos:\n\n2. Elige uno y fundaméntalo:\n- Propósito:\n- Estándar:\n- Dominio:\n- 3 Hechos comprobables:\n- 1 Hecho contrario:\n\n3. Reflexión basada en el decálogo:"
        elif ejercicio_seleccionado == "Mejorar la escucha":
            plantilla = "# Plantilla: Autodiagnóstico de la Escucha (R. Echeverría)\n\n1. Piensa en una reunión reciente que falló. ¿Asumes la responsabilidad de la brecha interpretativa?\n\n2. ¿Qué prejuicios tienes sobre un colega con quien la comunicación está bloqueada?\n\n3. Reto de 15 min: Descubre su inquietud. ¿Qué descubriste al no dar soluciones inmediatas?"
        else:
            plantilla = "# Plantilla: Mapa de Relaciones\n\n| Colega | Relación | Calidad (1-5) | Confianza (1-5) | Cuánto Escucho (1-5) | Cuánto me Escuchan (1-5) |\n|---|---|---|---|---|---|\n| 1 | | | | | |\n| 2 | | | | | |\n| 3 | | | | | |\n\nReflexión: ¿Qué dice esto de ti como líder? Plan de acercamiento para la relación más baja:"

        st.download_button(
            label="Descargar Plantilla",
            data=plantilla,
            file_name=f"Plantilla_{ejercicio_seleccionado.replace(' ', '_')}.txt",
            mime="text/plain",
        )

    if st.session_state.ejercicio_actual != ejercicio_seleccionado:
        st.session_state.ejercicio_actual = ejercicio_seleccionado
        st.session_state.messages_mod2 = []
        st.rerun()

    if not st.session_state.messages_mod2:
        prompt_dinamico = ""
        mensaje_bienvenida = ""
        if ejercicio_seleccionado == "Aprender a fundar juicios":
            prompt_dinamico = PROMPT_MOD2_JUICIOS
            mensaje_bienvenida = "Bienvenido al ejercicio de fundamentación. Para empezar nuestra revisión, por favor escribe 2 juicios positivos y 2 juicios negativos que tengas sobre ti mismo o sobre alguien de tu equipo."
        elif ejercicio_seleccionado == "Mejorar la escucha":
            prompt_dinamico = PROMPT_MOD2_ESCUCHA
            mensaje_bienvenida = "Bienvenido al Autodiagnóstico de la Escucha. Para empezar, piensa en una reunión reciente donde el resultado operativo no fue el que esperabas. ¿Consideras que tu forma de hablar fue efectiva si, al final, el resultado falló?"
        elif ejercicio_seleccionado == "Mapa de relaciones interpersonales":
            prompt_dinamico = PROMPT_MOD2_RELACIONES
            mensaje_bienvenida = "Bienvenido al diseño de tu Mapa de Relaciones. Antes de evaluar a otros, hagamos un ejercicio de espejo: ¿Hace cuánto tiempo no te miras, no para ver tu aspecto, sino para evaluarte internamente? ¿Qué cosas mejorarías de ti a nivel actitudinal?"

        st.session_state.messages_mod2.append(
            {"role": "system", "content": prompt_dinamico}
        )
        st.session_state.messages_mod2.append(
            {"role": "assistant", "content": mensaje_bienvenida}
        )

    for msg in st.session_state.messages_mod2:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu respuesta aquí..."):
        st.session_state.messages_mod2.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages_mod2
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.content or ""
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages_mod2.append(
            {"role": "assistant", "content": full_response}
        )

elif st.session_state.current_module == "Módulo 3: Coach en Línea":
    st.header("Módulo 3: Coach en Línea")
    st.markdown(
        "Agenda tu sesión personalizada con un experto humano para profundizar en tus resultados del simulador."
    )

    st.markdown('<div class="module-card">', unsafe_allow_html=True)
    with st.form("agendamiento_form"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input(
                "Fecha preferida", min_value=datetime.date.today()
            )
            horario = st.selectbox(
                "Franja horaria",
                ["Mañana (9:00 - 12:00)", "Tarde (14:00 - 18:00)"],
            )
        with col2:
            foco = st.selectbox(
                "Tema principal a trabajar",
                [
                    "Diseño de Conversación Crítica",
                    "Gestión de Juicios",
                    "Desarrollo de Escucha Activa",
                    "Liderazgo y Relaciones",
                ],
            )
            comentarios = st.text_area("Comentarios adicionales")

        submitted = st.form_submit_button("Agendar Sesión")
        if submitted:
            st.success(
                f"¡Solicitud enviada! Nos pondremos en contacto para confirmar tu sesión el {fecha.strftime('%d/%m/%Y')} en el horario de {horario}."
            )
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_module == "Exploraciones Autodiagnósticas":
    st.header("Exploraciones Autodiagnósticas")
    st.markdown(
        "Evalúa tu punto de partida antes de iniciar el diseño de tus conversaciones."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
        <div class="module-card">
            <h4>1. Cuestionario de Escucha Reactiva</h4>
            <p>Descubre tu brecha interpretativa en reuniones críticas y cómo afecta a tu equipo.</p>
            <button style="width:100%; padding:8px; border-radius:5px; background-color:#f0f2f6; border:1px solid #ccc;">Iniciar Evaluación</button>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
        <div class="module-card">
            <h4>2. Evaluación de Roles (Belbin)</h4>
            <p>Comprende cómo tus percepciones impactan en la dinámica de trabajo de tu equipo.</p>
            <button style="width:100%; padding:8px; border-radius:5px; background-color:#f0f2f6; border:1px solid #ccc;">Iniciar Evaluación</button>
        </div>
        """,
            unsafe_allow_html=True,
        )

elif st.session_state.current_module == "Biblioteca":
    st.header("Biblioteca de Distinciones")
    st.markdown(
        "Material teórico y lecturas recomendadas para anclar los conceptos clave."
    )

    st.markdown(
        """
    <div class="module-card">
        <h3>📚 Lecturas Sugeridas</h3>
        <ul>
            <li><strong>Ontología del Lenguaje</strong> - Rafael Echeverría. <em>Capítulo sobre La Escucha como criterio de validación del habla.</em></li>
            <li><strong>Decálogo de Juicios:</strong> Los juicios hablan de lo que hace una persona y no de lo que es. Acción mata juicio.</li>
            <li><strong>El Mapa de la Inquietud:</strong> Herramientas para transformar la escucha reactiva en escucha generativa.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.download_button(
        label="Descargar Guía Rápida de Distinciones",
        data="Guía Rápida DIALECTA\n\n1. La Escucha valida el habla.\n2. Los Juicios pertenecen a quien los emite.\n3. Buscar la Inquietud del otro es el primer paso para coordinar acciones.",
        file_name="Distinciones_Dialecta.txt",
        mime="text/plain",
    )
