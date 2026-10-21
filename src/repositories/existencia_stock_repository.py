from datetime import date
from decimal import Decimal

from sqlalchemy import Select, func, select

from src.db.models.existencia_stock_model import ExistenciaStockModel
from src.db.models.repuesto_model import RepuestoModel
from src.repositories.base_repository import BaseRepository


class ExistenciaStockRepository(BaseRepository[ExistenciaStockModel]):
    model = ExistenciaStockModel

    def listar_existencias(self, db, descripcion, codigo, conjunto, limit, page):
        type SelectType = Select[tuple[int, str, str, Decimal, date]]

        repuestos = RepuestoModel

        codigo_col = func.concat(repuestos.Familia, ".", repuestos.Articulo).label(
            "Codigo"
        )

        stmt: SelectType = select(
            self.model.IDExistencia,
            codigo_col,
            repuestos.Descripcion,
            func.coalesce(self.model.Stock, 0).label("Stock"),
            self.model.FechaExistencia,
        ).join(repuestos, repuestos.IDRepuesto == self.model.IDRepuesto)

        if conjunto:
            stmt: SelectType = stmt.where(repuestos.Conjunto == conjunto)

        if descripcion:
            for palabra in descripcion.split():
                stmt: SelectType = stmt.where(
                    repuestos.Descripcion.icontains(palabra, autoescape=True)
                )
        if codigo:
            stmt: SelectType = stmt.where(codigo_col.ilike(f"%{codigo}%"))

        return self._paginar_offset(
            db,
            stmt,
            limit,
            page,
            order_cols=(repuestos.Descripcion.asc(), repuestos.IDRepuesto.asc()),
        )
