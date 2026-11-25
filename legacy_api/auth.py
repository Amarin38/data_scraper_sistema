from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from legacy_api.security import leer_token
from shared.core.enums import TipoUsuarioLoginEnum
from shared.db.models.usuario_model import UsuarioModel
from shared.db.session import SessionLocal

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


def requiere(*roles: TipoUsuarioLoginEnum):
    """Dependencia que deja pasar solo a los roles indicados."""

    def _chequeo(u: UsuarioModel = Depends(usuario_actual)) -> UsuarioModel:
        if u.TipoUser not in roles:
            raise HTTPException(403, "Sin permiso")
        return u

    return _chequeo


req_all = requiere(
    TipoUsuarioLoginEnum.OWNER, TipoUsuarioLoginEnum.ADMIN, TipoUsuarioLoginEnum.USER
)
req_owner = requiere(TipoUsuarioLoginEnum.OWNER)
req_admin = requiere(TipoUsuarioLoginEnum.OWNER, TipoUsuarioLoginEnum.ADMIN)
