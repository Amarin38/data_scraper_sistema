from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from sqlalchemy import Numeric, Select, and_, func, literal, or_, select

from src.core.enums import CabecerasEnum
from src.db.models.estadisticas.conteo_stock_model import ConteoStockModel
from src.db.models.estadisticas.duracion_repuestos_model import DuracionRepuestosModel
from src.db.models.estadisticas.indice_consumo_model import IndiceConsumoModel
from src.db.models.estadisticas.prevision_model import PrevisionModel
from src.db.models.interno_vigencia_model import InternoVigenciaModel
from src.db.models.repuesto_model import RepuestoModel
from src.db.models.repuesto_unidades_model import RepuestoUnidadesModel
from src.db.views.consumo_mensual import t as consumo_mensual
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


class PrevisionRepository(BaseRepository[PrevisionModel]):
    model = PrevisionModel

    def listar_por_repuesto(self, db, id_repuesto: int):
        hoy_mes = date.today().replace(day=1)
        desde = hoy_mes - relativedelta(months=24)

        consumo = select(
            consumo_mensual.c.IDRepuesto,
            func.to_char(consumo_mensual.c.mes, "YYYY-MM").label("Mes"),
            consumo_mensual.c.consumo.label("Cantidad"),
            literal("Consumo").label("Tipo"),
        ).where(
            consumo_mensual.c.IDRepuesto == id_repuesto,
            consumo_mensual.c.mes >= desde,
            consumo_mensual.c.mes < hoy_mes,
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

    def listar_por_repuesto(self, db, id_repuesto: int):
        fila = (
            db.execute(
                select(
                    (func.avg(self.model.DuracionDias) / 365.0).label("Media"),
                    (func.stddev_samp(self.model.DuracionDias) / 365.0).label("Desvio"),
                    func.count().label("N"),
                ).where(self.model.IDRepuesto == id_repuesto, ~self.model.Censurado)
            )
            .mappings()
            .one()
        )
        return dict(fila)


class ConteoStockRepository(BaseRepository[ConteoStockModel]):
    model = ConteoStockModel
