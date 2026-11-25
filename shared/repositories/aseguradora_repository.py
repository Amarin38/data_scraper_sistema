from shared.db.models.aseguradora_model import AseguradoraModel
from shared.repositories.base_repository import BaseRepository


class AseguradoraRepository(BaseRepository[AseguradoraModel]):
    model = AseguradoraModel
