from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import DB
from src.api.schemas.existencia_stock_schema import (
    ExistenciaStockOffsetOut,
    ExistenciaStockOut,
)
from src.api.utils import Limite
from src.core.enums import FormatoEnum
from src.core.exports import exportacion, limpiar_nombre
from src.repositories.existencia_stock_repository import (
    DEPOSITO_EXISTENCIA,
    MIN_MESES_CON_DATOS,
    ExistenciaStockRepository,
    rango_meses,
)

router = APIRouter(prefix="/existencia-stock", tags=["existencias"])
repo = ExistenciaStockRepository()
COLUMNAS_EXPORT = [c for c in ExistenciaStockOut.model_fields if c != "IDExistencia"]


def minmax(
    meses_min: float | None = Query(None, ge=0, le=60),
    meses_max: float | None = Query(None, ge=0, le=60),
    demanda_desde: date | None = None,
    demanda_hasta: date | None = None,
    min_meses_con_datos: int = Query(MIN_MESES_CON_DATOS, ge=1, le=36),
    deposito: str = DEPOSITO_EXISTENCIA,
):
    if meses_min is None or meses_max is None:
        return None  # sin meses no se calcula nada
    if meses_max < meses_min:
        raise HTTPException(422, "El máximo no puede ser menor que el mínimo")

    ini, fin, n = rango_meses(demanda_desde, demanda_hasta)
    if n < 1:
        raise HTTPException(422, "El rango no incluye ningún mes cerrado")

    return {
        "ini": ini,
        "fin": fin,
        "n": n,
        "meses_min": meses_min,
        "meses_max": meses_max,
        "min_datos": min(min_meses_con_datos, max(1, n // 2)),
        "deposito": deposito,
    }


MinMax = Annotated[dict | None, Depends(minmax)]


@router.get(
    "",
    response_model=ExistenciaStockOffsetOut,
    status_code=200,
    summary="Lista la existencia de stock.",
)
def listar(
    db: DB,
    mm: MinMax,
    descripcion: str | None = None,
    codigo: str | None = None,
    conjunto: str | None = None,
    solo_con_minmax: bool = False,
    limit: Limite = 50,
    page: int = 0,
    orden: str | None = None,
    direccion: Literal["asc", "desc"] = "asc",
):
    return repo.get_existencias(
        db,
        descripcion,
        codigo,
        conjunto,
        limit,
        page,
        mm,
        solo_con_minmax and mm is not None,
        orden,
        direccion,
    )


@router.get(
    "/exportar",
)
def exportar_ficha(
    mm: MinMax,
    formato: FormatoEnum = FormatoEnum.CSV,
    nombre: str | None = None,
    validar: bool | None = False,
    descripcion: str | None = None,
    codigo: str | None = None,
    conjunto: str | None = None,
    solo_con_minmax: bool = False,
    orden: str | None = None,
    direccion: Literal["asc", "desc"] = "asc",
):
    stmt = repo.stmt_exportar(
        descripcion=descripcion,
        codigo=codigo,
        conjunto=conjunto,
        mm=mm,
        con_max_min=solo_con_minmax and mm is not None,
        orden=orden,
        direccion=direccion,
    )
    return exportacion(
        stmt,
        COLUMNAS_EXPORT,
        formato,
        limpiar_nombre(nombre) or "existencia_stock",
        validar=validar,
    )
