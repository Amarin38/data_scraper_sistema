from sqlalchemy import func, select

from src.db.models.existencia_stock_model import ExistenciaStockModel
from src.db.models.repuesto_model import RepuestoModel, codigo_expr
from src.repositories.base_repository import BaseRepository


class ExistenciaStockRepository(BaseRepository[ExistenciaStockModel]):
    model = ExistenciaStockModel
    codigo_col = codigo_expr()

    def _select_base(self):
        return select(
            self.model.IDExistencia,
            self.codigo_col.label("Codigo"),
            RepuestoModel.Descripcion,
            func.coalesce(self.model.Stock, 0).label("Stock"),
            self.model.FechaExistencia,
        ).join(RepuestoModel, RepuestoModel.IDRepuesto == self.model.IDRepuesto)

    def _filtrar(self, stmt, conjunto, descripcion, codigo):
        if conjunto:
            stmt = stmt.where(RepuestoModel.Conjunto == conjunto)

        if descripcion:
            for palabra in descripcion.split():
                stmt = stmt.where(
                    RepuestoModel.Descripcion.icontains(palabra, autoescape=True)
                )
        if codigo:
            stmt = stmt.where(self.codigo_col.ilike(f"%{codigo}%"))

        sin_filtros = not (conjunto or descripcion or codigo)
        total_stmt = (
            select(func.count()).select_from(self.model) if sin_filtros else None
        )

        return stmt, total_stmt

    def get_existencias(
        self,
        db,
        descripcion,
        codigo,
        conjunto,
        limit,
        page,
    ):
        stmt, total_stmt = self._filtrar(
            self._select_base(), conjunto, descripcion, codigo
        )

        return self._paginar_offset(
            db,
            stmt,
            limit,
            page,
            order_cols=(
                RepuestoModel.Descripcion.asc(),
                RepuestoModel.IDRepuesto.asc(),
            ),
            total_stmt=total_stmt,
        )

    def stmt_exportar(self, conjunto, descripcion, codigo):
        stmt, _ = self._filtrar(self._select_base(), conjunto, descripcion, codigo)

        return stmt.order_by(
            self.codigo_col.desc(),
            self.model.IDExistencia.asc(),
        )
