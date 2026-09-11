from src.db.models.parque_movil_historial_model import ParqueMovilHistorialModel
from src.db.models.parque_movil_model import ParqueMovilModel
from src.repositories.base_repository import BaseRepository


class ParqueMovilRepository(BaseRepository[ParqueMovilModel]):
    model = ParqueMovilModel
    pk_name = ParqueMovilModel.IDParqueMovil


class ParqueMovilHistorialRepository(BaseRepository[ParqueMovilHistorialModel]):
    model = ParqueMovilHistorialModel
    pk_name = ParqueMovilHistorialModel.IDParqueMovilHistorial
