from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.schemas.auth_schema import LoginIn
from src.core.auth import COOKIE, get_db, usuario_actual
from src.core.security import DURACION_HORAS, crear_token, verificar
from src.db.models.usuario_model import UsuarioModel

router = APIRouter(prefix="/auth", tags=["auth"])


# def (no async): argon2 es CPU y bloquearía el event loop
@router.post("/login")
def login(
    datos: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)
):
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
    return {"user": u.User, "tipo": u.TipoUser.value}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@router.get("/yo")
def yo(u: UsuarioModel = Depends(usuario_actual)):
    return {"user": u.User, "tipo": u.TipoUser.value}
