from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from src.db.models.repuesto_model import RepuestoModel
from src.db.models.repuesto_unidades_model import RepuestoUnidadesModel
from src.repositories.base_repository import BaseRepository


class RepuestoRepository(BaseRepository[RepuestoModel]):
    model = RepuestoModel

    def get_criticos(self, db: Session) -> set[int]:
        stmt = select(self.model.IDRepuesto).where(self.model.Critico.is_(True))
        return set(db.execute(stmt).scalars())

    def get_conjuntos(self, db: Session):
        stmt = (
            select(self.model.Conjunto)
            .where(self.model.Conjunto.is_not(None))
            .distinct()
            .order_by(self.model.Conjunto)
        )

        return list(db.execute(stmt).scalars())

    def get_repuestos(self, db, conjunto, descripcion, codigo, critico, limit, page):
        type SelectType = Select[tuple[int, str, str, str | None, str, bool]]

        codigo_col = func.concat(self.model.Familia, ".", self.model.Articulo).label(
            "Codigo"
        )

        stmt: SelectType = select(
            self.model.IDRepuesto,
            codigo_col,
            self.model.Descripcion,
            self.model.Conjunto,
            self.model.Condicion,
            self.model.Critico,
        )

        if conjunto:
            stmt: SelectType = stmt.where(self.model.Conjunto == conjunto)

        if descripcion:
            for palabra in descripcion.split():
                stmt: SelectType = stmt.where(
                    self.model.Descripcion.icontains(palabra, autoescape=True)
                )

        if codigo:
            stmt: SelectType = stmt.where(codigo_col.ilike(f"%{codigo}%"))

        if critico is True:
            stmt: SelectType = stmt.where(self.model.Critico.is_(True))

        return self._paginar_offset(
            db,
            stmt,
            limit,
            page,
            order_cols=(self.model.Descripcion.asc(), self.model.IDRepuesto.asc()),
        )


class RepuestoUnidadesRepository(BaseRepository[RepuestoUnidadesModel]):
    model = RepuestoUnidadesModel
