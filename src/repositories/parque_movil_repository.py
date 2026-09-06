from src.db.models.parque_movil_model import ParqueMovilModel
from src.repositories.base_repository import BaseRepository


class ParqueMovilRepository(BaseRepository[ParqueMovilModel]):
    model = ParqueMovilModel
