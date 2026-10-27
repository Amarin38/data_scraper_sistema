from sqlalchemy import Select, Text, cast, func, literal_column, select
from sqlalchemy.orm import Session

from src.db.models.repuesto_model import RepuestoModel
from src.db.models.repuesto_unidades_model import RepuestoUnidadesModel
from src.repositories.base_repository import BaseRepository


class RepuestoRepository(BaseRepository[RepuestoModel]):
    model = RepuestoModel

    def get_criticos(self, db: Session) -> set[int]:
        stmt = select(self.model.IDRepuesto).where(self.model.Critico.is_(True))
        return set(db.execute(stmt).scalars())

    def _select_base(self):
        codigo_col = func.concat(self.model.Familia, ".", self.model.Articulo).label(
            "Codigo"
        )
        return select(
            self.model.IDRepuesto,
            codigo_col,
            self.model.Descripcion,
            self.model.Conjunto,
            self.model.Condicion,
            self.model.Critico,
        )

    def _filtrar(self, stmt, conjunto, descripcion, codigo, critico):
        if conjunto:
            stmt = stmt.where(self.model.Conjunto == conjunto)

        if descripcion:
            for palabra in descripcion.split():
                stmt = stmt.where(
                    self.model.Descripcion.icontains(palabra, autoescape=True)
                )

        if codigo:
            codigo_expr = (
                cast(self.model.Familia, Text)
                .op("||")(literal_column("'.'"))
                .op("||")(cast(self.model.Articulo, Text))
            )
            stmt = stmt.where(codigo_expr.ilike(f"%{codigo}%"))

        if critico is True:
            stmt = stmt.where(self.model.Critico.is_(True))

        return stmt

    def get_repuestos(
        self,
        db,
        conjunto,
        descripcion,
        codigo,
        critico,
        limit,
        page,
    ):
        stmt = self._filtrar(
            self._select_base(), conjunto, descripcion, codigo, critico
        )
        return self._paginar_offset(
            db,
            stmt,
            limit,
            page,
            order_cols=(self.model.Descripcion.asc(), self.model.IDRepuesto.asc()),
        )

    def stmt_exportar(
        self,
        conjunto,
        descripcion,
        codigo,
        critico,
    ):
        stmt = self._filtrar(
            self._select_base(),
            conjunto,
            descripcion,
            codigo,
            critico,
        )
        return stmt.order_by(self.model.Descripcion.asc(), self.model.IDRepuesto.asc())


class RepuestoUnidadesRepository(BaseRepository[RepuestoUnidadesModel]):
    model = RepuestoUnidadesModel
