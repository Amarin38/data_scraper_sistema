import os

import httpx
import pytest

BASE = os.getenv("API_URL", "http://127.0.0.1:8001")


@pytest.fixture(scope="session")
def api():
    with httpx.Client(base_url=f"{BASE}/api/v1", timeout=60) as cliente:
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
