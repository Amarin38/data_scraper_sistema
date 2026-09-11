from src.db.models.chasis_marca_model import ChasisMarcaModel
from src.db.models.chasis_modelo_model import ChasisModeloModel
from src.repositories.base_repository import BaseRepository


class ChasisMarcaRepository(BaseRepository[ChasisMarcaModel]):
    model = ChasisMarcaModel
    pk_name = ChasisMarcaModel.IDChasisMarca

class ChasisModeloRepository(BaseRepository[ChasisModeloModel]):
    model = ChasisModeloModel
    pk_name = ChasisModeloModel.IDChasisModelo
