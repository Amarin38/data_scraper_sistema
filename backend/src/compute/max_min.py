from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy import delete, func, insert, select
from sqlalchemy.orm import Session

from src.core.enums import TipoMovEnum
from src.db.models.ficha_stock_model import FichaStockModel
from src.db.models.maximos_minimos_model import MaximosMinimosModel

ficha = FichaStockModel
MESES = 6


def compute_max_min(db: Session):
    hoy_mes = date.today().replace(day=1)
    desde = hoy_mes - relativedelta(months=MESES)
    mes = func.date_trunc("month", ficha.FechaMov)

    salidas = (
        select(
            ficha.IDRepuesto,
            ficha.Deposito,
            mes.label("Mes"),
            func.sum(func.abs(ficha.Cantidad)).label("Consumo"),
        )
        .where(
            ficha.TipoMov == TipoMovEnum.SALIDA,
            ficha.FechaMov >= desde,
            ficha.FechaMov < hoy_mes,
        )
        .group_by(ficha.IDRepuesto, ficha.Deposito, mes)
    ).cte("salidas")

    s = salidas.c

    demanda = select(
        s.IDRepuesto,
        s.Deposito,
        (func.sum(s.Consumo) / float(MESES)).label("DemandaMensual"),
        func.count().label("MesesConDatos"),
        func.current_date().label("FechaCalculo"),
    ).group_by(s.IDRepuesto, s.Deposito)

    cols = [
        "IDRepuesto",
        "Deposito",
        "DemandaMensual",
        "MesesConDatos",
        "FechaCalculo",
    ]

    db.execute(delete(MaximosMinimosModel))
    return db.execute(  # type: ignore
        insert(MaximosMinimosModel.__table__).from_select(
            cols,
            demanda,
        )
    ).rowcount
