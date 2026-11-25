from shared.db.models.chasis_marca_model import ChasisMarcaModel
from shared.db.models.chasis_modelo_model import ChasisModeloModel
from shared.repositories.base_repository import BaseRepository


class ChasisMarcaRepository(BaseRepository[ChasisMarcaModel]):
    model = ChasisMarcaModel


class ChasisModeloRepository(BaseRepository[ChasisModeloModel]):
    model = ChasisModeloModel
