from sqlalchemy import Date, cast, column, func, select, table

from shared.core.enums import TipoMovEnum
from shared.db.models.ficha_stock_model import FichaStockModel as ficha
from shared.db.models.repuesto_model import RepuestoModel
from shared.db.views._ddl import CreateMatView

NOMBRE = "gasto_mensual"

_mes = cast(func.date_trunc("month", ficha.FechaMov), Date).label("mes")
# costo = unidades que salieron × precio unitario (las salidas tienen Cantidad negativa)
_gasto = (-func.sum(ficha.Cantidad * func.coalesce(ficha.PrecioUnitario, 0))).label(
    "gasto"
)

SELECT = (
    select(ficha.IDRepuesto, _mes, _gasto)
    .where(
        ficha.TipoMov == TipoMovEnum.SALIDA,
        RepuestoModel.Conjunto.not_in(["SERVICIOS"]),
    )
    .join(RepuestoModel, RepuestoModel.IDRepuesto == ficha.IDRepuesto)
    .group_by(ficha.IDRepuesto, _mes)
)

CREAR = [
    CreateMatView(NOMBRE, SELECT),
    f'CREATE UNIQUE INDEX IF NOT EXISTS ux_{NOMBRE} ON {NOMBRE} ("IDRepuesto", mes)',
]

t = table(NOMBRE, column("IDRepuesto"), column("mes"), column("gasto"))
