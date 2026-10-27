from src.core.enums import FormatoEnum
from src.core.exports import exportacion, iterar_filas, limpiar_nombre
from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.existencia_stock_schema import (
    ExistenciaStockOffsetOut,
    ExistenciaStockOut,
)
from src.api.utils import Limite
from src.repositories.existencia_stock_repository import ExistenciaStockRepository

router = APIRouter(prefix="/existencia-stock", tags=["existencias"])
repo = ExistenciaStockRepository()
COLUMNAS_EXPORT = [c for c in ExistenciaStockOut.model_fields if c != "IDExistencia"]


@router.get(
    "",
    response_model=ExistenciaStockOffsetOut,
    status_code=200,
    summary="Lista la existencia de stock.",
)
def listar(
    db: DB,
    descripcion: str | None = None,
    codigo: str | None = None,
    conjunto: str | None = None,
    limit: Limite = 50,
    page: int = 0,
):
    return repo.get_existencias(db, descripcion, codigo, conjunto, limit, page)


@router.get(
    "/exportar",
)
def exportar_ficha(
    formato: FormatoEnum = FormatoEnum.CSV,
    nombre: str | None = None,
    validar: bool | None = False,
    descripcion: str | None = None,
    codigo: str | None = None,
    conjunto: str | None = None,
):
    stmt = repo.stmt_exportar(
        descripcion=descripcion,
        codigo=codigo,
        conjunto=conjunto,
    )

    return exportacion(
        stmt,
        COLUMNAS_EXPORT,
        formato,
        limpiar_nombre(nombre) or "existencia_stock",
        validar=validar,
    )
