from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ExistenciaStockOut(BaseModel):
    IDRepuesto: int
    IDExistencia: int | None = None
    Codigo: str
    Descripcion: str
    Condicion: str | None = None
    Conjunto: str | None = None
    Critico: bool = False
    Stock: Decimal
    FechaExistencia: date | None = None
    Minimo: Decimal | None = None
    Maximo: Decimal | None = None
    Reponer: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class ExistenciaStockOffsetOut(BaseModel):
    items: list[ExistenciaStockOut]
    total: int
