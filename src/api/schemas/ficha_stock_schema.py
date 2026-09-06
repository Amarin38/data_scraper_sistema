from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class FichaStockBase(BaseModel):
    Familia: str
    Articulo: str
    FechaMov: date
    Deposito: int
    TipoMov: str
    Cantidad: Decimal
    PrecioUnitario: Decimal
    Usuario: str
    DepositoTransfer: int


class FichaStockCreate(FichaStockBase):
    pass


class FichaStockOut(FichaStockBase):
    id: int
    creado_en: date

    model_config = {"from_attributes": True}
