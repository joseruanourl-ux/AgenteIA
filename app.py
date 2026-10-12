import streamlit as st
from groq import Groq

from agent import process_response
from basic_memory import BasicMemory

MEMORY_MAX_MESSAGES = 10

st.set_page_config(page_title="R2D2", page_icon="🤖")
st.title("🤖 R2D2")
st.caption("Tipo de cambio, criptomonedas e indicadores del Banco Mundial.")

# --- Cliente de Groq (la clave viene de los Secrets de Streamlit) ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Falta configurar GROQ_API_KEY en los Secrets de la app.")
    st.stop()


@st.cache_resource
def get_client(key: str) -> Groq:
    return Groq(api_key=key)


client = get_client(api_key)

# --- Estado de la sesión: memoria del agente + historial visible ---
if "memory" not in st.session_state:
    st.session_state.memory = BasicMemory(max_messages=MEMORY_MAX_MESSAGES)
if "chat" not in st.session_state:
    st.session_state.chat = []

# --- Barra lateral ---
with st.sidebar:
    st.header("Ejemplos")
    st.markdown(
        "- ¿Cuánto es 100 USD en quetzales?\n"
        "- ¿Cuál es el precio de bitcoin?\n"
        "- Top 5 criptomonedas\n"
        "- Inflación en Guatemala\n"
        "- Compara el desempleo de GT, MX y US\n"
        "- Tipo de cambio EUR a USD el 2024-01-15\n"
        "- Información de Guatemala"
    )
    if st.button("🗑️ Borrar conversación"):
        st.session_state.memory = BasicMemory(max_messages=MEMORY_MAX_MESSAGES)
        st.session_state.chat = []
        st.rerun()

# --- Mostrar el historial ---
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- Entrada del usuario ---
user_text = st.chat_input("Escribe tu mensaje...")

if user_text:
    user_text = user_text.strip()

if user_text:
    st.session_state.chat.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                assistant_text = process_response(
                    client, st.session_state.memory.messages(), user_text
                )
            except Exception as e:
                assistant_text = f"Ocurrió un error al contactar al modelo: {e}"
        st.markdown(assistant_text)

    st.session_state.chat.append({"role": "assistant", "content": assistant_text})
    st.session_state.memory.add("user", user_text)
    st.session_state.memory.add("assistant", assistant_text)
