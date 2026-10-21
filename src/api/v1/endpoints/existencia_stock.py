from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.existencia_stock_schema import (
    ExistenciaStockOffsetOut,
)
from src.api.utils import Limite
from src.repositories.existencia_stock_repository import ExistenciaStockRepository

router = APIRouter(prefix="/existencia-stock", tags=["existencias"])
repo = ExistenciaStockRepository()


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
    return repo.listar_existencias(db, descripcion, codigo, conjunto, limit, page)
