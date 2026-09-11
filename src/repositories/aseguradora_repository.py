from src.db.models.aseguradora_model import AseguradoraModel
from src.repositories.base_repository import BaseRepository


class AseguradoraRepository(BaseRepository[AseguradoraModel]):
    model = AseguradoraModel
    pk_name = AseguradoraModel.IDAseguradora
