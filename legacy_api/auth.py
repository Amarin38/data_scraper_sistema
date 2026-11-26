from typing import Annotated

from fastapi import Cookie, Depends, HTTPException

from legacy_api.deps import DB
from legacy_api.security import leer_token
from shared.core.enums import TipoUsuarioLoginEnum
from shared.db.models.usuario_model import UsuarioModel

COOKIE = "token"


def usuario_actual(
    db: DB,
    token: Annotated[str | None, Cookie(alias=COOKIE)] = None,
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

    def _chequeo(u: Annotated[UsuarioModel, Depends(usuario_actual)]) -> UsuarioModel:
        if u.TipoUser not in roles:
            raise HTTPException(403, "Sin permiso")
        return u

    return _chequeo


req_all = requiere(
    TipoUsuarioLoginEnum.OWNER, TipoUsuarioLoginEnum.ADMIN, TipoUsuarioLoginEnum.USER
)
req_owner = requiere(TipoUsuarioLoginEnum.OWNER)
req_admin = requiere(TipoUsuarioLoginEnum.OWNER, TipoUsuarioLoginEnum.ADMIN)

REQ_ALL = Annotated[UsuarioModel, Depends(req_all)]
REQ_OWNER = Annotated[UsuarioModel, Depends(req_owner)]
REQ_ADMIN = Annotated[UsuarioModel, Depends(req_admin)]
USUARIO = Annotated[UsuarioModel, Depends(usuario_actual)]
