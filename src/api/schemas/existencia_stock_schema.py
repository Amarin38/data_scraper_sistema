from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ExistenciaStockBase(BaseModel):
    Familia: str
    Articulo: str
    Nombre: str
    Unidad: str
    Stock: Decimal
    FechaExistencia: date


class ExistenciaStockCreate(ExistenciaStockBase):
    pass


class ExistenciaStockOut(ExistenciaStockBase):
    id: int
    creado_en: date

    model_config = {"from_attributes": True}
