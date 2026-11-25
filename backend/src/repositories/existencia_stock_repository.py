from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy import Numeric, case, cast, func, insert, literal, select, text

from src.core.constants import TODAY
from src.core.enums import CabecerasEnum
from src.db.models.existencia_stock_model import ExistenciaStockModel
from src.db.models.ficha_stock_model import FichaStockModel
from src.db.models.repuesto_model import RepuestoModel, codigo_expr
from src.db.views.consumo_mensual_deposito import t as consumo_dep
from src.repositories.base_repository import BaseRepository

MIN_MESES_CON_DATOS = 6
DEPOSITO_EXISTENCIA = "Megabus"
MESES_SIN_USO = 24


def rango_meses(desde: date | None, hasta: date | None, defecto: int = 12):
    """(ini, fin, n): meses cerrados, fin exclusivo, nunca incluye el mes actual."""
    hoy_mes = date.today().replace(day=1)
    if hasta:
        fin = min(hasta.replace(day=1) + relativedelta(months=1), hoy_mes)
    else:
        fin = hoy_mes
    ini = desde.replace(day=1) if desde else fin - relativedelta(months=defecto)
    n = (fin.year - ini.year) * 12 + fin.month - ini.month
    return ini, fin, n


# columnas por las que se puede ordenar (lista cerrada: nunca se arma SQL con texto del usuario)
ORDEN_PERMITIDO = (
    "Codigo",
    "Descripcion",
    "Condicion",
    "Conjunto",
    "Critico",
    "FechaExistencia",
    "Stock",
    "Minimo",
    "Maximo",
    "Reponer",
)


def limite_sin_uso() -> date:
    return date.today().replace(day=1) - relativedelta(months=MESES_SIN_USO)


class ExistenciaStockRepository(BaseRepository[ExistenciaStockModel]):
    model = ExistenciaStockModel
    codigo_col = codigo_expr()

    def _select_base(self, mm: dict | None = None):
        stock = func.coalesce(self.model.Stock, 0)

        exprs = {
            "Codigo": self.codigo_col,
            "Descripcion": RepuestoModel.Descripcion,
            "Condicion": RepuestoModel.Condicion,
            "Conjunto": RepuestoModel.Conjunto,
            "Critico": RepuestoModel.Critico,
            "FechaExistencia": self.model.FechaExistencia,
            "Stock": stock,
        }
        if mm is None:
            nulo = cast(literal(None), Numeric)
            exprs.update({"Minimo": nulo, "Maximo": nulo, "Reponer": nulo})
            demanda = None
        else:
            c = consumo_dep.c
            demanda = (
                select(
                    c.IDRepuesto,
                    (func.sum(c.consumo) / float(mm["n"])).label("Demanda"),
                    func.count().label("Meses"),
                )
                .where(
                    c.Deposito == mm["deposito"],
                    c.mes >= mm["ini"],
                    c.mes < mm["fin"],
                )
                .group_by(c.IDRepuesto)
                .subquery("demanda")
            )
            d = demanda.c
            aplica = d.Meses >= mm["min_datos"]
            minimo = case((aplica, func.ceil(d.Demanda * mm["meses_min"])))
            maximo = case((aplica, func.ceil(d.Demanda * mm["meses_max"])))
            exprs.update(
                {
                    "Minimo": minimo,
                    "Maximo": maximo,
                    "Reponer": case((stock < minimo, maximo - stock), else_=0),
                }
            )

        limite = date.today().replace(day=1) - relativedelta(months=MESES_SIN_USO)
        sin_uso = func.coalesce(self.model.UltimoConsumo < limite, True)

        stmt = (
            select(
                RepuestoModel.IDRepuesto,
                self.model.IDExistencia,
                exprs["Codigo"].label("Codigo"),
                RepuestoModel.Descripcion,
                RepuestoModel.Condicion,
                RepuestoModel.Conjunto,
                RepuestoModel.Critico,
                stock.label("Stock"),
                self.model.FechaExistencia,
                exprs["Minimo"].label("Minimo"),
                exprs["Maximo"].label("Maximo"),
                exprs["Reponer"].label("Reponer"),
                self.model.UltimoConsumo,
                sin_uso.label("SinUso"),
            )
            .select_from(RepuestoModel)
            .outerjoin(self.model, self.model.IDRepuesto == RepuestoModel.IDRepuesto)
        )
        if demanda is not None:
            stmt = stmt.outerjoin(
                demanda, demanda.c.IDRepuesto == RepuestoModel.IDRepuesto
            )

        stmt._orden_exprs = exprs  # expresiones por nombre, para ordenar
        return stmt

    def _filtrar(
        self,
        stmt,
        conjunto,
        descripcion,
        codigo,
        con_max_min=False,
        critico=False,
        incluir_sin_uso=False,
    ):
        if conjunto:
            stmt = stmt.where(RepuestoModel.Conjunto == conjunto)

        if descripcion:
            for palabra in descripcion.split():
                stmt = stmt.where(
                    RepuestoModel.Descripcion.icontains(palabra, autoescape=True)
                )
        if codigo:
            stmt = stmt.where(self.codigo_col.ilike(f"%{codigo}%"))

        if critico:
            stmt = stmt.where(RepuestoModel.Critico.is_(True))

        if con_max_min:
            # solo los que tienen mínimo y máximo (suficientes meses con datos)
            stmt = stmt.where(
                stmt.selected_columns.Minimo.is_not(None),
                stmt.selected_columns.Reponer != 0,
            ).order_by(stmt.selected_columns.Reponer.desc())

        if not incluir_sin_uso:
            stmt = stmt.where(self.model.UltimoConsumo >= limite_sin_uso())

        sin_filtros = not (
            conjunto
            or descripcion
            or codigo
            or con_max_min
            or critico
            or not incluir_sin_uso
        )
        total_stmt = (
            select(func.count()).select_from(RepuestoModel) if sin_filtros else None
        )

        return stmt, total_stmt

    def _orden(self, stmt, orden: str | None, direccion: str):
        """Orden pedido por el usuario; siempre desempata por IDRepuesto."""
        exprs = getattr(stmt, "_orden_exprs", {})
        if orden not in ORDEN_PERMITIDO or orden not in exprs:
            return None
        col = exprs[orden]
        col = col.desc() if direccion == "desc" else col.asc()
        return (col.nulls_last(), RepuestoModel.IDRepuesto.asc())

    def get_existencias(
        self,
        db,
        descripcion,
        codigo,
        conjunto,
        limit,
        page,
        mm=None,
        con_max_min=False,
        orden=None,
        direccion="asc",
        critico=False,
        incluir_sin_uso=False,
    ):
        stmt, total_stmt = self._filtrar(
            self._select_base(mm),
            conjunto,
            descripcion,
            codigo,
            con_max_min,
            critico,
            incluir_sin_uso,
        )
        order_cols = self._orden(stmt, orden, direccion) or (
            RepuestoModel.Descripcion.asc(),
            RepuestoModel.IDRepuesto.asc(),
        )

        return self._paginar_offset(
            db,
            stmt,
            limit,
            page,
            order_cols=order_cols,
            total_stmt=total_stmt,
        )

    def stmt_exportar(
        self,
        conjunto,
        descripcion,
        codigo,
        mm=None,
        con_max_min=False,
        orden=None,
        direccion="asc",
        critico=False,
        incluir_sin_uso=False,
    ):
        stmt, _ = self._filtrar(
            self._select_base(mm),
            conjunto,
            descripcion,
            codigo,
            con_max_min,
            critico,
            incluir_sin_uso,
        )
        order_cols = self._orden(stmt, orden, direccion) or (
            self.codigo_col.desc(),
            RepuestoModel.IDRepuesto.asc(),
        )
        return stmt.order_by(None).order_by(*order_cols)

    def stock_actual(self, db, id_repuesto: int):
        """(Stock, FechaExistencia) del repuesto, o (None, None) si no hay fila."""
        fila = db.execute(
            select(self.model.Stock, self.model.FechaExistencia)
            .where(self.model.IDRepuesto == id_repuesto)
            .order_by(self.model.FechaExistencia.desc())
            .limit(1)
        ).first()
        return (fila[0], fila[1]) if fila else (None, None)

    def insert_existencia(self, db, cabecera: CabecerasEnum) -> int:
        """Reemplaza existencia_stock con la suma de ficha_stock por repuesto."""
        f = FichaStockModel
        c = consumo_dep.c

        ultimo = (
            select(c.IDRepuesto, func.max(c.mes).label("Ultimo"))
            .where(c.consumo > 0)
            .group_by(c.IDRepuesto)
            .cte("ultimo")
        )

        suma = (
            select(
                f.IDRepuesto,
                func.sum(f.Cantidad),
                literal(TODAY),
                literal(cabecera.name),
                func.max(ultimo.c.Ultimo),
            )
            .select_from(f)
            .outerjoin(ultimo, ultimo.c.IDRepuesto == f.IDRepuesto)
            .where(f.Deposito == cabecera)
            .group_by(f.IDRepuesto)
        )

        sin_ficha = select(
            ultimo.c.IDRepuesto,
            literal(0),
            literal(TODAY),
            literal(cabecera.name),
            ultimo.c.Ultimo,
        ).where(
            ultimo.c.Ultimo >= limite_sin_uso(),
            ultimo.c.IDRepuesto.not_in(
                select(f.IDRepuesto).where(f.Deposito == cabecera).distinct()
            ),
        )
        union = suma.union_all(sin_ficha).subquery("existencias")

        db.execute(text('TRUNCATE TABLE "existencia_stock" RESTART IDENTITY'))
        db.execute(
            insert(self.model).from_select(
                ["IDRepuesto", "Stock", "FechaExistencia", "Cabecera", "UltimoConsumo"],
                select(union),
            )
        )
        n = db.scalar(select(func.count()).select_from(self.model))
        if n == 0:
            db.rollback()  # deshace el TRUNCATE
            raise RuntimeError(
                f"ficha_stock no tiene filas para '{cabecera.value}': "
                "existencia_stock no se modificó"
            )
        db.commit()
        return n
