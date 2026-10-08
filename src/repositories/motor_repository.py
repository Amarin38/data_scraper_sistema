from src.db.models.motor_marca_model import MotorMarcaModel
from src.db.models.motor_modelo_model import MotorModeloModel
from src.repositories.base_repository import BaseRepository


class MotorModeloRepository(BaseRepository[MotorModeloModel]):
    model = MotorModeloModel


class MotorMarcaRepository(BaseRepository[MotorMarcaModel]):
    model = MotorMarcaModel
