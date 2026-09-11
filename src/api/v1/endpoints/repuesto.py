from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError

from db.models.repuesto_model import RepuestoModel
from src.api.deps import DB
from src.api.schemas.repuesto_schema import RepuestoCreate, RepuestoOut, RepuestoPatch
from src.repositories.repuesto_repository import RepuestoRepository

router = APIRouter(prefix="/repuestos", tags=["repuestos"])
repo = RepuestoRepository()

no_existe = HTTPException(404, "El repuesto no existe.")
ya_existe = HTTPException(405, "El repuesto ya existe.")

Limite = Annotated[int, Query(ge=1, le=1000, description="Filas por página")]
Cursor = Annotated[
    int, Query(ge=0, description="IDFichaStock de la última fila anterior")
]


@router.get(
    "/",
    response_model=list[RepuestoOut],
    status_code=200,
    summary="Lista todos los repuestos.",
)
def listar(db: DB, limit: Limite = 50, cursor: Cursor = 0):
    return repo.list(db, limit=limit, cursor=cursor)


@router.post(
    "/",
    response_model=RepuestoOut,
    status_code=201,
    summary="Guarda un repuesto nuevo.",
)
def guardar(db: DB, payload: RepuestoCreate):
    try:
        obj = repo.add(db, RepuestoModel(**payload.model_dump()))
    except SQLAlchemyError:
        raise ya_existe

    db.commit()
    db.refresh(obj)
    return obj


@router.patch(
    "/{familia}/{articulo}",
    response_model=RepuestoOut,
    status_code=200,
    summary="Modifica el nombre de un repuesto, dado su familia y articulo.",
)
def cambiar_nombre(db: DB, payload: RepuestoPatch, familia: str, articulo: str):
    obj = repo.get_by_codigo(db, familia=familia, articulo=articulo)

    if obj is None:
        raise no_existe

    obj.Descripcion = payload.Descripcion

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


@router.delete(
    "/{familia}/{articulo}", 
    status_code=204, 
    summary="Elimina un repuesto dado su familia y articulo."
)
def eliminar_repuesto(db: DB, familia: str, articulo: str):
    obj = repo.get_by_codigo(db, familia, articulo)

    if obj is None:
        raise no_existe

    repo.delete_by_id(db, obj)
    db.commit()
