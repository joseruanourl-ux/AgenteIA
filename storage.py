"""Guardado de conversaciones en Supabase.

Habla directamente con la API REST de Supabase (PostgREST) usando `requests`,
así no hace falta instalar librerías nuevas.
"""
import hashlib
import json

import requests
import streamlit as st

TABLA = "conversaciones"
TIMEOUT = 20


def _config():
    try:
        return str(st.secrets["SUPABASE_URL"]).rstrip("/"), str(st.secrets["SUPABASE_KEY"])
    except Exception:
        return None


def disponible() -> bool:
    return _config() is not None


def _cabeceras(extra=None):
    _, clave = _config()
    # Con las claves nuevas (sb_secret_...) se envía SOLO 'apikey'. Si además se manda como
    # 'Authorization: Bearer', Supabase intenta leerla como JWT y responde "Invalid JWT".
    cab = {"apikey": clave, "Content-Type": "application/json"}
    cab.update(extra or {})
    return cab


def _endpoint() -> str:
    return f"{_config()[0]}/rest/v1/{TABLA}"


def _verificar(r):
    if r.status_code < 400:
        return
    pistas = {
        401: "revisa SUPABASE_KEY",
        403: "revisa SUPABASE_KEY (debe ser la clave secret, no la publishable)",
        404: "¿ejecutaste el SQL que crea la tabla 'conversaciones'?",
    }
    raise RuntimeError(f"Supabase respondió {r.status_code} ({pistas.get(r.status_code, 'error')}): {r.text[:160]}")


def calcular_owner(nombre: str, pin: str) -> str:
    # El "dueño" de las conversaciones es un hash de usuario + PIN: en la base de datos
    # nunca se guarda ni el nombre ni el PIN en texto.
    try:
        sal = str(st.secrets.get("OWNER_SALT", "aurum-capital"))
    except Exception:
        sal = "aurum-capital"
    base = f"{nombre.strip().lower()}|{pin}".encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", base, sal.encode("utf-8"), 120_000).hex()


def listar(owner: str) -> list:
    r = requests.get(
        _endpoint(),
        params={"owner": f"eq.{owner}", "select": "id,title,created,updated,chat",
                "order": "updated.desc", "limit": 200},
        headers=_cabeceras(), timeout=TIMEOUT)
    _verificar(r)
    return r.json() or []


def guardar(owner: str, conv: dict):
    fila = {
        "owner": owner,
        "id": conv["id"],
        "title": conv.get("title") or "Nueva conversación",
        "created": conv.get("created"),
        "updated": conv.get("updated"),
        "chat": json.loads(json.dumps(conv["chat"], default=str)),
    }
    r = requests.post(
        _endpoint(), params={"on_conflict": "owner,id"}, data=json.dumps(fila, ensure_ascii=False).encode("utf-8"),
        headers=_cabeceras({"Prefer": "resolution=merge-duplicates,return=minimal"}), timeout=TIMEOUT)
    _verificar(r)


def eliminar(owner: str, cid: str):
    r = requests.delete(
        _endpoint(), params={"owner": f"eq.{owner}", "id": f"eq.{cid}"},
        headers=_cabeceras({"Prefer": "return=minimal"}), timeout=TIMEOUT)
    _verificar(r)


def probar():
    # Devuelve None si la conexión y la tabla funcionan; si no, un texto con el motivo.
    try:
        r = requests.get(_endpoint(), params={"select": "id", "limit": 1}, headers=_cabeceras(), timeout=TIMEOUT)
        _verificar(r)
        return None
    except Exception as e:
        return str(e)
