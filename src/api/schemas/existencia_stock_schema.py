from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.core.enums import UnidadEnum


class ExistenciaStockCreate(BaseModel):
    pass


class ExistenciaStockPatch(BaseModel):
    Stock: Decimal


class ExistenciaStockOut(BaseModel):
    IDExistencia: int
    IDRepuesto: int
    Unidad: UnidadEnum
    Stock: Decimal
    FechaExistencia: date
    Cabecera: str

    model_config = ConfigDict(from_attributes=True)
