from venv import logger

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models.ficha_stock_model import FichaStockModel
from src.db.models.repuesto_model import RepuestoModel
from src.repositories.base_repository import BaseRepository


class FichaStockRepository(BaseRepository[FichaStockModel]):
    model = FichaStockModel

    
