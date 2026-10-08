import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models.interno_vigencia_model import InternoVigenciaModel
from src.db.models.parque_movil_historial_model import ParqueMovilHistorialModel
from src.db.models.parque_movil_model import ParqueMovilModel
from src.repositories.base_repository import BaseRepository


class ParqueMovilRepository(BaseRepository[ParqueMovilModel]):
    model = ParqueMovilModel


class ParqueMovilHistorialRepository(BaseRepository[ParqueMovilHistorialModel]):
    model = ParqueMovilHistorialModel

    def listar_internos_patentes(self, db: Session) -> pd.DataFrame:
        stmt = select(
            self.model.FechaHistorial,
            self.model.Interno,
            self.model.Dominio,
            self.model.FechaPatentado,
        ).order_by(self.model.FechaHistorial, self.model.Interno, self.model.Dominio)

        return pd.read_sql(stmt, db.bind)  # type: ignore


class InternoVigenciaRepository(BaseRepository[InternoVigenciaModel]):
    model = InternoVigenciaModel
