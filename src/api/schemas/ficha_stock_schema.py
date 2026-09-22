from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.core.enums import CabecerasEnum, TipoMovEnum


class FichaStockOut(BaseModel):
    IDFichaStock: int
    IDRepuesto: int
    FechaMov: date
    Deposito: CabecerasEnum
    TipoMov: TipoMovEnum
    Cantidad: Decimal | None
    PrecioUnitario: Decimal | None
    Usuario: str | None
    DepositoTransfer: int | None

    model_config = ConfigDict(from_attributes=True)
