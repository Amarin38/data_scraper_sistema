from fastapi import APIRouter, HTTPException

from legacy_api.auth import USUARIO
from legacy_api.deps import DB
from legacy_api.schemas.usuario_preferencia_schema import TableroIn, TableroOut
from shared.core.paneles import paneles_permitidos
from shared.repositories import usuario_preferencia_repository as repo

CLAVE = "inicio.tablero"
router = APIRouter(prefix="/usuario/preferencias/inicio", tags=["preferencias"])


def _permitidos(usuario: USUARIO) -> set[str]:
    return paneles_permitidos(usuario.TipoUser)


@router.get("", response_model=TableroOut)
def leer(db: DB, usuario: USUARIO):
    doc = repo.obtener(db, usuario.IDUsuario, CLAVE) or {"v": 1, "Paneles": {}}
    return TableroOut(
        v=doc.get("v", 1),
        Paneles=doc.get("Paneles", {}),
        Permitidos=sorted(_permitidos(usuario)),
    )


@router.put("", status_code=204)
def guardar(body: TableroIn, db: DB, usuario: USUARIO):
    ok = _permitidos(usuario)
    limpio = {pid: c.model_dump() for pid, c in body.Paneles.items() if pid in ok}
    repo.guardar(db, usuario.IDUsuario, CLAVE, {"v": 1, "Paneles": limpio})


@router.delete("", status_code=204)
def restablecer(db: DB, usuario: USUARIO):
    repo.borrar(db, usuario.IDUsuario, CLAVE)


def requiere_panel(panel_id: str):
    def dep(usuario: USUARIO):
        if panel_id not in _permitidos(usuario):
            raise HTTPException(403, "Sin acceso a este panel")

    return dep
