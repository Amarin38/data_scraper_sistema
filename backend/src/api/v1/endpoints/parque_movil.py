from datetime import date

from fastapi import APIRouter
from sqlalchemy import select

from src.api.deps import DB
from src.api.schemas.parque_movil_schema import (
    ParqueMovilHistorialOut,
    ParqueMovilHistorialPaginadoOut,
)
from src.api.utils import Limite
from src.core.enums import FormatoEnum
from src.core.exports import exportacion, iterar_filas, limpiar_nombre
from src.db.models.chasis_marca_model import ChasisMarcaModel
from src.db.models.chasis_modelo_model import ChasisModeloModel
from src.db.models.motor_marca_model import MotorMarcaModel
from src.db.models.motor_modelo_model import MotorModeloModel
from src.db.views.carrocerias import t as carrocerias
from src.repositories.parque_movil_repository import (
    ParqueMovilHistorialRepository,
)

router = APIRouter(prefix="/parque-movil", tags=["parque-movil"])
repo_historial = ParqueMovilHistorialRepository()
COLUMNAS_EXPORT = [
    c for c in ParqueMovilHistorialOut.model_fields if c != "IDParqueMovilHistorial"
]


@router.get(
    "/historiales",
    response_model=ParqueMovilHistorialPaginadoOut,
    status_code=200,
    summary="Muestra el historial del parque movil",
)
def mostrar_parque_historial(
    db: DB,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    linea: int | None = None,
    interno: int | None = None,
    dominio: str | None = None,
    carroceria: str | None = None,
    chasis_marca: str | None = None,
    chasis_modelo: str | None = None,
    motor_marca: str | None = None,
    motor_modelo: str | None = None,
    limit: Limite = 50,
    cursor_valor: date | None = None,
    cursor_id: int | None = None,
):
    return repo_historial.get_historial(
        db,
        fecha_desde,
        fecha_hasta,
        linea,
        interno,
        dominio,
        carroceria,
        chasis_marca,
        chasis_modelo,
        motor_marca,
        motor_modelo,
        limit,
        cursor_valor,
        cursor_id,
    )


@router.get("/exportar")
def exportar_parque(
    formato: FormatoEnum = FormatoEnum.CSV,
    nombre: str | None = None,
    validar: bool | None = False,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    linea: int | None = None,
    interno: int | None = None,
    dominio: str | None = None,
    carroceria: str | None = None,
    chasis_marca: str | None = None,
    chasis_modelo: str | None = None,
    motor_marca: str | None = None,
    motor_modelo: str | None = None,
):
    stmt = repo_historial.stmt_exportar(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        linea=linea,
        interno=interno,
        dominio=dominio,
        carroceria=carroceria,
        chasis_marca=chasis_marca,
        chasis_modelo=chasis_modelo,
        motor_marca=motor_marca,
        motor_modelo=motor_modelo,
    )

    return exportacion(
        stmt,
        COLUMNAS_EXPORT,
        formato,
        limpiar_nombre(nombre) or "parque_movil",
        validar=validar,
    )


@router.get(
    "/carrocerias",
    response_model=list[str],
    status_code=200,
    summary="Muestra el historial del parque movil",
)
def get_carrocerias(db: DB):
    stmt = select(carrocerias.c.Carroceria).order_by(carrocerias.c.Carroceria)
    return list(db.execute(stmt).scalars().all())


@router.get(
    "/chasis-marcas",
    response_model=list[str],
    status_code=200,
    summary="Muestra el historial del parque movil",
)
def get_chasis_marcas(db: DB):
    return repo_historial.get_distinct_by_col(db, ChasisMarcaModel.ChasisMarca)


@router.get(
    "/chasis-modelos",
    response_model=list[str],
    status_code=200,
    summary="Muestra el historial del parque movil",
)
def get_chasis_modelos(db: DB):
    return repo_historial.get_distinct_by_col(db, ChasisModeloModel.ChasisModelo)


@router.get(
    "/motor-marcas",
    response_model=list[str],
    status_code=200,
    summary="Muestra el historial del parque movil",
)
def get_motor_marcas(db: DB):
    return repo_historial.get_distinct_by_col(db, MotorMarcaModel.MotorMarca)


@router.get(
    "/motor-modelos",
    response_model=list[str],
    status_code=200,
    summary="Muestra el historial del parque movil",
)
def get_motor_modelos(db: DB):
    return repo_historial.get_distinct_by_col(db, MotorModeloModel.MotorModelo)
