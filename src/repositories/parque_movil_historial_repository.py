from src.db.models.parque_movil_historial_model import ParqueMovilHistorialModel
from src.repositories.base_repository import BaseRepository


class ParqueMovilHistorialRepository(BaseRepository[ParqueMovilHistorialModel]):
    model = ParqueMovilHistorialModel
