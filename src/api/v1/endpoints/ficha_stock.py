from datetime import date

from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.ficha_stock_schema import FichaStockOut, FichaStockPaginadoOut
from src.api.utils import Limite
from src.core.enums import CabecerasEnum, FormatoEnum, TipoMovEnum
from src.core.exports import exportacion, iterar_filas, limpiar_nombre
from src.repositories.ficha_stock_repository import FichaStockRepository

router = APIRouter(prefix="/ficha-stock", tags=["ficha-stock"])
repo = FichaStockRepository()

COLUMNAS_EXPORT = [
    c for c in FichaStockOut.model_fields if c not in ("IDFichaStock", "IDRepuesto")
]


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
    return repo.get_ficha(
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
    "/movimientos",
    response_model=list[str],
    status_code=200,
    summary="Devuelve los tipos de movimientos",
)
def get_movimientos():
    return [c.value for c in TipoMovEnum]


@router.get(
    "/exportar",
)
def exportar_ficha(
    formato: FormatoEnum = FormatoEnum.CSV,
    nombre: str | None = None,
    validar: bool | None = False,
    deposito: CabecerasEnum | None = None,
    descripcion: str | None = None,
    codigo: str | None = None,
    movimiento: TipoMovEnum | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
):
    stmt = repo.stmt_exportar(
        deposito=deposito,
        descripcion=descripcion,
        codigo=codigo,
        movimiento=movimiento,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    return exportacion(
        stmt,
        COLUMNAS_EXPORT,
        formato,
        limpiar_nombre(nombre) or "ficha_stock",
        validar=validar,
    )
