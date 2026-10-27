from datetime import date
from time import monotonic

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter
from sqlalchemy import func, select

from src.api.deps import DB
from src.api.schemas.inicio_schema import DatosRapidosOut
from src.core.constants import DICT_TIPO_DURACION, REPUESTOS_IMPORTACION
from src.core.enums import TipoDuracionEnum
from src.db.models.estadisticas.prevision_model import PrevisionModel
from src.db.models.existencia_stock_model import ExistenciaStockModel
from src.db.models.ficha_stock_model import FichaStockModel
from src.db.models.repuesto_model import RepuestoModel
from src.db.views.consumo_mensual import t as consumo_mensual

router = APIRouter(prefix="/inicio", tags=["inicio"])

ficha = FichaStockModel
repuestos = RepuestoModel
existencias = ExistenciaStockModel
prevision = PrevisionModel

_cache = {"t": 0.0, "datos": None}
TTL = 600


codigo_col = func.concat(repuestos.Familia, ".", repuestos.Articulo).label("Codigo")
consumo = func.sum(-ficha.Cantidad).label("Cantidad")
mes_actual = date.today().replace(day=1)
un_mes = relativedelta(months=1)
cuatro_meses = relativedelta(months=4)


@router.get(
    "/datos-rapidos",
    response_model=DatosRapidosOut,
    status_code=200,
    summary="Devuelve los datos rápidos del sistema",
)
def get_datos_rapidos(db: DB):
    if _cache["datos"] is None or monotonic() - _cache["t"] > TTL:  # type: ignore
        _cache["datos"] = get_all(db)
        _cache["t"] = monotonic()
    return _cache["datos"]


def get_all(db: DB):
    return {
        "mayor_stock": get_mayor_stock(db),
        "crit_sin_exist": get_crit_sin_exist(db),
        "importar": get_importaciones(db),
    }


def get_mayor_stock(db: DB):
    stmt = (
        select(
            consumo_mensual.c.IDRepuesto,
            codigo_col,
            repuestos.Descripcion,
            consumo_mensual.c.consumo.label("Cantidad"),
        )
        .join(repuestos, repuestos.IDRepuesto == consumo_mensual.c.IDRepuesto)
        .where(consumo_mensual.c.mes == mes_actual - un_mes)
        .order_by(consumo_mensual.c.consumo.desc())
        .limit(10)
    )

    return [dict(r) for r in db.execute(stmt).mappings().all()]


def get_crit_sin_exist(db: DB):
    stmt = (
        select(
            existencias.IDRepuesto,
            codigo_col,
            repuestos.Descripcion,
            existencias.Stock,
        )
        .where(func.coalesce(existencias.Stock, 0) == 0, repuestos.Critico)
        .join(repuestos, repuestos.IDRepuesto == existencias.IDRepuesto)
        .order_by(repuestos.Descripcion.desc())
    )

    return [dict(r) for r in db.execute(stmt).mappings().all()]


def get_importaciones(db: DB):
    prevista = (
        select(
            prevision.IDRepuesto,
            func.sum(prevision.Cantidad).label("Prevision"),
        )
        .where(
            prevision.Periodo >= mes_actual + un_mes,
            prevision.Periodo < mes_actual + cuatro_meses,
        )
        .group_by(prevision.IDRepuesto)
        .subquery()
    )
    stock = func.coalesce(existencias.Stock, 0)
    falta = prevista.c.Prevision - stock

    stmt = (
        select(
            repuestos.IDRepuesto,
            codigo_col,
            repuestos.Descripcion,
            prevista.c.Prevision,
            stock.label("Stock"),
            falta.label("Faltante"),
        )
        .join(prevista, prevista.c.IDRepuesto == repuestos.IDRepuesto)
        .outerjoin(existencias, existencias.IDRepuesto == repuestos.IDRepuesto)
        .where(
            falta > 0,
            codigo_col.in_(REPUESTOS_IMPORTACION),
        )
        .order_by(falta.desc())
    )
    return [dict(r) for r in db.execute(stmt).mappings().all()]
