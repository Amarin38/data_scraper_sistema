from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from sqlalchemy import Numeric, Select, and_, func, literal, or_, select

from src.core.enums import CabecerasEnum, TipoMovEnum
from src.db.models.estadisticas.conteo_stock_model import ConteoStockModel
from src.db.models.estadisticas.duracion_repuestos_model import DuracionRepuestosModel
from src.db.models.estadisticas.indice_consumo_model import IndiceConsumoModel
from src.db.models.estadisticas.prevision_model import PrevisionModel
from src.db.models.ficha_stock_model import FichaStockModel
from src.db.models.interno_vigencia_model import InternoVigenciaModel
from src.db.models.repuesto_model import RepuestoModel
from src.db.models.repuesto_unidades_model import RepuestoUnidadesModel
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

    def listar_por_repuesto(self, db, id_repuesto: int):
        fila = (
            db.execute(
                select(
                    func.avg(self.model.DuracionDias / 365.0).label("Media"),
                    func.stddev_samp(self.model.DuracionDias / 365.0).label("Desvio"),
                    func.count().label("N"),
                ).where(self.model.IDRepuesto == id_repuesto, ~self.model.Censurado)
            )
            .mappings()
            .one()
        )
        return dict(fila)

    def view_duracion(self):
        rep, rep_unid, int_vigen = (
            RepuestoModel,
            RepuestoUnidadesModel,
            InternoVigenciaModel,
        )

        patentado = (
            select(
                int_vigen.Dominio,
                func.min(int_vigen.FechaPatentado).label("FechaPatentado"),
            )
            .group_by(int_vigen.Dominio)
            .subquery()
        )

        pat = patentado.c
        falla = ~self.model.Censurado
        unid_coche = func.coalesce(rep_unid.Unidades, 1)

        unidades = func.sum(func.least(self.model.Unidades, unid_coche)).filter(falla)
        exposicion = func.sum(self.model.DuracionDias * unid_coche)
        estimada = exposicion.cast(Numeric) / func.nullif(unidades, 0)

        coches = func.count(self.model.Dominio.distinct())
        duracion_dias = func.round(estimada, 1)
        duracion_años = func.round(estimada / 365, 2)

        dias_obs = func.max(self.model.DuracionDias)

        return (
            select(
                self.model.IDRepuesto,
                rep.Descripcion,
                rep.Conjunto,
                rep.TipoDuracion,
                coches.label("Coches"),
                unidades.label("UnidadesFalladas"),
                exposicion.label("DiasExposicion"),
                duracion_dias.label("DuracionEstimadaDias"),
                duracion_años.label("DuracionEstimadaAños"),
                dias_obs.label("MaxObservadoDias"),
            )
            .join(rep, rep.IDRepuesto == self.model.IDRepuesto)
            .join(patentado, pat.Dominio == self.model.Dominio)
            .outerjoin(
                rep_unid,
                and_(
                    rep_unid.IDRepuesto == self.model.IDRepuesto,
                    pat.FechaPatentado >= rep_unid.FechaDesde,
                    or_(
                        rep_unid.FechaHasta.is_(None),
                        pat.FechaPatentado < rep_unid.FechaHasta,
                    ),
                ),
            )
            .group_by(
                self.model.IDRepuesto,
                rep.Descripcion,
                rep.Conjunto,
                rep.TipoDuracion,
            )
        )


class ConteoStockRepository(BaseRepository[ConteoStockModel]):
    model = ConteoStockModel
