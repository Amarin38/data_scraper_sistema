from datetime import date
from time import monotonic
from typing import Annotated

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select

from legacy_api.auth import REQ_ALL
from legacy_api.deps import DB
from legacy_api.schemas.inicio_schema import (
    DatosRapidosOut,
    RepuestoBusquedaOut,
    RepuestoFijadoOut,
)
from legacy_api.v1.endpoints.usuario_preferencia import requiere_panel
from shared.core.constants import REPUESTOS_IMPORTACION, desde_1, hoy_mes
from shared.core.paneles import paneles_permitidos
from shared.db.models.estadisticas.prevision_model import PrevisionModel
from shared.db.models.existencia_stock_model import ExistenciaStockModel
from shared.db.models.ficha_stock_model import FichaStockModel
from shared.db.models.repuesto_model import RepuestoModel
from shared.db.views.consumo_mensual import t as cm
from shared.db.views.gasto_mensual import t as gm
from shared.repositories.repuesto_fijado_repository import RepuestoFijadoRepository

router = APIRouter(prefix="/inicio", tags=["inicio"])

ficha = FichaStockModel
repuestos = RepuestoModel
existencias = ExistenciaStockModel
prevision = PrevisionModel

_cache = {"t": 0.0, "datos": None}
TTL = 600

# a qué panel del front pertenece cada clave de /datos-rapidos (para filtrar por permiso)
_PANEL_DE_CLAVE = {
    "mayor_stock": "gasto",
    "mayor_gasto": "gasto",
    "crit_sin_exist": "criticos",
    "importar": "importar",
    "importar_6": "importar",
    "importar_12": "importar",
}


codigo_col = func.concat(repuestos.Familia, ".", repuestos.Articulo).label("Codigo")
consumo = func.sum(-ficha.Cantidad).label("Cantidad")


@router.get(
    "/datos-rapidos",
    response_model=DatosRapidosOut,
    status_code=200,
    summary="Devuelve los datos rápidos del sistema",
)
def get_datos_rapidos(db: DB, user: REQ_ALL):
    if _cache["datos"] is None or monotonic() - _cache["t"] > TTL:  # type: ignore
        _cache["datos"] = get_all(db)
        _cache["t"] = monotonic()
    # la caché es global; cada usuario recibe vacíos los paneles que su rol no puede ver
    ok = paneles_permitidos(user.TipoUser)
    return {
        clave: (valor if _PANEL_DE_CLAVE[clave] in ok else [])
        for clave, valor in _cache["datos"].items()  # type: ignore
    }


def get_all(db: DB):
    return {
        "mayor_stock": get_mayor_stock(db),
        "mayor_gasto": get_mayor_gasto(db),
        "crit_sin_exist": get_crit_sin_exist(db),
        "importar": get_importaciones(db, 3),
        "importar_6": get_importaciones(db, 6),
        "importar_12": get_importaciones(db, 12),
    }


def get_mayor_stock(db: DB):
    stmt = (
        select(
            cm.c.IDRepuesto,
            codigo_col,
            repuestos.Descripcion,
            cm.c.consumo.label("Cantidad"),
        )
        .join(repuestos, repuestos.IDRepuesto == cm.c.IDRepuesto)
        .where(cm.c.mes == desde_1)
        .order_by(cm.c.consumo.desc())
        .limit(10)
    )

    return [dict(r) for r in db.execute(stmt).mappings().all()]


def get_mayor_gasto(db: DB):
    stmt = (
        select(
            gm.c.IDRepuesto,
            codigo_col,
            repuestos.Descripcion,
            gm.c.gasto.label("Gasto"),
        )
        .join(repuestos, repuestos.IDRepuesto == gm.c.IDRepuesto)
        .where(gm.c.mes == desde_1)
        .order_by(gm.c.gasto.desc())
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


def get_importaciones(db: DB, meses: int = 3):
    ini = hoy_mes
    fin = ini + relativedelta(months=meses)
    prevista = (
        select(
            prevision.IDRepuesto,
            func.sum(prevision.Cantidad).label("Prevision"),
        )
        .where(
            prevision.Periodo >= ini,
            prevision.Periodo < fin,
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


@router.get(
    "/fijados",
    response_model=list[RepuestoFijadoOut],
    dependencies=[Depends(requiere_panel("fijados"))],
)
def listar_fijados(
    db: DB,
    user: REQ_ALL,
    desde: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    hasta: Annotated[int | None, Query(ge=2000, le=2100)] = None,
):
    anio = date.today().year
    desde = anio - 2 if desde is None else desde
    hasta = anio - 1 if hasta is None else hasta
    if desde > hasta:
        raise HTTPException(422, "desde no puede ser mayor que hasta")
    return RepuestoFijadoRepository().listar(db, user.IDUsuario, desde, hasta)


@router.get(
    "/fijados/buscar",
    response_model=list[RepuestoBusquedaOut],
    dependencies=[Depends(requiere_panel("fijados"))],
)
def buscar_para_fijar(
    db: DB,
    _: REQ_ALL,
    q: Annotated[str, Query(min_length=2, max_length=60)],
):
    return RepuestoFijadoRepository().buscar(db, q.strip())


@router.put(
    "/fijados/{id_repuesto}",
    status_code=204,
    dependencies=[Depends(requiere_panel("fijados"))],
)
def fijar(id_repuesto: int, db: DB, user: REQ_ALL):
    if not RepuestoFijadoRepository().fijar(db, user.IDUsuario, id_repuesto):
        raise HTTPException(404, "Repuesto inexistente")


@router.delete(
    "/fijados/{id_repuesto}",
    status_code=204,
    dependencies=[Depends(requiere_panel("fijados"))],
)
def desfijar(id_repuesto: int, db: DB, user: REQ_ALL):
    RepuestoFijadoRepository().desfijar(db, user.IDUsuario, id_repuesto)
