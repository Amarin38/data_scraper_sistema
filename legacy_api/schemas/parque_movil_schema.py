from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.core.enums import TipoCombustibleEnum


class ParqueMovilHistorialOut(BaseModel):
    IDParqueMovilHistorial: int
    FechaHistorial: date
    Linea: int | None
    Interno: int | None
    Dominio: str | None
    FechaPatentado: date | None
    KM: Decimal | None

    Asientos: int | None
    TipoCombustible: TipoCombustibleEnum | None

    Carroceria: str | None

    ChasisCod: str | None
    ChasisMarca: str | None
    ChasisModelo: str | None
    ChasisAño: int | None

    MotorCod: str | None
    MotorMarca: str | None
    MotorModelo: str | None

    model_config = ConfigDict(from_attributes=True)


class ParqueMovilHistorialPaginadoOut(BaseModel):
    items: list[ParqueMovilHistorialOut]
    next_cursor: dict | None
