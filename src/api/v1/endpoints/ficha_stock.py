from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.ficha_stock_schema import FichaStockOut
from src.repositories.ficha_stock_repository import FichaStockRepository

router = APIRouter(prefix="/ficha", tags=["ficha"])
repo = FichaStockRepository()


@router.get("", response_model=list[FichaStockOut])
def listar(db: DB):
    return repo.list(db)
