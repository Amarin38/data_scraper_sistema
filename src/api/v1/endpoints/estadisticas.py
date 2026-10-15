from fastapi import APIRouter

from src.api.deps import DB
from src.api.schemas.indice_consumo_schema import (
    IndiceConsumoOut,
    PaginadoIndiceConsumoTablaOut,
)
from src.api.utils import Limite
from src.repositories.estadisticas import IndiceConsumoRepository

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])
repo_indice = IndiceConsumoRepository()


@router.get(
    "/indices-consumo",
    response_model=PaginadoIndiceConsumoTablaOut,
    status_code=200,
    summary="Devuelve los datos necesarios de los indices para la tabla",
)
def mostrar_peores(
    db: DB,
    conjunto: str | None = None,
    texto: str | None = None,
    limit: Limite = 50,
    cursor_valor: float | None = None,
    cursor_id: int | None = None,
):
    return repo_indice.listar_peores(
        db, conjunto, texto, limit, cursor_valor, cursor_id
    )


@router.get(
    "/indices-consumo/{id_repuesto}",
    response_model=list[IndiceConsumoOut],
    status_code=200,
    summary="Devuelve los indices de consumo de todos los repuestos.",
)
def mostrar_indices(
    id_repuesto: int,
    db: DB,
):
    return repo_indice.listar_por_repuesto(db, id_repuesto)
