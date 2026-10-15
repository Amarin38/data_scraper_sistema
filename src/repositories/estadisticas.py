from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, and_, func, or_, select

from src.core.enums import CabecerasEnum
from src.db.models.estadisticas.conteo_stock_model import ConteoStockModel
from src.db.models.estadisticas.duracion_repuestos_model import DuracionRepuestosModel
from src.db.models.estadisticas.indice_consumo_model import IndiceConsumoModel
from src.db.models.estadisticas.prevision_model import PrevisionModel
from src.db.models.repuesto_model import RepuestoModel
from src.repositories.base_repository import BaseRepository

rep_model = RepuestoModel


class IndiceConsumoRepository(BaseRepository[IndiceConsumoModel]):
    model = IndiceConsumoModel

    def listar_por_repuesto(self, db, id_repuesto: int):
        type SelectIndice = Select[
            tuple[int, str, str, str, CabecerasEnum, Decimal, Decimal, Decimal, date]
        ]

        stmt: SelectIndice = (
            select(
                self.model.IDRepuesto,
                rep_model.Familia,
                rep_model.Articulo,
                rep_model.Descripcion,
                self.model.Deposito,
                self.model.Indice,
                self.model.IndiceGlobal,
                self.model.IndiceRelativo,
                self.model.FechaIndice,
            )
            .join(rep_model, rep_model.IDRepuesto == self.model.IDRepuesto)
            .where(self.model.IDRepuesto == id_repuesto)
            .order_by(rep_model.Descripcion)
        )

        return [dict(r) for r in db.execute(stmt).mappings().all()]

    def listar_peores(
        self,
        db,
        conjunto=None,
        texto=None,
        limit=50,
        cursor_valor: float | None = None,
        cursor_id: int | None = None,
    ):
        type SelectPeores = Select[tuple[Any, str, Any, Any, Any]]
        type SelectFinal = Select[tuple[Any, str, str, Any, Any, Any]]
        type Final = SelectPeores | SelectFinal

        peor = (
            (
                select(
                    self.model.IDRepuesto,
                    self.model.Deposito.label("PeorCabecera"),
                    self.model.IndiceRelativo.label("MaxRelativo"),
                )
            )
            .distinct(self.model.IDRepuesto)
            .order_by(self.model.IDRepuesto, self.model.IndiceRelativo.desc())
            .subquery()
        )

        rojas = (
            select(self.model.IDRepuesto, func.count().label("CantRojas"))
            .where(self.model.IndiceRelativo > 1.3)
            .group_by(self.model.IDRepuesto)
            .subquery()
        )

        stmt: SelectFinal = (
            select(
                peor.c.IDRepuesto,
                func.concat(rep_model.Familia, ".", rep_model.Articulo).label("Codigo"),
                rep_model.Descripcion,
                peor.c.PeorCabecera,
                peor.c.MaxRelativo,
                func.coalesce(rojas.c.CantRojas, 0).label("CantRojas"),
            )
            .join(rep_model, rep_model.IDRepuesto == peor.c.IDRepuesto)
            .outerjoin(rojas, rojas.c.IDRepuesto == peor.c.IDRepuesto)
            .order_by(peor.c.MaxRelativo.desc())
            .limit(limit)
        )

        if conjunto:
            stmt: SelectFinal = stmt.where(rep_model.Conjunto == conjunto)
        if texto:
            stmt: SelectFinal = stmt.where(rep_model.Descripcion.ilike(f"%{texto}%"))

        stmt: Final = stmt.order_by(peor.c.MaxRelativo.desc(), peor.c.IDRepuesto.asc())

        if cursor_valor is not None and cursor_id is not None:
            stmt: Final = stmt.where(
                or_(
                    peor.c.MaxRelativo < cursor_valor,
                    and_(
                        peor.c.MaxRelativo == cursor_valor,
                        peor.c.IDRepuesto > cursor_id,
                    ),
                )
            )

        # pido uno de más para saber si hay página siguiente
        filas = db.execute(stmt.limit(limit + 1)).mappings().all()
        hay_mas = len(filas) > limit
        filas = [dict(r) for r in filas[:limit]]

        next_cursor = None
        if hay_mas:
            ultima = filas[-1]
            next_cursor = {
                "valor": float(ultima["MaxRelativo"]),
                "id": ultima["IDRepuesto"],
            }

        return {"items": filas, "next_cursor": next_cursor}


class PrevisionRepository(BaseRepository[PrevisionModel]):
    model = PrevisionModel


class DuracionRepuestosRepository(BaseRepository[DuracionRepuestosModel]):
    model = DuracionRepuestosModel


class ConteoStockRepository(BaseRepository[ConteoStockModel]):
    model = ConteoStockModel
