from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.core.enums import TipoCombustibleEnum


class ParqueMovilPatch(BaseModel): ...


class ParqueMovilHistorialPatch(BaseModel): ...


class ParqueMovilOut(BaseModel):
    IDParqueMovil: int
    IDAseguradora: int

    Linea: int
    Interno: int
    Estado: str
    KM: Decimal | None
    Dominio: str | None
    FechaPatentado: date | None

    Asientos: int
    TipoCombustible: TipoCombustibleEnum | None

    Carroceria: str | None

    IDChasis: int | None
    ChasisCod: str | None
    ChasisAño: int | None

    IDMotor: int | None
    MotorCod: str | None

    model_config = ConfigDict(from_attributes=True)


class ParqueMovilHistorialOut(BaseModel):
    IDParqueMovilHistorial: int
    FechaHistorial: date
    IDAseguradora: int

    Linea: int
    Interno: int
    Estado: str
    KM: Decimal | None
    Dominio: str | None
    FechaPatentado: date | None

    Asientos: int
    TipoCombustible: TipoCombustibleEnum | None

    Carroceria: str | None

    IDChasis: int | None
    ChasisCod: str | None
    ChasisAño: int | None

    IDMotor: int | None
    MotorCod: str | None

    model_config = ConfigDict(from_attributes=True)
