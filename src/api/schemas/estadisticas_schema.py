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


class PrevisionOut(BaseModel):
    IDRepuesto: int
    Mes: str
    Cantidad: Decimal
    Tipo: str

    model_config = ConfigDict(from_attributes=True)


class DuracionRepuestosOut(BaseModel):
    IDRepuesto: int

    model_config = ConfigDict(from_attributes=True)
