from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FichaStockOut(BaseModel):
    IDFichaStock: int
    IDRepuesto: int
    Codigo: str
    Descripcion: str
    FechaMov: date
    Deposito: str
    TipoMov: str
    Cantidad: Decimal | None
    PrecioUnitario: Decimal | None
    Interno: int | None
    TipoUsuario: str | None
    DepositoTransfer: int | None

    model_config = ConfigDict(from_attributes=True)


class FichaStockPaginadoOut(BaseModel):
    items: list[FichaStockOut]
    next_cursor: dict | None
