import pytest
from rutas import BASE, RUTAS, con_ids

TIEMPO_MAX = 2.0  # segundos por request


def test_openapi_disponible():
    assert RUTAS, f"No se pudo leer {BASE}/openapi.json: ¿la API está levantada?"


@pytest.mark.parametrize("ruta,query", RUTAS, ids=[r for r, _ in RUTAS])
def test_get_responde_200_y_rapido(api, repuesto, ruta, query):
    r = api.get(BASE + con_ids(ruta, repuesto["IDRepuesto"]), params=query)
    assert r.status_code == 200, r.text[:300]
    assert "application/json" in r.headers["content-type"]
    r.json()
    assert r.elapsed.total_seconds() < TIEMPO_MAX, f"{r.elapsed.total_seconds():.2f}s"
