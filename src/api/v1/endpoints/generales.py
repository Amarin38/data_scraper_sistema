from fastapi import APIRouter

from src.api.deps import DB
from src.core.enums import CabecerasEnum

router = APIRouter(prefix="", tags=["repuestos"])


@router.get(
    "/cabeceras",
    response_model=list[str],
    status_code=200,
    summary="Devuelve las cabeceras",
)
def get_cabeceras():
    return [c.value for c in CabecerasEnum]
