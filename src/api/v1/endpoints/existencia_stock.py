from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.existencia_stock_schema import (
    ExistenciaStockOut,
    ExistenciaStockPatch,
)
from src.api.utils import Cursor, Limite, no_existe_existencia
from src.repositories.existencia_stock_repository import ExistenciaStockRepository

router = APIRouter(prefix="/existencias", tags=["existencias"])
repo = ExistenciaStockRepository()


@router.get(
    "/",
    response_model=list[ExistenciaStockOut],
    status_code=200,
    summary="Lista la existencia de stock.",
)
def listar(db: DB, limit: Limite = 100, cursor: Cursor = 0):
    items, next_cursor = repo.listar_pagina(db, limit=limit, cursor=cursor)

    return {"items": items, "next_cursor": next_cursor}


@router.patch(
    "/{id_existencia}",
    response_model=ExistenciaStockOut,
    status_code=200,
    summary="Modifica el stock de un repuesto.",
)
def cambiar_stock(id_existencia: int, payload: ExistenciaStockPatch, db: DB):
    obj = repo.get_by_id(db, id_existencia)

    if obj is None:
        raise no_existe_existencia

    obj.Stock = payload.Stock

    db.commit()
    db.refresh(obj)

    return obj
