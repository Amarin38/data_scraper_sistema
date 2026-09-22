from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.ficha_stock_schema import FichaStockOut
from src.api.schemas.pagina import Pagina
from src.api.utils import Cursor, Limite
from src.repositories.ficha_stock_repository import FichaStockRepository

router = APIRouter(prefix="/fichas-stock", tags=["fichas-stock"])
repo = FichaStockRepository()


@router.get(
    "/",
    response_model=Pagina[FichaStockOut],
    status_code=200,
    summary="Muestra la ficha de stock.",
)
def mostrar_ficha(db: DB, limit: Limite = 300, cursor: Cursor = 0):
    items, next_cursor = repo.listar_pagina(db, limit=limit, cursor=cursor)

    return {"items": items, "next_cursor": next_cursor}
