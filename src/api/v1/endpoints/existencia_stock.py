from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas.existencia_stock_schema import ExistenciaStockOut
from src.repositories.existencia_stock_repository import ExistenciaStockRepository

router = APIRouter(prefix="/existencia", tags=["ficha"])
repo = ExistenciaStockRepository()


@router.get("", response_model=list[ExistenciaStockOut])
def listar(db: Session = Depends(get_db)):
    return repo.list(db)
