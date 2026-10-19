from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError

from src.api.deps import DB
from src.api.schemas.repuesto_schema import (
    RepuestoCreate,
    RepuestoOut,
    RepuestoPaginadoOut,
    RepuestoPatch,
)
from src.api.utils import Limite, no_existe_repuesto, ya_existe_repuesto
from src.db.models.repuesto_model import RepuestoModel
from src.repositories.repuesto_repository import RepuestoRepository

router = APIRouter(prefix="/repuestos", tags=["repuestos"])
repo = RepuestoRepository()


@router.get(
    "",
    response_model=RepuestoPaginadoOut,
    status_code=200,
    summary="Lista todos los repuestos.",
)
def listar(
    db: DB,
    conjunto: str | None = None,
    descripcion: str | None = None,
    codigo: str | None = None,
    critico: bool = False,
    limit: Limite = 50,
    cursor_valor: str | None = None,
    cursor_id: int | None = None,
):
    return repo.get_repuestos(
        db, conjunto, descripcion, codigo, critico, limit, cursor_valor, cursor_id
    )


@router.get(
    "/conjuntos",
    response_model=list[str],
    status_code=200,
    summary="Devuelve todos los conjuntos de los repuestos.",
)
def get_conjuntos(db: DB):
    return repo.get_conjuntos(db)


@router.post(
    "/",
    response_model=RepuestoOut,
    status_code=201,
    summary="Guarda un repuesto nuevo.",
)
def guardar(payload: RepuestoCreate, db: DB):
    try:
        obj = repo.add(db, RepuestoModel(**payload.model_dump()))
    except SQLAlchemyError:
        raise ya_existe_repuesto from None

    db.commit()
    db.refresh(obj)
    return obj


@router.patch(
    "/{id_repuesto}",
    response_model=RepuestoOut,
    status_code=200,
    summary="Modifica el nombre de un repuesto, dado su id.",
)
def cambiar_nombre(id_repuesto: int, payload: RepuestoPatch, db: DB):
    obj = repo.get_by_id(db, id_repuesto)

    if obj is None:
        raise no_existe_repuesto

    obj.Descripcion = payload.Descripcion

    db.commit()
    db.refresh(obj)

    return obj


@router.delete(
    "/{id_repuesto}",
    status_code=204,
    summary="Elimina un repuesto dado su id.",
)
def eliminar_repuesto(id_repuesto: int, db: DB):
    obj = repo.get_by_id(db, id_repuesto)

    if obj is None:
        raise no_existe_repuesto

    repo.delete_by_obj(db, obj)
    db.commit()
