import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from rutas import BASE, RUTAS_TODAS, con_ids

JWT_SECRET = os.getenv("JWT_SECRET")
necesita_secret = pytest.mark.skipif(
    not JWT_SECRET, reason="JWT_SECRET no está en el entorno de los tests"
)


def _atributos(set_cookie: str) -> list[str]:
    return [a.strip().lower() for a in set_cookie.split(";")]


def _token(clave: str, sub, delta: timedelta) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {"sub": str(sub), "tipo": "User", "iat": ahora, "exp": ahora + delta}
    return jwt.encode(payload, clave, algorithm="HS256")


def test_salud_es_publico(anon):
    assert anon.get("/salud").status_code == 200


@pytest.mark.parametrize("ruta", RUTAS_TODAS)
def test_get_sin_sesion_da_401(anon, ruta):
    r = anon.get(BASE + con_ids(ruta, 1))
    assert r.status_code == 401, f"{ruta} quedó sin proteger ({r.status_code})"


def test_login_ok_setea_cookie_segura_y_no_expone_el_token(anon, credenciales):
    r = anon.post("/auth/login", json=credenciales)
    assert r.status_code == 200
    assert set(r.json()) == {"user", "tipo"}
    attrs = _atributos(r.headers["set-cookie"])
    assert attrs[0].startswith("token=")
    assert "httponly" in attrs and "samesite=lax" in attrs
    assert "secure" not in attrs  # http directo: no puede llevar Secure


def test_cookie_lleva_secure_detras_de_https(anon, credenciales):
    r = anon.post(
        "/auth/login", json=credenciales, headers={"X-Forwarded-Proto": "https"}
    )
    assert r.status_code == 200
    assert "secure" in _atributos(r.headers["set-cookie"])


def test_login_ignora_mayusculas_y_espacios(anon, credenciales):
    r = anon.post(
        "/auth/login",
        json={**credenciales, "user": f"  {credenciales['user'].upper()} "},
    )
    assert r.status_code == 200


def test_login_mal_da_401_igual_para_usuario_inexistente(anon, credenciales):
    a = anon.post(
        "/auth/login", json={"user": credenciales["user"], "password": "incorrecta-xyz"}
    )
    b = anon.post(
        "/auth/login", json={"user": "no-existe-xyz", "password": "incorrecta-xyz"}
    )
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json()  # no revela si el usuario existe
    assert "set-cookie" not in a.headers


def test_login_sin_campos_da_422(anon):
    assert anon.post("/auth/login", json={"user": "x"}).status_code == 422


def test_yo_con_sesion(api, credenciales):
    d = api.get("/auth/yo").json()
    assert d["user"] == credenciales["user"].strip().lower()
    assert d["tipo"] in {"Admin", "User"}


def test_logout_borra_la_cookie(anon, credenciales):
    anon.post("/auth/login", json=credenciales)
    assert anon.get("/auth/yo").status_code == 200
    assert anon.post("/auth/logout").status_code == 200
    assert anon.get("/auth/yo").status_code == 401


def test_token_basura_da_401(anon):
    r = anon.get("/auth/yo", headers={"Cookie": "token=abc.def.ghi"})
    assert r.status_code == 401


def test_token_firmado_con_otra_clave_da_401(anon):
    t = _token("una-clave-equivocada-de-al-menos-32-caracteres", 1, timedelta(hours=1))
    assert anon.get("/auth/yo", headers={"Cookie": f"token={t}"}).status_code == 401


@necesita_secret
def test_token_vencido_da_401(anon):
    t = _token(JWT_SECRET, 1, timedelta(hours=-1))
    assert anon.get("/auth/yo", headers={"Cookie": f"token={t}"}).status_code == 401


@necesita_secret
def test_token_valido_de_usuario_inexistente_da_401(anon):
    t = _token(JWT_SECRET, 999_999_999, timedelta(hours=1))
    assert anon.get("/auth/yo", headers={"Cookie": f"token={t}"}).status_code == 401
