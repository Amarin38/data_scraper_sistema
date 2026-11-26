from datetime import date

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from shared.core.enums import CabecerasEnum, TipoMovEnum
from shared.db.models import FichaStockModel, RepuestoFijadoModel, RepuestoModel
from shared.db.models.repuesto_model import codigo_expr
from shared.repositories.base_repository import BaseRepository


class RepuestoFijadoRepository(BaseRepository[RepuestoFijadoModel]):
    model = RepuestoFijadoModel
    ficha = FichaStockModel
    rep = RepuestoModel

    def listar(self, db, id_usuario: int, desde: int, hasta: int):
        """Años calendario completos: de 1/1/desde hasta 31/12/hasta."""
        inicio = date(desde, 1, 1)
        fin = date(hasta + 1, 1, 1)
        ids = select(self.model.IDRepuesto).where(self.model.IDUsuario == id_usuario)

        # Salidas de Megabus (incluye transferencias a cabeceras)
        salidas = (
            select(
                self.ficha.IDRepuesto,
                (-func.sum(self.ficha.Cantidad)).label("Consumo"),
                (
                    -func.sum(
                        self.ficha.Cantidad
                        * func.coalesce(self.ficha.PrecioUnitario, 0)
                    )
                ).label("Gasto"),
            )
            .where(
                self.ficha.IDRepuesto.in_(ids),
                self.ficha.Deposito == CabecerasEnum.MEGABUS,
                self.ficha.TipoMov == TipoMovEnum.SALIDA,
                self.ficha.FechaMov >= inicio,
                self.ficha.FechaMov < fin,
            )
            .group_by(self.ficha.IDRepuesto)
            .subquery()
        )
        gasto = func.coalesce(salidas.c.Gasto, 0)

        stmt = (
            select(
                self.rep.IDRepuesto,
                codigo_expr().label("Codigo"),
                self.rep.Descripcion,
                func.coalesce(salidas.c.Consumo, 0).label("Consumo"),
                gasto.label("Gasto"),
            )
            .select_from(self.model)
            .join(self.rep, self.rep.IDRepuesto == self.model.IDRepuesto)
            .outerjoin(salidas, salidas.c.IDRepuesto == self.rep.IDRepuesto)
            .where(self.model.IDUsuario == id_usuario)
            .order_by(gasto.desc())
        )
        return db.execute(stmt).all()

    def fijar(self, db, id_usuario: int, id_repuesto: int) -> bool:
        try:
            db.execute(
                insert(self.model)
                .values(IDUsuario=id_usuario, IDRepuesto=id_repuesto)
                .on_conflict_do_nothing()
            )
            db.commit()
            return True
        except IntegrityError:  # repuesto inexistente
            db.rollback()
            return False

    def desfijar(self, db, id_usuario: int, id_repuesto: int) -> None:
        db.execute(
            delete(self.model).where(
                self.model.IDUsuario == id_usuario,
                self.model.IDRepuesto == id_repuesto,
            )
        )
        db.commit()

    def buscar(self, db, q: str, limite: int = 15):
        """Cada palabra de q debe aparecer en 'código | descripción' (sin distinguir mayúsculas)."""
        codigo = codigo_expr()
        texto = func.concat(codigo, " · ", self.rep.Descripcion)
        stmt = select(self.rep.IDRepuesto, codigo.label("Codigo"), self.rep.Descripcion)
        for palabra in q.split():
            stmt = stmt.where(texto.icontains(palabra, autoescape=True))
        return db.execute(stmt.order_by(codigo).limit(limite)).all()
