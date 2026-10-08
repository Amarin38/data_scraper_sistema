from datetime import date

from sqlalchemy import Date, delete, func, select
from sqlalchemy.orm import Session

from src.core.enums import CabecerasEnum, TipoMovEnum
from src.db.models.ficha_stock_model import FichaStockModel
from src.repositories.base_repository import BaseRepository


class FichaStockRepository(BaseRepository[FichaStockModel]):
    model = FichaStockModel

    def delete_by_cabecera(self, db: Session, cabecera: CabecerasEnum) -> int:
        stmt = delete(self.model).where(self.model.Deposito == cabecera)
        return db.execute(stmt).rowcount  # type: ignore

    def get_serie_mensual(self, desde: date):
        mes = func.date_trunc("month", self.model.FechaMov).cast(Date).label("Periodo")
        return (
            select(
                self.model.IDRepuesto,
                mes,
                func.sum(func.abs(self.model.Cantidad)).label("Cantidad"),
            )
            .where(
                self.model.TipoMov == TipoMovEnum.SALIDA,
                self.model.Deposito == CabecerasEnum.MEGABUS,
                self.model.FechaMov >= desde,
                self.model.FechaMov < date.today().replace(day=1),
            )
            .group_by(self.model.IDRepuesto, mes)
        )
