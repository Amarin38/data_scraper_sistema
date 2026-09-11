from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models.repuesto_model import RepuestoModel
from src.repositories.base_repository import BaseRepository


class RepuestoRepository(BaseRepository[RepuestoModel]):
    model = RepuestoModel

    def get_by_codigo(self, db: Session, familia: str, articulo: str):
        stmt = select(self.model).where(
            self.model.Familia == familia, self.model.Articulo == articulo
        )

        return db.scalars(stmt).first()
