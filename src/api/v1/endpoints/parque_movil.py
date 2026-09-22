from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.pagina import Pagina
from src.api.schemas.parque_movil_schema import ParqueMovilHistorialOut, ParqueMovilOut
from src.api.utils import Cursor, Limite
from src.repositories.parque_movil_repository import (
    ParqueMovilHistorialRepository,
    ParqueMovilRepository,
)

router = APIRouter(prefix="/parques-moviles", tags=["parques-moviles"])
repo_parque = ParqueMovilRepository()
repo_parque_historial = ParqueMovilHistorialRepository()


@router.get(
    "/",
    response_model=Pagina[ParqueMovilOut],
    status_code=200,
    summary="Muestra el parque movil.",
)
def mostrar_parque(db: DB, limit: Limite = 300, cursor: Cursor = 0):
    items, next_cursor = repo_parque.listar_pagina(db, limit=limit, cursor=cursor)

    return {"items": items, "next_cursor": next_cursor}


@router.get(
    "/historiales",
    response_model=Pagina[ParqueMovilHistorialOut],
    status_code=200,
    summary="Muestra el historial del parque movil",
)
def mostrar_parque_historial(db: DB, limit: Limite = 500, cursor: Cursor = 0):
    items, next_cursor = repo_parque_historial.listar_pagina(
        db, limit=limit, cursor=cursor
    )

    return {"items": items, "next_cursor": next_cursor}
