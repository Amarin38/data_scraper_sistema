from src.db.models import (
    ConteoStockModel,
    DuracionRepuestosModel,
    IndiceConsumoModel,
    PrevisionModel,
)
from src.repositories.base_repository import BaseRepository


class DuracionRepuestosRepository(BaseRepository[DuracionRepuestosModel]):
    model = DuracionRepuestosModel


class PrevisionRepository(BaseRepository[PrevisionModel]):
    model = PrevisionModel


class IndiceConsumoRepository(BaseRepository[IndiceConsumoModel]):
    model = IndiceConsumoModel


class ConteoStockRepository(BaseRepository[ConteoStockModel]):
    model = ConteoStockModel
