import json
import random
import time
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st
from groq import Groq

from agent import process_response
from basic_memory import BasicMemory
from intermediate_tools import IntermediateTools
import storage

# ======================================================================
# CONFIGURACIÓN (cambia aquí el nombre y el emoji de la app)
# ======================================================================
APP_NAME = "AURUM"
APP_TAGLINE = "Capital Intelligence · Divisas · Criptoactivos · Macroeconomía"
APP_ICON = "💠"
MEMORY_MAX_MESSAGES = 10

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="centered")


def html(s: str) -> str:
    # Markdown trata las líneas con 4+ espacios de sangría, o con líneas en blanco,
    # como bloque de código. Aplanamos el HTML en una sola línea para evitarlo.
    return " ".join(l.strip() for l in s.splitlines() if l.strip())


# ======================================================================
# ESTILO VISUAL (HUD financiero)
# ======================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;500;600&family=Cormorant+Garamond:wght@600;700&family=Share+Tech+Mono&display=swap');

:root { --cyan:#00d4ff; --gold:#d4af37; --navy:#050b14; --line:rgba(0,212,255,.28);
        --txt:#dce9f5; --mute:#7f96b2; --up:#4ade80; }

.stApp {
    background-color: var(--navy);
    background-image:
        radial-gradient(ellipse at 50% -10%, rgba(0,212,255,.15), transparent 55%),
        radial-gradient(ellipse at 95% 100%, rgba(212,175,55,.08), transparent 50%),
        linear-gradient(rgba(0,212,255,.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,.045) 1px, transparent 1px);
    background-size: auto, auto, 44px 44px, 44px 44px;
    font-family: 'Exo 2', sans-serif; font-size: 1rem; color: var(--txt);
}
[data-testid="stHeader"] { background: transparent; }

/* Encabezado */
.hud-header { display:flex; align-items:center; gap:18px; margin: 0 0 4px 0; }
.hud-logo { filter: drop-shadow(0 0 8px rgba(0,212,255,.55)); flex-shrink:0; }
.ring-a { animation: giro 16s linear infinite; transform-box: fill-box; transform-origin: center; }
.ring-b { animation: giro 10s linear infinite reverse; transform-box: fill-box; transform-origin: center; }
.core { animation: latido 2.6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes giro { to { transform: rotate(360deg); } }
@keyframes latido { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: .55; transform: scale(.82); } }
.hud-brand { font-family:'Cormorant Garamond', serif; font-weight:700; font-size:2.7rem; line-height:1;
             letter-spacing:.34em; color: var(--gold); text-shadow: 0 0 18px rgba(212,175,55,.35); }
.hud-sub { font-weight:400; color: var(--cyan); letter-spacing:.2em; text-transform:uppercase;
           font-size:.72rem; margin-top:6px; }
.hud-status { margin-left:auto; font-family:'Share Tech Mono', monospace; font-size:.72rem; color: var(--up);
              border:1px solid rgba(74,222,128,.4); border-radius:20px; padding:4px 12px; white-space:nowrap; }
.hud-status:before { content:"●"; margin-right:6px; animation: latido 1.8s ease-in-out infinite; display:inline-block; }
.hud-line { height:1px; margin:12px 0 10px 0;
            background: linear-gradient(90deg, var(--cyan), var(--gold) 55%, rgba(212,175,55,0)); }
@media (max-width: 640px) { .hud-status { display:none; } .hud-brand { font-size:2rem; } }

/* Cinta de cotizaciones */
.ticker { overflow:hidden; white-space:nowrap; border-top:1px solid var(--line); border-bottom:1px solid var(--line);
          background: rgba(0,212,255,.04); padding:7px 0; margin:0 0 18px 0;
          font-family:'Share Tech Mono', monospace; font-size:.84rem; }
.ticker-track { display:inline-block; animation: cinta 50s linear infinite; }
.ticker:hover .ticker-track { animation-play-state: paused; }
@keyframes cinta { from { transform: translateX(0); } to { transform: translateX(-25%); } }
.tk b { color: var(--gold); font-weight:400; letter-spacing:.14em; margin-right:6px; }
.tk i { color: var(--up); font-style:normal; }
.tk em { color: var(--mute); font-style:normal; }
.sep { color: var(--cyan); margin: 0 26px; opacity:.7; }

/* Mensajes del chat (paneles HUD con esquinas) */
[data-testid="stChatMessage"] {
    position: relative; background: rgba(8,20,38,.78); border: 1px solid var(--line);
    border-left: 3px solid var(--cyan); border-radius: 4px; backdrop-filter: blur(4px);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { border-left-color: var(--gold); }
[data-testid="stChatMessage"]:before, [data-testid="stChatMessage"]:after {
    content:""; position:absolute; width:10px; height:10px; pointer-events:none; }
[data-testid="stChatMessage"]:before { top:-1px; right:-1px; border-top:2px solid var(--cyan); border-right:2px solid var(--cyan); }
[data-testid="stChatMessage"]:after { bottom:-1px; right:-1px; border-bottom:2px solid var(--cyan); border-right:2px solid var(--cyan); }

/* Barra lateral */
[data-testid="stSidebar"] { background:#040912; border-right:1px solid var(--line); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family:'Exo 2', sans-serif; font-weight:600; color: var(--cyan); letter-spacing:.24em;
    font-size:.74rem; text-transform:uppercase; border-bottom:1px solid var(--line); padding-bottom:6px;
}
[data-testid="stSidebar"] .stButton button, .stDownloadButton button {
    background: transparent; color: var(--txt); border:1px solid var(--line); border-radius:3px;
    font-family:'Exo 2', sans-serif; font-weight:500; text-align:left; transition: all .2s ease;
}
[data-testid="stSidebar"] .stButton button:hover, .stDownloadButton button:hover {
    background: rgba(0,212,255,.1); border-color: var(--cyan); box-shadow: 0 0 12px rgba(0,212,255,.3); color:#fff;
}
[data-testid="stMetricValue"] { font-family:'Share Tech Mono', monospace; color: var(--gold); font-size:1.3rem; }
[data-testid="stMetricLabel"] { color: var(--mute); }

/* Panel de bienvenida */
.brief { position:relative; border:1px solid var(--line); background: rgba(8,20,38,.72);
         padding:22px 24px; margin-bottom:16px; border-radius:4px; }
.brief:before { content:""; position:absolute; top:-1px; left:-1px; width:14px; height:14px;
                border-top:2px solid var(--gold); border-left:2px solid var(--gold); }
.brief:after { content:""; position:absolute; bottom:-1px; right:-1px; width:14px; height:14px;
               border-bottom:2px solid var(--gold); border-right:2px solid var(--gold); }
.brief-tag { font-family:'Share Tech Mono', monospace; font-size:.72rem; color: var(--up); letter-spacing:.16em; }
.brief-title { font-family:'Cormorant Garamond', serif; font-size:1.7rem; font-weight:700; color:#fff; margin:6px 0 8px 0; }
.brief p { color: var(--txt); opacity:.88; margin:0 0 14px 0; }
.cards { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; margin-bottom:14px; }
@media (max-width: 640px) { .cards { grid-template-columns: 1fr; } }
.card { border:1px solid var(--line); border-top:2px solid var(--gold); padding:12px 14px; background: rgba(0,212,255,.04); }
.ci { color: var(--cyan); font-size:1.1rem; }
.ct { color: var(--gold); letter-spacing:.14em; text-transform:uppercase; font-size:.78rem; font-weight:600; margin:2px 0 4px 0; }
.cd { color: var(--mute); font-size:.88rem; line-height:1.35; }
.brief-hint { color: var(--cyan) !important; font-size:.85rem; letter-spacing:.06em; margin:0 !important; }
.hud-foot { text-align:center; color:#5d7391; font-size:.7rem; margin-top:30px; letter-spacing:.14em; }

/* Respaldo del tema oscuro (por si no se carga .streamlit/config.toml) */
.stApp { color: var(--txt); }
[data-testid="stBottom"], [data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"] { background: #050b14 !important; }
[data-testid="stChatInput"], [data-testid="stChatInput"] > div,
[data-testid="stChatInput"] textarea { background: #0b1626 !important; color: var(--txt) !important; }
[data-testid="stChatInput"] { border: 1px solid var(--cyan); border-radius: 4px; }
[data-testid="stChatInput"] textarea::placeholder { color: #7f96b2 !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary *,
[data-testid="stStatus"] summary, [data-testid="stStatus"] summary *,
[data-testid="stCheckbox"] label *, [data-testid="stToggle"] label *,
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: var(--txt) !important; }
[data-testid="stExpander"] { border-color: var(--line) !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

LOGO_SVG = """
<svg class="hud-logo" width="74" height="74" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
  <circle cx="40" cy="40" r="37" fill="none" stroke="#00d4ff" stroke-opacity=".25" stroke-width="1"/>
  <circle class="ring-a" cx="40" cy="40" r="32" fill="none" stroke="#00d4ff" stroke-width="2" stroke-dasharray="6 5 28 5"/>
  <circle class="ring-b" cx="40" cy="40" r="25" fill="none" stroke="#d4af37" stroke-width="1.5" stroke-dasharray="3 6"/>
  <polygon points="40,23 54.7,31.5 54.7,48.5 40,57 25.3,48.5 25.3,31.5" fill="none" stroke="#00d4ff" stroke-width="1.2" stroke-opacity=".85"/>
  <circle cx="40" cy="40" r="11" fill="none" stroke="#ffffff" stroke-opacity=".45" stroke-width=".8"/>
  <circle class="core" cx="40" cy="40" r="6.5" fill="#d4af37"/>
</svg>
"""

st.markdown(
    html(f"""
    <div class="hud-header">
        {LOGO_SVG}
        <div>
            <div class="hud-brand">{APP_NAME}</div>
            <div class="hud-sub">{APP_TAGLINE}</div>
        </div>
        <div class="hud-status">SISTEMAS EN LÍNEA</div>
    </div>
    <div class="hud-line"></div>
    """),
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
TITULO_NUEVA = "Nueva conversación"


def _ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def reconstruir_memoria(chat, n):
    # La memoria del agente son los últimos n mensajes de la conversación activa.
    mem = BasicMemory(max_messages=n)
    for m in chat:
        mem.add(m["role"], m["content"])
    return mem


def nueva_conv():
    cid = uuid.uuid4().hex[:8]
    st.session_state.convs[cid] = {
        "id": cid, "title": TITULO_NUEVA, "created": _ahora(), "updated": _ahora(), "chat": [],
    }
    return cid


def activar(cid):
    # Cambia a otra conversación: restaura su historial y la memoria del agente.
    st.session_state.current = cid
    st.session_state.chat = st.session_state.convs[cid]["chat"]
    st.session_state.memory = reconstruir_memoria(
        st.session_state.chat, st.session_state.get("mem_n", MEMORY_MAX_MESSAGES)
    )


def eliminar_conv(cid):
    st.session_state.convs.pop(cid, None)
    if st.session_state.get("owner"):
        try:
            storage.eliminar(st.session_state.owner, cid)
        except Exception as e:
            st.session_state.sync_error = str(e)
    restantes = [c for c in st.session_state.convs.values() if c["chat"]]
    if st.session_state.current == cid or st.session_state.current not in st.session_state.convs:
        if restantes:
            activar(max(restantes, key=lambda c: c["updated"])["id"])
        else:
            activar(nueva_conv())


def sincronizar(conv):
    # Guarda una conversación en Supabase (si hay sesión). Un fallo nunca rompe la app.
    if not st.session_state.get("owner") or not conv.get("chat"):
        return
    try:
        storage.guardar(st.session_state.owner, conv)
        st.session_state.pop("sync_error", None)
    except Exception as e:
        st.session_state.sync_error = str(e)


def sincronizar_todas(excepto=()):
    for c in list(st.session_state.convs.values()):
        if c["id"] not in excepto:
            sincronizar(c)


def conectar(nombre: str, pin: str):
    # Devuelve None si todo salió bien, o un texto con el problema.
    if len(nombre.strip()) < 3 or len(pin) < 4:
        return "El usuario necesita al menos 3 caracteres y el PIN al menos 4."
    owner = storage.calcular_owner(nombre, pin)
    try:
        filas = storage.listar(owner)
    except Exception as e:
        return f"No se pudo conectar: {e}"
    ids_nube = set()
    for f in filas:
        cid = str(f.get("id"))
        ids_nube.add(cid)
        if cid not in st.session_state.convs and f.get("chat"):
            st.session_state.convs[cid] = {
                "id": cid, "title": f.get("title") or TITULO_NUEVA,
                "created": f.get("created") or _ahora(), "updated": f.get("updated") or _ahora(),
                "chat": f["chat"],
            }
    st.session_state.owner = owner
    st.session_state.owner_nombre = nombre.strip()
    sincronizar_todas(excepto=ids_nube)  # sube lo que ya hubieras escrito antes de conectar
    if not st.session_state.chat:
        con_datos = [c for c in st.session_state.convs.values() if c["chat"]]
        if con_datos:
            activar(max(con_datos, key=lambda c: c["updated"])["id"])
    return None


def desconectar():
    # Cierra la sesión y limpia lo que había en pantalla (útil en equipos compartidos).
    for k in ("owner", "owner_nombre", "sync_error", "login_msg"):
        st.session_state.pop(k, None)
    st.session_state.convs = {}
    activar(nueva_conv())


def exportar_json() -> str:
    data = {
        "version": 1,
        "exportado": _ahora(),
        "conversations": [c for c in st.session_state.convs.values() if c["chat"]],
    }
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def importar_json(raw: bytes):
    # Devuelve (importadas, omitidas, error). Valida el formato antes de aceptar nada.
    try:
        items = json.loads(raw.decode("utf-8"))["conversations"]
        if not isinstance(items, list):
            raise ValueError
    except Exception:
        return 0, 0, "El archivo no parece un respaldo válido."
    nuevas = omitidas = 0
    for c in items:
        try:
            cid = str(c["id"])
            chat = []
            for m in c["chat"]:
                if m["role"] not in ("user", "assistant"):
                    continue
                msg = {"role": m["role"], "content": str(m["content"])}
                if m.get("trace"):
                    msg["trace"] = m["trace"]
                chat.append(msg)
        except Exception:
            continue
        if not chat or cid in st.session_state.convs:
            omitidas += 1
            continue
        st.session_state.convs[cid] = {
            "id": cid,
            "title": str(c.get("title") or TITULO_NUEVA)[:80],
            "created": str(c.get("created") or _ahora()),
            "updated": str(c.get("updated") or _ahora()),
            "chat": chat,
        }
        nuevas += 1
    return nuevas, omitidas, None


if "convs" not in st.session_state:
    st.session_state.convs = {}
    activar(nueva_conv())

AVATARES = {"user": "💼", "assistant": APP_ICON}

FRASES_CARGA = [
    "Consultando mercados globales...",
    "Procesando cotizaciones en tiempo real...",
    "Analizando indicadores macroeconómicos...",
    "Verificando fuentes de datos...",
    "Calculando posiciones...",
]

MISIONES = {
    "Divisas": [
        "¿Cuánto son 100 USD en quetzales?",
        "¿Cuál es el tipo de cambio del euro en quetzales?",
        "Tipo de cambio de EUR a USD el 2024-01-15",
        "¿Cuál es el tipo de cambio oficial del Banguat hoy?",
    ],
    "Criptoactivos": [
        "¿Cuál es el precio de bitcoin?",
        "Dame el top 5 de criptomonedas",
        "¿Cómo está el índice de miedo y codicia del mercado cripto?",
    ],
    "Referencia": [
        "¿Qué es la inflación?",
        "Dame datos de Costa Rica: población, capital y moneda",
    ],
    "Macroeconomía": [
        "¿Cuál es la inflación en Guatemala?",
        "Compara el desempleo de GT, MX y US",
        "Muéstrame una gráfica de la inflación de Guatemala de los últimos 10 años",
        "Compara en una gráfica el desempleo de GT, MX y CR",
        "Analiza el crecimiento del PIB de Guatemala y proyecta 3 años",
        "¿Qué proyecta el FMI para el crecimiento de Guatemala?",
        "¿Cuál es la deuda pública de Estados Unidos?",
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
    ("consultar_serie_historica_banco_mundial_api", "Banco Mundial", lambda t: t.consultar_serie_historica_banco_mundial_api("GT", "inflacion")),
    ("consultar_proyecciones_fmi_api", "FMI", lambda t: t.consultar_proyecciones_fmi_api("GT", "crecimiento_pib")),
    ("consultar_datos_pais_api", "REST Countries", lambda t: t.consultar_datos_pais_api("GT")),
    ("consultar_deuda_publica_eeuu_api", "Tesoro de EE. UU.", lambda t: t.consultar_deuda_publica_eeuu_api("deuda")),
    ("consultar_indice_miedo_codicia_api", "Alternative.me", lambda t: t.consultar_indice_miedo_codicia_api(1)),
    ("consultar_concepto_wikipedia_api", "Wikipedia", lambda t: t.consultar_concepto_wikipedia_api("inflación")),
    ("consultar_tipo_cambio_banguat_api", "Banguat", lambda t: t.consultar_tipo_cambio_banguat_api()),
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
    if storage.disponible():
        motivo = storage.probar()
        filas.append({
            "Estado": "✅" if motivo is None else "❌",
            "Herramienta": "guardado de conversaciones",
            "API": "Supabase",
            "Detalle": "Conexión y tabla correctas" if motivo is None else motivo[:110],
        })
    return filas


def exportar_conversacion() -> str:
    lineas = [f"Conversación con {APP_NAME} · {datetime.now():%Y-%m-%d %H:%M}", ""]
    for m in st.session_state.chat:
        quien = "Tú" if m["role"] == "user" else APP_NAME
        lineas.append(f"{quien}: {m['content']}")
        lineas.append("")
    return "\n".join(lineas)


PALETA = ["#00d4ff", "#d4af37", "#4ade80", "#f472b6", "#a78bfa", "#fb923c"]


SERIES_TOOLS = {"consultar_serie_historica_banco_mundial_api", "consultar_proyecciones_fmi_api"}


def mostrar_graficos(trace):
    # Dibuja una gráfica por cada serie histórica consultada (datos reales del Banco Mundial).
    for t in trace or []:
        if t.get("herramienta") not in SERIES_TOOLS:
            continue
        r = t.get("resultado")
        if not isinstance(r, dict) or not r.get("series"):
            continue
        cols = {pais: {int(a): v for a, v in s["datos"].items()} for pais, s in r["series"].items()}
        proy = r.get("proyeccion")
        if proy and proy.get("pais") in cols:
            base = cols[proy["pais"]]
            ultimo = max(base)
            etiqueta = "Proyección FMI" if "FMI" in proy.get("metodo", "") else "Proyección (tendencia)"
            cols[etiqueta] = {ultimo: base[ultimo], **{int(a): v for a, v in proy["datos"].items()}}
        df = pd.DataFrame(cols).sort_index()
        df.index = df.index.astype(str)
        df.index.name = "Año"
        st.markdown(f"**{r.get('indicador', 'Indicador')}** · {r.get('periodo_solicitado', '')}")
        try:
            st.line_chart(df, height=300, color=PALETA[: len(df.columns)])
        except Exception:
            st.line_chart(df, height=300)
        if len(r["series"]) == 1:
            res = next(iter(r["series"].values())).get("resumen", {})
            if res:
                st.caption(
                    f"Último: {res['ultimo_dato']['valor']} ({res['ultimo_dato']['anio']}) · "
                    f"Mín: {res['minimo']['valor']} ({res['minimo']['anio']}) · "
                    f"Máx: {res['maximo']['valor']} ({res['maximo']['anio']}) · "
                    f"Promedio: {res['promedio']} · Tendencia: {res.get('tendencia', 'n/d')}"
                )
        nota = f"Fuente: {r.get('fuente', 'Banco Mundial (datos anuales)')}."
        if proy and "FMI" in proy.get("metodo", ""):
            nota += " La línea de proyección corresponde a las estimaciones oficiales del FMI."
        elif proy:
            nota += " La línea de proyección es una extrapolación lineal simple, no un pronóstico oficial."
        st.caption(nota)


def mostrar_trace(trace):
    # Muestra qué herramientas usó el agente, con qué argumentos y qué devolvieron.
    if not trace or not st.session_state.get("modo_ingeniero", True):
        return
    with st.expander(f"Fuentes y herramientas consultadas ({len(trace)})"):
        for t in trace:
            st.markdown(f"**{t['herramienta']}**")
            st.code(json.dumps(t["argumentos"], ensure_ascii=False), language="json")
            res = t["resultado"]
            if isinstance(res, str):
                st.code(res, language=None)
            else:
                st.code(json.dumps(res, ensure_ascii=False, indent=2), language="json")


def render_ticker():
    # Cinta de cotizaciones tipo bolsa, con los datos en vivo (se refrescan cada 5 min).
    try:
        met = cargar_metricas()
    except Exception:
        met = {}
    elementos = []
    if met.get("usd"):
        elementos.append(f'<span class="tk"><b>USD/GTQ</b><i>{met["usd"]:.2f}</i></span>')
    if met.get("eur"):
        elementos.append(f'<span class="tk"><b>EUR/GTQ</b><i>{met["eur"]:.2f}</i></span>')
    if met.get("btc"):
        elementos.append(f'<span class="tk"><b>BTC/USD</b><i>{met["btc"]:,.0f}</i></span>')
    elementos += [
        '<span class="tk"><b>DIVISAS</b><em>open.er-api · Frankfurter · Banguat</em></span>',
        '<span class="tk"><b>CRIPTO</b><em>CoinGecko · Alternative.me</em></span>',
        '<span class="tk"><b>MACRO</b><em>Banco Mundial · FMI · Tesoro EE. UU.</em></span>',
        '<span class="tk"><b>REFERENCIA</b><em>REST Countries · Wikipedia</em></span>',
    ]
    grupo = '<span class="sep">◆</span>'.join(elementos) + '<span class="sep">◆</span>'
    st.markdown(
        html(f'<div class="ticker"><div class="ticker-track">{grupo * 4}</div></div>'),
        unsafe_allow_html=True,
    )


render_ticker()

# ======================================================================
# BARRA LATERAL
# ======================================================================
with st.sidebar:
    st.header("MERCADOS EN VIVO")
    try:
        met = cargar_metricas()
        c1, c2 = st.columns(2)
        c1.metric("USD → GTQ", f"Q {met['usd']:.2f}" if met["usd"] else "—")
        c2.metric("EUR → GTQ", f"Q {met['eur']:.2f}" if met["eur"] else "—")
        st.metric("Bitcoin", f"$ {met['btc']:,.0f}" if met["btc"] else "—")
    except Exception:
        st.caption("Sin conexión con las fuentes de mercado por ahora.")

    st.header("CUENTA EN LA NUBE")
    if not storage.disponible():
        st.caption("Guardado en la nube sin configurar: faltan SUPABASE_URL y SUPABASE_KEY en Secrets.")
    elif st.session_state.get("owner"):
        st.caption(f"Sincronizado como **{st.session_state.owner_nombre}**. Cada respuesta se guarda automáticamente.")
        if st.button("Cerrar sesión", key="logout", use_container_width=True):
            desconectar()
            st.rerun()
    else:
        st.text_input("Usuario", key="login_user")
        st.text_input("PIN", type="password", key="login_pin")
        if st.button("Conectar", key="login_btn", use_container_width=True):
            error = conectar(st.session_state.login_user, st.session_state.login_pin)
            if error:
                st.session_state.login_msg = error
            else:
                st.session_state.pop("login_msg", None)
            st.rerun()
        if st.session_state.get("login_msg"):
            st.caption("⚠️ " + st.session_state.login_msg)
        st.caption("Sin usuario y PIN, tus conversaciones solo viven en esta sesión.")
    if st.session_state.get("sync_error"):
        st.caption("⚠️ No se pudo guardar en la nube: " + st.session_state.sync_error)

    st.header("HISTORIAL")
    if st.button("+ Nueva conversación", use_container_width=True):
        if st.session_state.chat:  # si la actual está vacía no crea otra
            activar(nueva_conv())
        st.rerun()
    guardadas = sorted(
        (c for c in st.session_state.convs.values() if c["chat"]),
        key=lambda c: c["updated"], reverse=True,
    )
    if not guardadas:
        st.caption("Aún no hay conversaciones guardadas.")
    for c in guardadas[:12]:
        activa = c["id"] == st.session_state.current
        titulo = c["title"] if len(c["title"]) <= 26 else c["title"][:25] + "…"
        col_a, col_b = st.columns([5, 1])
        if col_a.button(("▶ " if activa else "") + titulo, key=f"conv_{c['id']}", use_container_width=True):
            activar(c["id"])
            st.rerun()
        if col_b.button("✕", key=f"del_{c['id']}", help="Eliminar esta conversación"):
            eliminar_conv(c["id"])
            st.rerun()
    if len(guardadas) > 12:
        st.caption(f"+{len(guardadas) - 12} más (están incluidas en el respaldo)")

    st.header("CONSULTAS RÁPIDAS")
    for categoria, preguntas in MISIONES.items():
        with st.expander(categoria):
            for i, p in enumerate(preguntas):
                if st.button(p, key=f"m_{categoria}_{i}", use_container_width=True):
                    st.session_state.pending = p

    st.header("CONTROLES")
    st.toggle("Modo analista (ver fuentes)", value=True, key="modo_ingeniero")
    st.slider(
        "Memoria del asistente (mensajes)", 4, 40, MEMORY_MAX_MESSAGES, key="mem_n",
        help="Cuántos mensajes recientes recuerda el agente. Más memoria = más tokens por consulta.",
    )
    if st.session_state.memory.history.maxlen != st.session_state.mem_n:
        st.session_state.memory = reconstruir_memoria(st.session_state.chat, st.session_state.mem_n)
    if st.button("Diagnóstico de sistemas", use_container_width=True):
        st.session_state.run_diag = True
    if st.session_state.chat:
        st.download_button(
            "Exportar conversación (.txt)",
            data=exportar_conversacion(),
            file_name="conversacion.txt",
            mime="text/plain",
            use_container_width=True,
        )
    if st.button("Borrar esta conversación", use_container_width=True):
        eliminar_conv(st.session_state.current)
        st.session_state.pop("diag", None)
        st.rerun()

    st.header("RESPALDO")
    st.download_button(
        "Descargar respaldo (JSON)",
        data=exportar_json(),
        file_name="aurum_conversaciones.json",
        mime="application/json",
        disabled=not guardadas,
        use_container_width=True,
    )
    subido = st.file_uploader("Cargar respaldo", type="json", key="uploader")
    if subido is not None and st.session_state.get("ultimo_import") != (subido.name, subido.size):
        st.session_state.ultimo_import = (subido.name, subido.size)
        nuevas, omitidas, error = importar_json(subido.getvalue())
        if error:
            st.session_state.import_msg = f"⚠️ {error}"
        else:
            st.session_state.import_msg = f"✅ {nuevas} conversación(es) cargada(s)" + (
                f", {omitidas} ya existían u omitidas." if omitidas else "."
            )
            sincronizar_todas()
        st.rerun()
    if st.session_state.get("import_msg"):
        st.caption(st.session_state.import_msg)
    if st.session_state.get("owner"):
        st.caption("Tus conversaciones se guardan en la nube. El respaldo JSON es opcional.")
    else:
        st.caption("Las conversaciones viven en esta sesión: si cierras la pestaña se pierden. Conéctate a la nube o descarga el respaldo para conservarlas.")

    st.header("ESTADÍSTICAS")
    n_user = sum(1 for m in st.session_state.chat if m["role"] == "user")
    n_tools = sum(len(m.get("trace") or []) for m in st.session_state.chat)
    s1, s2 = st.columns(2)
    s1.metric("Consultas", n_user)
    s2.metric("Herramientas", n_tools)
    st.caption(f"Memoria: últimos {st.session_state.mem_n} mensajes · {len(PRUEBAS)} herramientas · {len({a for _, a, _ in PRUEBAS})} APIs")

# ======================================================================
# DIAGNÓSTICO (si se pidió)
# ======================================================================
if st.session_state.pop("run_diag", False):
    with st.status("Verificando conectividad con las fuentes de datos...", expanded=True) as estado:
        st.session_state.diag = ejecutar_diagnostico()
        fallas = sum(1 for f in st.session_state.diag if f["Estado"] == "❌")
        if fallas:
            estado.update(label=f"Diagnóstico terminado: {fallas} sistema(s) con fallas", state="error")
        else:
            estado.update(label="Diagnóstico terminado: todos los sistemas operativos", state="complete")

if st.session_state.get("diag"):
    with st.expander("Resultado del diagnóstico", expanded=True):
        st.dataframe(pd.DataFrame(st.session_state.diag), hide_index=True)

# ======================================================================
# PANTALLA DE BIENVENIDA (solo si el chat está vacío)
# ======================================================================
if not st.session_state.chat:
    st.markdown(
        html(f"""
        <div class="brief">
            <div class="brief-tag">SISTEMA EN LÍNEA</div>
            <div class="brief-title">Bienvenido a {APP_NAME}</div>
            <p>Asistente de inteligencia financiera con acceso en tiempo real a diez fuentes
            de datos públicas. Consulta cotizaciones, criptoactivos e indicadores macroeconómicos con
            respuestas basadas en datos verificables.</p>
            <div class="cards">
                <div class="card"><div class="ci">◈</div><div class="ct">Divisas</div>
                    <div class="cd">Tipo de cambio de mercado y oficial del Banguat, histórico y conversión de montos.</div></div>
                <div class="card"><div class="ci">◈</div><div class="ct">Criptoactivos</div>
                    <div class="cd">Precios en vivo, ranking por capitalización e índice de miedo y codicia.</div></div>
                <div class="card"><div class="ci">◈</div><div class="ct">Macroeconomía</div>
                    <div class="cd">Gráficas históricas, proyecciones del FMI, deuda de EE. UU. y datos por país.</div></div>
            </div>
            <p class="brief-hint">Elige una consulta rápida en el panel lateral o escribe tu pregunta abajo.</p>
        </div>
        """),
        unsafe_allow_html=True,
    )

# ======================================================================
# HISTORIAL
# ======================================================================
for m in st.session_state.chat:
    with st.chat_message(m["role"], avatar=AVATARES[m["role"]]):
        st.markdown(m["content"])
        mostrar_graficos(m.get("trace"))
        mostrar_trace(m.get("trace"))

# ======================================================================
# ENTRADA (chat o botón de misión rápida)
# ======================================================================
pendiente = st.session_state.pop("pending", None)
escrito = st.chat_input("Escribe tu consulta financiera...")
user_text = (pendiente or escrito or "").strip()

if user_text:
    st.session_state.chat.append({"role": "user", "content": user_text})
    _conv = st.session_state.convs[st.session_state.current]
    if _conv["title"] == TITULO_NUEVA:
        _conv["title"] = user_text if len(user_text) <= 40 else user_text[:39] + "…"
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
        mostrar_graficos(trace)
        mostrar_trace(trace)

    st.session_state.chat.append(
        {"role": "assistant", "content": assistant_text, "trace": trace}
    )
    st.session_state.memory.add("user", user_text)
    st.session_state.memory.add("assistant", assistant_text)
    st.session_state.convs[st.session_state.current]["updated"] = _ahora()
    sincronizar(st.session_state.convs[st.session_state.current])
    st.rerun()  # refresca el historial y las estadísticas

st.markdown(
    f'<div class="hud-foot">{APP_NAME} CAPITAL INTELLIGENCE · INFORMACIÓN DE CARÁCTER INFORMATIVO, NO CONSTITUYE ASESORÍA FINANCIERA</div>',
    unsafe_allow_html=True,
)
