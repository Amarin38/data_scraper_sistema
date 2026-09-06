from typing import Annotated

from fastapi import APIRouter, Query

from src.api.deps import DB
from src.api.schemas.repuesto_schema import RepuestoOut
from src.repositories.repuesto_repository import RepuestoRepository

router = APIRouter(prefix="/repuestos", tags=["repuestos"])
repo = RepuestoRepository()


@router.get("", response_model=list[RepuestoOut])
def listar(
    db: DB,
    limit: Annotated[int, Query(le=1000)] = 50,
):
    return repo.list(db, limit=limit)
