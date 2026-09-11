from src.db.models.existencia_stock_model import ExistenciaStockModel
from src.repositories.base_repository import BaseRepository


class ExistenciaStockRepository(BaseRepository[ExistenciaStockModel]):
    model = ExistenciaStockModel
    pk_name = ExistenciaStockModel.IDExistencia
