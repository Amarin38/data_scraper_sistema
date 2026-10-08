from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models.repuesto_model import RepuestoModel
from src.db.models.repuesto_unidades_model import RepuestoUnidadesModel
from src.repositories.base_repository import BaseRepository


class RepuestoRepository(BaseRepository[RepuestoModel]):
    model = RepuestoModel

    def get_criticos(self, db: Session) -> set[int]:
        stmt = select(self.model.IDRepuesto).where(self.model.Critico.is_(True))
        return set(db.execute(stmt).scalars())


class RepuestoUnidadesRepository(BaseRepository[RepuestoUnidadesModel]):
    model = RepuestoUnidadesModel
