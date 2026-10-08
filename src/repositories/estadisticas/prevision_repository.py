from src.db.models.estadisticas.prevision_model import PrevisionModel
from src.repositories.base_repository import BaseRepository


class PrevisionRepository(BaseRepository[PrevisionModel]):
    model = PrevisionModel
