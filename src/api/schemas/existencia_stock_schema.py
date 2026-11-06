from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ExistenciaStockOut(BaseModel):
    IDExistencia: int
    Codigo: str
    Descripcion: str
    Stock: Decimal
    FechaExistencia: date
    Minimo: Decimal | None = None
    Maximo: Decimal | None = None
    Reponer: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class ExistenciaStockOffsetOut(BaseModel):
    items: list[ExistenciaStockOut]
    total: int
