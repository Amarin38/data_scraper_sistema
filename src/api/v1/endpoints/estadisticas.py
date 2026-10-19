from fastapi import APIRouter
from statsmodels.iolib.summary import summary

from src.api.deps import DB
from src.api.schemas.estadisticas_schema import (
    DuracionRepuestosOut,
    IndiceConsumoOut,
    PrevisionOut,
)
from src.repositories.estadisticas import (
    DuracionRepuestosRepository,
    IndiceConsumoRepository,
    PrevisionRepository,
)

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])
repo_indice = IndiceConsumoRepository()
repo_prevision = PrevisionRepository()
repo_duraciones = DuracionRepuestosRepository()


@router.get(
    "/indices-consumo/{id_repuesto}",
    response_model=list[IndiceConsumoOut],
    status_code=200,
    summary="Devuelve los indices de consumo de un repuesto.",
)
def mostrar_indices(
    id_repuesto: int,
    db: DB,
):
    return repo_indice.listar_por_repuesto(db, id_repuesto)


@router.get(
    "/previsiones/{id_repuesto}",
    response_model=list[PrevisionOut],
    status_code=200,
    summary="Devuelve las previsiones de un repuesto.",
)
def mostrar_previsiones(id_repuesto: int, db: DB):
    return repo_prevision.listar_por_repuesto(db, id_repuesto)


@router.get(
    "/duracion-repuestos/{id_repuesto}",
    response_model=list[DuracionRepuestosOut],
    status_code=200,
    summary="Devuelve la duracion de un repuesto.",
)
def mostrar_duracion(id_repuesto: int, db: DB):
    return repo_duraciones.listar_por_repuesto(db, id_repuesto)
