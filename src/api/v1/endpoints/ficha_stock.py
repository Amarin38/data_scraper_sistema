from typing import Any
from datetime import date

from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.ficha_stock_schema import FichaStockPaginadoOut
from src.api.utils import Limite
from src.core.enums import CabecerasEnum, TipoMovEnum
from src.repositories.ficha_stock_repository import FichaStockRepository

router = APIRouter(prefix="/ficha-stock", tags=["ficha-stock"])
repo = FichaStockRepository()


@router.get(
    "",
    response_model=FichaStockPaginadoOut,
    status_code=200,
    summary="Muestra la ficha de stock.",
)
def listar(
    db: DB,
    deposito: CabecerasEnum | None = None,
    descripcion: str | None = None,
    codigo: str | None = None,
    movimiento: TipoMovEnum | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    limit: Limite = 50,
    cursor_valor: date | None = None,
    cursor_id: int | None = None,
):
    return repo.listar_ficha(
        db,
        deposito,
        descripcion,
        codigo,
        movimiento,
        fecha_desde,
        fecha_hasta,
        limit,
        cursor_valor,
        cursor_id,
    )


@router.get(
    "/cabeceras",
    response_model=list[str],
    status_code=200,
    summary="Devuelve las cabeceras",
)
def get_cabeceras():
    return [c.value for c in CabecerasEnum]


@router.get(
    "/movimientos",
    response_model=list[str],
    status_code=200,
    summary="Devuelve los tipos de movimientos",
)
def get_movimientos():
    return [c.value for c in TipoMovEnum]
