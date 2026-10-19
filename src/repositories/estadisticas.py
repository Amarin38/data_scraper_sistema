from dateutil.relativedelta import relativedelta
from src.db.models.ficha_stock_model import FichaStockModel
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, func, select, literal

from src.core.enums import CabecerasEnum, TipoMovEnum
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
        cursor_valor: str | None = None,
        cursor_id: int | None = None,
    ):
        type SelectType = Select[tuple[Any, str, str, Any, Any, Any]]

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

        stmt: SelectType = (
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
            stmt: SelectType = stmt.where(rep_model.Conjunto == conjunto)
        if texto:
            stmt: SelectType = stmt.where(rep_model.Descripcion.ilike(f"%{texto}%"))

        return self._paginar(
            db,
            stmt,
            limit,
            pk_col=("IDRepuesto", peor.c.IDRepuesto),
            valor_col=("MaxRelativo", peor.c.MaxRelativo),
            cursor=(cursor_id, cursor_valor),
        )


class PrevisionRepository(BaseRepository[PrevisionModel]):
    model = PrevisionModel

    def listar_por_repuesto(self, db, id_repuesto: int):
        ficha = FichaStockModel
        hoy_mes = date.today().replace(day=1)
        desde = hoy_mes - relativedelta(months=24)

        mes = func.to_char(ficha.FechaMov, "YYYY-MM")

        consumo = (
            select(
                ficha.IDRepuesto,
                mes.label("Mes"),
                (-func.sum(ficha.Cantidad)).label("Cantidad"),
                literal("Consumo").label("Tipo"),
            )
            .where(
                ficha.IDRepuesto == id_repuesto,
                ficha.TipoMov == TipoMovEnum.SALIDA,
                ficha.FechaMov >= desde,
                ficha.FechaMov < hoy_mes,
            )
            .group_by(ficha.IDRepuesto, mes)
        )

        prev = select(
            self.model.IDRepuesto,
            func.to_char(self.model.Periodo, "YYYY-MM").label("Mes"),
            self.model.Cantidad,
            literal("Prevision").label("Tipo"),
        ).where(self.model.IDRepuesto == id_repuesto)

        stmt = consumo.union_all(prev)
        return [dict(f) for f in db.execute(stmt).mappings().all()]


class DuracionRepuestosRepository(BaseRepository[DuracionRepuestosModel]):
    model = DuracionRepuestosModel

    def listar_por_repuesto(self, db, id_repuesto: int): ...


class ConteoStockRepository(BaseRepository[ConteoStockModel]):
    model = ConteoStockModel
