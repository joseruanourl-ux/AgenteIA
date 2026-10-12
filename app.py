import json
import random
import time
from datetime import datetime

import pandas as pd
import streamlit as st
from groq import Groq

from agent import process_response
from basic_memory import BasicMemory
from intermediate_tools import IntermediateTools

# ======================================================================
# CONFIGURACIÓN (cambia aquí el nombre y el emoji de la app)
# ======================================================================
APP_NAME = "R2-DATA"
APP_TAGLINE = "Droide de inteligencia financiera · Divisas · Cripto · Banco Mundial"
APP_ICON = "🤖"
MEMORY_MAX_MESSAGES = 10

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="centered")

# ======================================================================
# ESTILO STAR WARS
# ======================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600&display=swap');

.stApp {
    background-color: #02030a;
    background-image:
        radial-gradient(1px 1px at 20px 30px, #ffffff, transparent),
        radial-gradient(1px 1px at 90px 120px, #cfe3ff, transparent),
        radial-gradient(2px 2px at 160px 70px, #ffe81f, transparent),
        radial-gradient(1px 1px at 40px 160px, #ffffff, transparent),
        radial-gradient(1px 1px at 130px 20px, #ffffff, transparent),
        radial-gradient(1.5px 1.5px at 190px 150px, #9fd0ff, transparent);
    background-size: 220px 220px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.05rem;
}
[data-testid="stHeader"] { background: transparent; }

/* Encabezado */
.sw-header { display:flex; align-items:center; gap:18px; margin: 0 0 6px 0; }
.sw-droid { animation: flotar 3.5s ease-in-out infinite; filter: drop-shadow(0 0 10px rgba(58,160,255,.55)); }
.sw-eye { animation: pulso 1.8s ease-in-out infinite; }
@keyframes flotar { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
@keyframes pulso { 0%,100% { opacity: 1; } 50% { opacity: .35; } }
.sw-title {
    font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 2.6rem;
    letter-spacing: .18em; color: #FFE81F; line-height: 1.1;
    text-shadow: 0 0 8px rgba(255,232,31,.55), 0 0 24px rgba(255,232,31,.25);
}
.sw-sub { font-family: 'Rajdhani', sans-serif; font-weight: 500; color: #6cc4ff;
          letter-spacing: .12em; text-transform: uppercase; font-size: .9rem; }
.sw-line { height: 2px; margin: 10px 0 18px 0;
           background: linear-gradient(90deg, #FFE81F, rgba(255,232,31,0)); }

/* Mensajes del chat */
[data-testid="stChatMessage"] {
    background: rgba(10, 20, 45, .72);
    border: 1px solid rgba(255, 232, 31, .22);
    border-left: 3px solid #3aa0ff;
    border-radius: 12px;
    backdrop-filter: blur(3px);
}
[data-testid="stChatInput"] { border: 1px solid #FFE81F; border-radius: 12px; }

/* Barra lateral */
[data-testid="stSidebar"] { background: #05070f; border-right: 1px solid rgba(255,232,31,.25); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: 'Orbitron', sans-serif; color: #FFE81F; letter-spacing: .08em; font-size: 1rem;
}
[data-testid="stSidebar"] .stButton button, .stDownloadButton button {
    background: transparent; color: #FFE81F; border: 1px solid rgba(255,232,31,.55);
    border-radius: 8px; font-family: 'Rajdhani', sans-serif; font-weight: 600;
    text-align: left; transition: all .2s ease;
}
[data-testid="stSidebar"] .stButton button:hover, .stDownloadButton button:hover {
    background: rgba(255,232,31,.12); box-shadow: 0 0 12px rgba(255,232,31,.4); color: #fff;
}
[data-testid="stMetricValue"] { font-family: 'Orbitron', sans-serif; color: #FFE81F; font-size: 1.3rem; }
[data-testid="stMetricLabel"] { color: #6cc4ff; }

/* Crawl de apertura */
.crawl-wrap { height: 250px; overflow: hidden; position: relative; perspective: 260px;
              border: 1px solid rgba(255,232,31,.25); border-radius: 12px;
              background: rgba(0,0,0,.55); margin-bottom: 14px; }
.crawl-wrap:after { content:""; position:absolute; inset:0;
    background: linear-gradient(180deg, #02030a 0%, rgba(2,3,10,0) 35%); pointer-events:none; }
.crawl { position:absolute; width: 86%; left: 7%; bottom: -120%; text-align: justify;
         color: #FFE81F; font-family: 'Orbitron', sans-serif; font-weight: 700;
         font-size: .95rem; line-height: 1.5; transform-origin: 50% 100%;
         transform: rotateX(28deg); animation: crawl 38s linear infinite; }
.crawl h3 { text-align:center; margin: 0 0 .6em 0; font-size: 1.1rem; letter-spacing:.15em; }
@keyframes crawl { 0% { bottom: -120%; } 100% { bottom: 160%; } }
.hace-mucho { color: #6cc4ff; font-family: 'Rajdhani', sans-serif; font-size: 1.15rem;
              text-align:center; margin: 6px 0 12px 0; }
.sw-foot { text-align:center; color:#6b7a99; font-size:.8rem; margin-top: 28px; letter-spacing:.1em; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DROID_SVG = """
<svg class="sw-droid" width="74" height="74" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <rect x="13" y="36" width="7" height="22" rx="2" fill="#cfd8e3"/>
  <rect x="44" y="36" width="7" height="22" rx="2" fill="#cfd8e3"/>
  <rect x="10" y="56" width="13" height="4" rx="2" fill="#8794a8"/>
  <rect x="41" y="56" width="13" height="4" rx="2" fill="#8794a8"/>
  <rect x="18" y="26" width="28" height="30" rx="4" fill="#eef3f8" stroke="#9fb0c7"/>
  <path d="M18 26 A14 14 0 0 1 46 26 Z" fill="#eef3f8" stroke="#9fb0c7"/>
  <rect x="18" y="22" width="28" height="4" fill="#1e66d0"/>
  <circle class="sw-eye" cx="32" cy="17" r="4.2" fill="#0b1220" stroke="#3aa0ff" stroke-width="1.6"/>
  <circle cx="32" cy="17" r="1.6" fill="#ff4d4d"/>
  <rect x="22" y="33" width="8" height="6" rx="1" fill="#1e66d0"/>
  <rect x="34" y="33" width="8" height="11" rx="1" fill="#1e66d0"/>
  <rect x="22" y="43" width="8" height="8" rx="1" fill="#9fb0c7"/>
  <circle cx="38" cy="49" r="2" fill="#ff4d4d"/>
</svg>
"""

st.markdown(
    f"""
    <div class="sw-header">
        {DROID_SVG}
        <div>
            <div class="sw-title">{APP_NAME}</div>
            <div class="sw-sub">{APP_TAGLINE}</div>
        </div>
    </div>
    <div class="sw-line"></div>
    """,
    unsafe_allow_html=True,
)

# ======================================================================
# CLIENTE DE GROQ (la clave viene de los Secrets de Streamlit)
# ======================================================================
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Falta configurar GROQ_API_KEY en los Secrets de la app.")
    st.stop()


@st.cache_resource
def get_client(key: str) -> Groq:
    return Groq(api_key=key)


client = get_client(api_key)

# ======================================================================
# ESTADO DE LA SESIÓN
# ======================================================================
if "memory" not in st.session_state:
    st.session_state.memory = BasicMemory(max_messages=MEMORY_MAX_MESSAGES)
if "chat" not in st.session_state:
    st.session_state.chat = []

AVATARES = {"user": "🧑‍🚀", "assistant": APP_ICON}

FRASES_CARGA = [
    "Consultando los archivos Jedi...",
    "Calculando la ruta de hiperespacio...",
    "Interrogando al droide astromecánico...",
    "Descifrando transmisiones rebeldes...",
    "Sincronizando con la Holo-Red...",
    "Que la Fuerza te acompañe...",
]

MISIONES = {
    "💱 Divisas": [
        "¿Cuánto son 100 USD en quetzales?",
        "¿Cuál es el tipo de cambio del euro en quetzales?",
        "Tipo de cambio de EUR a USD el 2024-01-15",
    ],
    "🪙 Cripto": [
        "¿Cuál es el precio de bitcoin?",
        "Dame el top 5 de criptomonedas",
    ],
    "🌎 Economía": [
        "¿Cuál es la inflación en Guatemala?",
        "Compara el desempleo de GT, MX y US",
        "Dame información básica de Guatemala",
    ],
}

PRUEBAS = [
    ("consultar_tipo_cambio_api", "open.er-api", lambda t: t.consultar_tipo_cambio_api("USD", "GTQ")),
    ("consultar_precio_cripto_api", "CoinGecko", lambda t: t.consultar_precio_cripto_api("bitcoin", "usd")),
    ("consultar_indicador_banco_mundial_api", "Banco Mundial", lambda t: t.consultar_indicador_banco_mundial_api("GT", "SP.POP.TOTL")),
    ("consultar_indicador_macro_api", "Banco Mundial", lambda t: t.consultar_indicador_macro_api("inflacion", "GT")),
    ("consultar_tasa_cambio_frankfurter_api", "Frankfurter", lambda t: t.consultar_tasa_cambio_frankfurter_api("EUR", "USD")),
    ("consultar_top_criptos_api", "CoinGecko", lambda t: t.consultar_top_criptos_api(3, "usd")),
    ("consultar_historial_tasa_cambio_api", "Frankfurter", lambda t: t.consultar_historial_tasa_cambio_api("2024-01-15", "EUR", "USD")),
    ("consultar_conversion_moneda_api", "open.er-api", lambda t: t.consultar_conversion_moneda_api(100, "USD", "GTQ")),
    ("consultar_comparativo_indicador_banco_mundial_api", "Banco Mundial", lambda t: t.consultar_comparativo_indicador_banco_mundial_api("GT,MX,US", "desempleo")),
    ("consultar_info_pais_banco_mundial_api", "Banco Mundial", lambda t: t.consultar_info_pais_banco_mundial_api("GT")),
]


# ======================================================================
# FUNCIONES AUXILIARES
# ======================================================================
@st.cache_data(ttl=300, show_spinner=False)
def cargar_metricas():
    # Datos en vivo para el panel lateral (se refrescan cada 5 minutos).
    t = IntermediateTools()
    out = {"usd": None, "eur": None, "btc": None}
    r = t.consultar_tipo_cambio_api("USD", "GTQ")
    if isinstance(r, dict):
        out["usd"] = r.get("tasa")
    r = t.consultar_tipo_cambio_api("EUR", "GTQ")
    if isinstance(r, dict):
        out["eur"] = r.get("tasa")
    r = t.consultar_precio_cripto_api("bitcoin", "usd")
    if isinstance(r, dict):
        out["btc"] = (r.get("bitcoin") or {}).get("usd")
    if all(v is None for v in out.values()):
        raise RuntimeError("Sin datos")  # así no se guarda en caché un fallo
    return out


def ejecutar_diagnostico():
    t = IntermediateTools()
    filas = []
    for i, (nombre, api, prueba) in enumerate(PRUEBAS):
        try:
            r = prueba(t)
            ok = not (isinstance(r, str) and r.strip().lower().startswith("error"))
            detalle = r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)
        except Exception as e:
            ok, detalle = False, f"{type(e).__name__}: {e}"
        filas.append({
            "Estado": "✅" if ok else "❌",
            "Herramienta": nombre,
            "API": api,
            "Detalle": detalle[:110],
        })
        if api == "CoinGecko" and i < len(PRUEBAS) - 1:
            time.sleep(1.2)  # evita el límite de peticiones de CoinGecko
    return filas


def exportar_conversacion() -> str:
    lineas = [f"Conversación con {APP_NAME} · {datetime.now():%Y-%m-%d %H:%M}", ""]
    for m in st.session_state.chat:
        quien = "Tú" if m["role"] == "user" else APP_NAME
        lineas.append(f"{quien}: {m['content']}")
        lineas.append("")
    return "\n".join(lineas)


def mostrar_trace(trace):
    # Muestra qué herramientas usó el agente, con qué argumentos y qué devolvieron.
    if not trace or not st.session_state.get("modo_ingeniero", True):
        return
    with st.expander(f"🔧 Herramientas usadas ({len(trace)})"):
        for t in trace:
            st.markdown(f"**{t['herramienta']}**")
            st.code(json.dumps(t["argumentos"], ensure_ascii=False), language="json")
            res = t["resultado"]
            if isinstance(res, str):
                st.code(res, language=None)
            else:
                st.code(json.dumps(res, ensure_ascii=False, indent=2), language="json")


# ======================================================================
# BARRA LATERAL
# ======================================================================
with st.sidebar:
    st.header("📡 TRANSMISIONES EN VIVO")
    try:
        met = cargar_metricas()
        c1, c2 = st.columns(2)
        c1.metric("USD → GTQ", f"Q {met['usd']:.2f}" if met["usd"] else "—")
        c2.metric("EUR → GTQ", f"Q {met['eur']:.2f}" if met["eur"] else "—")
        st.metric("Bitcoin", f"$ {met['btc']:,.0f}" if met["btc"] else "—")
    except Exception:
        st.caption("Sin señal de la Holo-Red por ahora.")

    st.header("🎯 MISIONES RÁPIDAS")
    for categoria, preguntas in MISIONES.items():
        with st.expander(categoria):
            for i, p in enumerate(preguntas):
                if st.button(p, key=f"m_{categoria}_{i}", use_container_width=True):
                    st.session_state.pending = p

    st.header("⚙️ CONTROLES")
    st.toggle("Modo ingeniero (ver herramientas)", value=True, key="modo_ingeniero")
    if st.button("🧪 Diagnosticar sistemas", use_container_width=True):
        st.session_state.run_diag = True
    if st.session_state.chat:
        st.download_button(
            "💾 Descargar conversación",
            data=exportar_conversacion(),
            file_name="conversacion.txt",
            mime="text/plain",
            use_container_width=True,
        )
    if st.button("🗑️ Borrar conversación", use_container_width=True):
        st.session_state.memory = BasicMemory(max_messages=MEMORY_MAX_MESSAGES)
        st.session_state.chat = []
        st.session_state.pop("diag", None)
        st.rerun()

    st.header("📊 ESTADÍSTICAS")
    n_user = sum(1 for m in st.session_state.chat if m["role"] == "user")
    n_tools = sum(len(m.get("trace") or []) for m in st.session_state.chat)
    s1, s2 = st.columns(2)
    s1.metric("Consultas", n_user)
    s2.metric("Herramientas", n_tools)
    st.caption(f"Memoria: últimos {MEMORY_MAX_MESSAGES} mensajes · 10 herramientas · 4 APIs")

# ======================================================================
# DIAGNÓSTICO (si se pidió)
# ======================================================================
if st.session_state.pop("run_diag", False):
    with st.status("Revisando los sistemas del droide...", expanded=True) as estado:
        st.session_state.diag = ejecutar_diagnostico()
        fallas = sum(1 for f in st.session_state.diag if f["Estado"] == "❌")
        if fallas:
            estado.update(label=f"Diagnóstico terminado: {fallas} sistema(s) con fallas", state="error")
        else:
            estado.update(label="Diagnóstico terminado: todos los sistemas operativos", state="complete")

if st.session_state.get("diag"):
    with st.expander("🧪 Resultado del diagnóstico", expanded=True):
        st.dataframe(pd.DataFrame(st.session_state.diag), hide_index=True)

# ======================================================================
# PANTALLA DE BIENVENIDA (solo si el chat está vacío)
# ======================================================================
if not st.session_state.chat:
    st.markdown(
        """
        <div class="hace-mucho">Hace mucho tiempo, en una galaxia muy, muy lejana...</div>
        <div class="crawl-wrap"><div class="crawl">
            <h3>EPISODIO I<br>EL DROIDE DE LOS DATOS</h3>
            Las divisas fluctúan, las criptomonedas se disparan y la economía
            galáctica vive tiempos de incertidumbre. Un pequeño droide
            astromecánico, armado con diez herramientas y conexión a cuatro
            redes de datos, ha despertado para ayudarte.<br><br>
            Pregúntale por el tipo de cambio, el precio de las criptomonedas
            o los indicadores del Banco Mundial. Su memoria guarda tus últimas
            consultas, y sus respuestas se basan en datos reales.<br><br>
            Elige una misión en el panel lateral o escribe tu primera
            transmisión abajo...
        </div></div>
        """,
        unsafe_allow_html=True,
    )

# ======================================================================
# HISTORIAL
# ======================================================================
for m in st.session_state.chat:
    with st.chat_message(m["role"], avatar=AVATARES[m["role"]]):
        st.markdown(m["content"])
        mostrar_trace(m.get("trace"))

# ======================================================================
# ENTRADA (chat o botón de misión rápida)
# ======================================================================
pendiente = st.session_state.pop("pending", None)
escrito = st.chat_input("Transmite tu mensaje a la galaxia...")
user_text = (pendiente or escrito or "").strip()

if user_text:
    st.session_state.chat.append({"role": "user", "content": user_text})
    with st.chat_message("user", avatar=AVATARES["user"]):
        st.markdown(user_text)

    trace = []
    with st.chat_message("assistant", avatar=AVATARES["assistant"]):
        with st.spinner(random.choice(FRASES_CARGA)):
            try:
                assistant_text = process_response(
                    client, st.session_state.memory.messages(), user_text, trace
                )
            except Exception as e:
                assistant_text = f"Ocurrió un error al contactar al modelo: {e}"
        st.markdown(assistant_text)
        mostrar_trace(trace)

    st.session_state.chat.append(
        {"role": "assistant", "content": assistant_text, "trace": trace}
    )
    st.session_state.memory.add("user", user_text)
    st.session_state.memory.add("assistant", assistant_text)
    st.rerun()  # refresca el panel de estadísticas

st.markdown(
    '<div class="sw-foot">QUE LA FUERZA DE LOS DATOS TE ACOMPAÑE</div>',
    unsafe_allow_html=True,
)
