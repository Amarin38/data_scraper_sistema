import os
import re

import httpx

BASE = os.getenv("API_URL", "http://127.0.0.1:8001")


def _paths():
    try:
        return httpx.get(f"{BASE}/openapi.json", timeout=10).json()["paths"]
    except Exception:
        return {}


_PATHS = _paths()

# todos los GET del schema (para verificar que ninguno quede sin proteger)
RUTAS_TODAS = [r for r, m in _PATHS.items() if "get" in m]


def _listos_para_llamar():
    rutas = []
    for ruta, metodos in _PATHS.items():
        get = metodos.get("get")
        if not get or ruta.endswith("/exportar"):
            continue
        params = get.get("parameters", [])
        if any(p["in"] == "query" and p.get("required") for p in params):
            continue
        nombres = {p["name"] for p in params if p["in"] == "query"}
        query = {}
        if "limit" in nombres:
            query["limit"] = 5
        if "page" in nombres:
            query["page"] = 0
        rutas.append((ruta, query))
    return rutas


RUTAS = _listos_para_llamar()


def con_ids(ruta: str, valor) -> str:
    return re.sub(r"\{[^}]+\}", str(valor), ruta)
