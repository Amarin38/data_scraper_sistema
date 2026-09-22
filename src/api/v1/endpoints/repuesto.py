from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError

from src.api.deps import DB
from src.api.schemas.pagina import Pagina
from src.api.schemas.repuesto_schema import RepuestoCreate, RepuestoOut, RepuestoPatch
from src.api.utils import Cursor, Limite, no_existe_repuesto, ya_existe_repuesto
from src.db.models.repuesto_model import RepuestoModel
from src.repositories.repuesto_repository import RepuestoRepository

router = APIRouter(prefix="/repuestos", tags=["repuestos"])
repo = RepuestoRepository()


@router.get(
    "/",
    response_model=Pagina[RepuestoOut],
    status_code=200,
    summary="Lista todos los repuestos.",
)
def listar(db: DB, limit: Limite = 150, cursor: Cursor = 0):
    items, next_cursor = repo.listar_pagina(db, limit=limit, cursor=cursor)

    return {"items": items, "next_cursor": next_cursor}


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
