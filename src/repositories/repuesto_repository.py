from src.db.models.repuesto_model import RepuestoModel
from src.repositories.base_repository import BaseRepository


class RepuestoRepository(BaseRepository[RepuestoModel]):
    model = RepuestoModel
