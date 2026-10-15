from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.core.enums import CabecerasEnum


class IndiceConsumoOut(BaseModel):
    IDRepuesto: int
    Familia: str
    Articulo: str
    Descripcion: str
    Deposito: CabecerasEnum
    Indice: Decimal
    IndiceGlobal: Decimal
    IndiceRelativo: Decimal
    FechaIndice: date

    model_config = ConfigDict(from_attributes=True)


class IndiceConsumoTablaOut(BaseModel):
    IDRepuesto: int
    Codigo: str
    Descripcion: str
    PeorCabecera: str
    MaxRelativo: Decimal
    CantRojas: int

    model_config = ConfigDict(from_attributes=True)


class PaginadoIndiceConsumoTablaOut(BaseModel):
    items: list[IndiceConsumoTablaOut]
    next_cursor: dict | None
