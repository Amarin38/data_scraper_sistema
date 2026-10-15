from datetime import date

import pandas as pd
from sqlalchemy import Numeric, and_, cast, delete, func, insert, select
from sqlalchemy.orm import Session

from src.core.enums import CabecerasEnum, TipoMovEnum, TipoUsuarioEnum
from src.db.models.estadisticas.indice_consumo_model import IndiceConsumoModel
from src.db.models.ficha_stock_model import FichaStockModel

ficha = FichaStockModel


def ventana(session: Session, meses: int) -> tuple[date, date]:
    """Últimos `meses` meses completos hasta el último dato válido (excluye el mes final parcial)."""
    ultima = session.execute(
        select(func.max(ficha.FechaMov)).where(
            ficha.FechaMov <= date.today(), ficha.Deposito != CabecerasEnum.MEGABUS
        )
    ).scalar_one()
    fin = ultima.replace(day=1)
    desde = (pd.Timestamp(fin) - pd.DateOffset(months=meses)).date()
    return desde, fin


def compute_indice_consumo(session: Session, meses: int = 12) -> None:
    desde, fin = ventana(session, meses)
    mes = func.date_trunc("month", ficha.FechaMov)
    base = and_(
        ficha.Deposito != CabecerasEnum.MEGABUS,
        ficha.FechaMov >= desde,
        ficha.FechaMov < fin,
    )

    unidades = (
        select(
            ficha.IDRepuesto,
            ficha.Deposito,
            func.sum(func.abs(ficha.Cantidad)).label("Unidades"),
        )
        .where(base, ficha.TipoMov == TipoMovEnum.SALIDA)
        .group_by(ficha.IDRepuesto, ficha.Deposito)
        .cte("unidades")
    )

    meses_cab = (
        select(ficha.Deposito, func.count(mes.distinct()).label("Meses"))
        .where(base)
        .group_by(ficha.Deposito)
        .cte("meses_cab")
    )

    # 3. Flota promedio por cabecera: coche-meses / meses con datos
    coche_mes = (
        select(ficha.Deposito, ficha.Interno, mes.label("Mes"))
        .where(
            base, ficha.TipoUsuario == TipoUsuarioEnum.COCHE, ficha.Interno.is_not(None)
        )
        .distinct()
        .subquery()
    )

    coches = func.count() / cast(meses_cab.c.Meses, Numeric)

    cabecera = (
        select(
            meses_cab.c.Deposito,
            meses_cab.c.Meses,
            coches.label("Coches"),
        )
        .join(coche_mes, coche_mes.c.Deposito == meses_cab.c.Deposito)
        .group_by(meses_cab.c.Deposito, meses_cab.c.Meses)
        .cte("cabecera")
    )

    # 4. Índice anual por coche en cada cabecera
    anual = unidades.c.Unidades * 12 / cast(cabecera.c.Meses, Numeric)
    idx_cabecera = (
        select(
            unidades.c.IDRepuesto,
            unidades.c.Deposito,
            unidades.c.Unidades,
            cabecera.c.Coches,
            anual.label("UnidadesAnual"),
            (anual / cabecera.c.Coches).label("Indice"),
        )
        .join(cabecera, cabecera.c.Deposito == unidades.c.Deposito)
        .cte("idx_cabecera")
    )

    # 5. Índice global: consumo anual de todas las cabeceras / flota total
    flota_total = select(func.sum(cabecera.c.Coches)).scalar_subquery()
    indice_global = func.sum(idx_cabecera.c.UnidadesAnual) / flota_total

    glob = (
        select(
            idx_cabecera.c.IDRepuesto,
            indice_global.label("IndiceGlobal"),
        )
        .group_by(idx_cabecera.c.IDRepuesto)
        .cte("glob")
    )

    # 6. Resultado
    query_final = select(
        idx_cabecera.c.IDRepuesto,
        idx_cabecera.c.Deposito,
        idx_cabecera.c.Unidades,
        idx_cabecera.c.Coches,
        idx_cabecera.c.Indice,
        glob.c.IndiceGlobal,
        (idx_cabecera.c.Indice / glob.c.IndiceGlobal).label("IndiceRelativo"),
        func.current_date().label("FechaIndice"),
    ).join(glob, glob.c.IDRepuesto == idx_cabecera.c.IDRepuesto)

    session.execute(delete(IndiceConsumoModel))
    session.execute(
        insert(IndiceConsumoModel).from_select(
            [
                "IDRepuesto",
                "Deposito",
                "Unidades",
                "Coches",
                "Indice",
                "IndiceGlobal",
                "IndiceRelativo",
                "FechaIndice",
            ],
            query_final,
        )
    )
