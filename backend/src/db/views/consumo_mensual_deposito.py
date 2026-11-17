from sqlalchemy import Date, Text, cast, column, func, select, table

from src.core.enums import TipoMovEnum
from src.db.models.ficha_stock_model import FichaStockModel as ficha
from src.db.views._ddl import CreateMatView

NOMBRE = "consumo_mensual_deposito"

_deposito = cast(ficha.Deposito, Text).label("Deposito")
_mes = cast(func.date_trunc("month", ficha.FechaMov), Date).label("mes")
_consumo = (-func.sum(ficha.Cantidad)).label("consumo")

SELECT = (
    select(ficha.IDRepuesto, _deposito, _mes, _consumo)
    .where(ficha.TipoMov == TipoMovEnum.SALIDA, ficha.Deposito.is_not(None))
    .group_by(ficha.IDRepuesto, _deposito, _mes)
)

CREAR = [
    CreateMatView(NOMBRE, SELECT),
    f'CREATE UNIQUE INDEX IF NOT EXISTS ux_{NOMBRE} ON {NOMBRE} ("IDRepuesto", "Deposito", mes)',
    f'CREATE INDEX IF NOT EXISTS ix_{NOMBRE}_dep_mes ON {NOMBRE} ("Deposito", mes) INCLUDE ("IDRepuesto", consumo)',
]

t = table(
    NOMBRE,
    column("IDRepuesto"),
    column("Deposito"),
    column("mes"),
    column("consumo"),
)
