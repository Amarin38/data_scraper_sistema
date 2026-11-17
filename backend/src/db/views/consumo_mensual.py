from sqlalchemy import Date, cast, column, func, select, table

from src.core.enums import TipoMovEnum
from src.db.models.ficha_stock_model import FichaStockModel as ficha
from src.db.views._ddl import CreateMatView

NOMBRE = "consumo_mensual"

_mes = cast(func.date_trunc("month", ficha.FechaMov), Date).label("mes")
_consumo = (-func.sum(ficha.Cantidad)).label("consumo")

SELECT = (
    select(ficha.IDRepuesto, _mes, _consumo)
    .where(ficha.TipoMov == TipoMovEnum.SALIDA)
    .group_by(ficha.IDRepuesto, _mes)
)

CREAR = [
    CreateMatView(NOMBRE, SELECT),
    f'CREATE UNIQUE INDEX IF NOT EXISTS ux_{NOMBRE} ON {NOMBRE} ("IDRepuesto", mes)',
]

t = table(NOMBRE, column("IDRepuesto"), column("mes"), column("consumo"))
