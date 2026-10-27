from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.enums import TipoUsuarioLoginEnum
from src.core.security import leer_token
from src.db.models.usuario_model import UsuarioModel
from src.db.session import SessionLocal

COOKIE = "token"


def get_db():
    with SessionLocal() as s:
        yield s


def usuario_actual(
    token: str | None = Cookie(default=None, alias=COOKIE),
    db: Session = Depends(get_db),
) -> UsuarioModel:
    datos = leer_token(token) if token else None
    if not datos:
        raise HTTPException(401, "No autenticado")
    u = db.get(UsuarioModel, int(datos["sub"]))
    if not u or not u.Activo:
        raise HTTPException(401, "No autenticado")
    return u


def solo_admin(u: UsuarioModel = Depends(usuario_actual)) -> UsuarioModel:
    if u.TipoUser != TipoUsuarioLoginEnum.ADMIN:
        raise HTTPException(403, "Sin permiso")
    return u
