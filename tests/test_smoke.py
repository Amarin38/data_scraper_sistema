import os
import re

import httpx
import pytest

BASE = os.getenv("API_URL", "http://127.0.0.1:8001")
TIEMPO_MAX = 2.0  # segundos por request


def _rutas_get():
    try:
        spec = httpx.get(f"{BASE}/openapi.json", timeout=10).json()
    except Exception:
        return []
    rutas = []
    for ruta, metodos in spec["paths"].items():
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


RUTAS = _rutas_get()


def test_openapi_disponible():
    assert RUTAS, f"No se pudo leer {BASE}/openapi.json: ¿la API está levantada?"


@pytest.mark.parametrize("ruta,query", RUTAS, ids=[r for r, _ in RUTAS])
def test_get_responde_200_y_rapido(ruta, query, repuesto):
    url = re.sub(r"\{[^}]+\}", str(repuesto["IDRepuesto"]), ruta)
    r = httpx.get(BASE + url, params=query, timeout=60)
    assert r.status_code == 200, r.text[:300]
    r.json()
    assert r.elapsed.total_seconds() < TIEMPO_MAX, f"{r.elapsed.total_seconds():.2f}s"
