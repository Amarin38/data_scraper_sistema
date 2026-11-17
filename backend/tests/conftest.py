import os

import httpx
import pytest
from rutas import BASE

API = f"{BASE}/api/v1"


@pytest.fixture(scope="session")
def credenciales():
    user, password = os.getenv("TEST_USER", ""), os.getenv("TEST_PASSWORD", "")
    if not (user and password):
        pytest.exit(
            "Faltan TEST_USER y TEST_PASSWORD (uv run --env-file .env pytest)",
            returncode=2,
        )
    return {"user": user, "password": password}


@pytest.fixture(scope="session")
def api(credenciales):
    """Cliente logueado: la cookie queda en el jar y viaja sola en cada request."""
    with httpx.Client(base_url=API, timeout=60) as cliente:
        r = cliente.post("/auth/login", json=credenciales)
        if r.status_code != 200:
            pytest.exit(
                f"Login de tests falló ({r.status_code}): {r.text[:200]}", returncode=2
            )
        yield cliente


@pytest.fixture
def anon():
    """Cliente sin sesión, nuevo en cada test (no comparte cookies)."""
    with httpx.Client(base_url=API, timeout=60) as cliente:
        yield cliente


@pytest.fixture(scope="session")
def repuesto(api):
    r = api.get("/repuestos", params={"limit": 1, "page": 0})
    assert r.status_code == 200, r.text[:300]
    items = r.json()["items"]
    assert items, "La base no tiene repuestos"
    return items[0]


@pytest.fixture(scope="session")
def repuesto_con_consumo(api):
    r = api.get("/inicio/datos-rapidos")
    assert r.status_code == 200, r.text[:300]
    top = r.json()["mayor_stock"]
    if not top:
        pytest.skip("No hay consumo en el último mes")
    return top[0]["IDRepuesto"]
