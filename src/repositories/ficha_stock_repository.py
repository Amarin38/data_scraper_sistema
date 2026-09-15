import time

import pandas as pd
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.core.enums import CabecerasEnum
from src.db.models.ficha_stock_model import FichaStockModel
from src.repositories.base_repository import BaseRepository


class FichaStockRepository(BaseRepository[FichaStockModel]):
    model = FichaStockModel

    def delete_by_cabecera(self, db: Session, cabecera: CabecerasEnum) -> int:
        stmt = delete(self.model).where(self.model.Deposito == cabecera)
        return db.execute(stmt).rowcount  # type: ignore