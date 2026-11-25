from datetime import date

from fastapi import APIRouter, HTTPException

from legacy_api.deps import DB
from legacy_api.schemas.estadisticas_schema import (
    DuracionRepuestosOut,
    IndiceConsumoOut,
    PrevisionOut,
    CoberturaOut,
)
from pipeline.compute.prevision import ComputePrevision
from shared.repositories.estadisticas import (
    DuracionRepuestosRepository,
    IndiceConsumoRepository,
    PrevisionRepository,
)

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])
repo_indice = IndiceConsumoRepository()
repo_prevision = PrevisionRepository()
repo_duraciones = DuracionRepuestosRepository()
calculo_prevision = ComputePrevision()


@router.get(
    "/indices-consumo/{id_repuesto}",
    response_model=list[IndiceConsumoOut],
    status_code=200,
    summary="Devuelve los indices de consumo de un repuesto.",
)
def mostrar_indices(id_repuesto: int, db: DB):
    return repo_indice.listar_por_repuesto(db, id_repuesto)


## PREVISIONES
def _filas_prevision(db, id_repuesto, consumo_desde, consumo_hasta):
    if consumo_desde is None and consumo_hasta is None:
        return repo_prevision.listar_por_repuesto(db, id_repuesto)
    if consumo_desde and consumo_hasta and consumo_desde > consumo_hasta:
        raise HTTPException(422, "«desde» es posterior a «hasta»")
    return calculo_prevision.prevision_simulada(
        db, id_repuesto, consumo_desde, consumo_hasta
    )


@router.get(
    "/previsiones/{id_repuesto}",
    response_model=list[PrevisionOut],
    status_code=200,
    summary="Devuelve las previsiones de un repuesto (guardadas, o recalculadas si se pasa un rango de consumo).",
)
def mostrar_previsiones(
    id_repuesto: int,
    db: DB,
    consumo_desde: date | None = None,
    consumo_hasta: date | None = None,
):
    return _filas_prevision(db, id_repuesto, consumo_desde, consumo_hasta)


@router.get(
    "/previsiones/{id_repuesto}/cobertura",
    response_model=CoberturaOut,
    status_code=200,
    summary="Stock actual, stock objetivo a 3/6/12 meses y fecha estimada de agotamiento.",
)
def mostrar_cobertura(
    id_repuesto: int,
    db: DB,
    consumo_desde: date | None = None,
    consumo_hasta: date | None = None,
):
    filas = _filas_prevision(db, id_repuesto, consumo_desde, consumo_hasta)
    return calculo_prevision.cobertura(db, id_repuesto, filas)


## -------------------------------------------------------------------------


@router.get(
    "/duracion-repuestos/{id_repuesto}",
    response_model=DuracionRepuestosOut,
    status_code=200,
    summary="Devuelve la duracion de un repuesto.",
)
def histograma(
    id_repuesto: int,
    db: DB,
    patentado_desde: date | None = None,
    patentado_hasta: date | None = None,
):
    return repo_duraciones.listar_por_repuesto(
        db, id_repuesto, patentado_desde, patentado_hasta
    )
