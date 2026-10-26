from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CriticosSinExist(BaseModel):
    IDRepuesto: int
    Codigo: str
    Descripcion: str
    Stock: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ArtMayorStock(BaseModel):
    IDRepuesto: int
    Codigo: str
    Descripcion: str
    Cantidad: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class Importar(BaseModel):
    IDRepuesto: int
    Codigo: str
    Descripcion: str
    Prevision: Decimal | None = None
    Stock: Decimal | None = None
    Faltante: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class DatosRapidosOut(BaseModel):
    mayor_stock: list[ArtMayorStock]
    crit_sin_exist: list[CriticosSinExist]
    importar: list[Importar]
