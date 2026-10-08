from src.db.models.estadisticas.duracion_repuestos_model import DuracionRepuestosModel
from src.repositories.base_repository import BaseRepository


class DuracionRepuestosRepository(BaseRepository[DuracionRepuestosModel]):
    model = DuracionRepuestosModel
