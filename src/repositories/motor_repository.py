from repositories.base_repository import BaseRepository
from src.db.models.motor_marca_model import MotorMarcaModel
from src.db.models.motor_modelo_model import MotorModeloModel


class MotorModeloRepository(BaseRepository[MotorModeloModel]):
    model = MotorModeloModel


class MotorMarcaRepository(BaseRepository[MotorMarcaModel]):
    model = MotorMarcaModel
