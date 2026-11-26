from datetime import date

from fastapi import APIRouter, HTTPException, Request, Response
from sqlalchemy import select

from legacy_api.auth import COOKIE, USUARIO
from legacy_api.deps import DB
from legacy_api.schemas.auth_schema import LoginIn, PreferenciasIn
from legacy_api.security import DURACION_HORAS, crear_token, verificar
from shared.db.models.usuario_model import UsuarioModel

router = APIRouter(prefix="/auth", tags=["auth"])


def _perfil(u: UsuarioModel) -> dict:
    return {"user": u.User, "tipo": u.TipoUser.value, "modo_noche": u.ModoNoche}


# def (no async): argon2 es CPU y bloquearía el event loop
@router.post("/login")
def login(datos: LoginIn, request: Request, response: Response, db: DB):
    u = db.scalar(
        select(UsuarioModel).where(UsuarioModel.User == datos.user.strip().lower())
    )
    ok = verificar(datos.password, u.PasswordHash if u else None)

    if not (ok and u and u.Activo):
        raise HTTPException(401, "Usuario o contraseña incorrectos")

    u.UltimoLogin = date.today()
    db.commit()

    response.set_cookie(
        COOKIE,
        crear_token(u.IDUsuario, u.TipoUser.value),
        max_age=DURACION_HORAS * 3600,
        httponly=True,
        samesite="lax",
        secure=request.headers.get("x-forwarded-proto") == "https",
        path="/",
    )
    return _perfil(u)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@router.get(path="/yo")
def yo(u: USUARIO):
    return _perfil(u)


@router.put(path="/preferencias")
def guardar_preferencias(
    datos: PreferenciasIn,
    u: USUARIO,
    db: DB,
):
    u.ModoNoche = datos.modo_noche
    db.commit()
    return _perfil(u)
