import time

import pandas as pd
from sqlalchemy import delete
from sqlalchemy.orm import Session

from core.enums import CabecerasEnum
from src.db.models.ficha_stock_model import FichaStockModel
from src.repositories.base_repository import BaseRepository


class FichaStockRepository(BaseRepository[FichaStockModel]):
    model = FichaStockModel
    pk_name = FichaStockModel.IDFichaStock  # type: ignore

    def load_df_with_overwrite_cabecera(self, db: Session, df: pd.DataFrame, cabecera: CabecerasEnum) -> int:
        t0 = time.perf_counter()
        
        try:
            borradas = self.delete_by_cabecera(db, cabecera)
            insertadas = self.load_df(db, df, commit=False)
            db.commit()
            print(f"[{self.table_name}] -{borradas} +{insertadas} en {time.perf_counter() - t0:.1f}s")
            return insertadas
        except Exception:
            db.rollback()
            raise   

    def delete_by_cabecera(self, db: Session, cabecera: CabecerasEnum) -> int:
        stmt = delete(self.model).where(self.model.Deposito == cabecera)
        return db.execute(stmt).rowcount # type: ignore