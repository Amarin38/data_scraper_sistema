from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Integer,
    and_,
    case,
    delete,
    exists,
    func,
    insert,
    literal,
    or_,
    select,
    union_all,
)
from sqlalchemy.orm import Session, aliased

from src.core.enums import TipoDuracionEnum, TipoMovEnum, TipoUsuarioEnum
from src.db.models.estadisticas.duracion_repuestos_model import DuracionRepuestosModel
from src.db.models.ficha_stock_model import FichaStockModel
from src.db.models.interno_vigencia_model import InternoVigenciaModel
from src.db.models.parque_movil_model import ParqueMovilModel
from src.db.models.repuesto_model import RepuestoModel
from src.repositories.estadisticas import DuracionRepuestosRepository
from src.repositories.ficha_stock_repository import FichaStockRepository
from src.repositories.parque_movil_repository import ParqueMovilHistorialRepository

ficha_stock = FichaStockRepository()
parque_movil_historial = ParqueMovilHistorialRepository()
duracion_rep = DuracionRepuestosRepository()

MIN_COCHES_MODELO = 3
MIN_COBERTURA = 0.5
MARGEN_INACTIVIDAD_DIAS = 180


# duración estimada = Σ días de exposición / Σ fallas observadas
def compute_duracion(
    db: Session, desde: date = date(2011, 1, 1), corte: date | None = None
) -> int:
    corte = corte or date.today()
    tipos = TipoDuracionEnum.obtener_con_duracion()
    ficha, vigencia, repuesto, duracion = (
        FichaStockModel,
        InternoVigenciaModel,
        RepuestoModel,
        DuracionRepuestosModel,
    )

    cambios = (
        select(
            ficha.IDRepuesto,
            vigencia.Dominio,
            ficha.FechaMov.label("FechaCambio"),
            func.sum(func.abs(ficha.Cantidad)).cast(Integer).label("Unidades"),
        )
        .join(
            vigencia,
            and_(
                vigencia.Interno == ficha.Interno,
                ficha.FechaMov >= vigencia.FechaDesde,
                or_(
                    vigencia.FechaHasta.is_(None), ficha.FechaMov < vigencia.FechaHasta
                ),
            ),
        )
        .join(repuesto, repuesto.IDRepuesto == ficha.IDRepuesto)
        .where(
            ficha.TipoMov == TipoMovEnum.SALIDA,
            ficha.TipoUsuario == TipoUsuarioEnum.COCHE,
            repuesto.TipoDuracion.in_(tipos),
        )
        .group_by(ficha.IDRepuesto, vigencia.Dominio, ficha.FechaMov)
        .cte("Cambios")
    )

    actividad = (
        select(
            cambios.c.Dominio.label("Dominio"),
            func.max(cambios.c.FechaCambio).label("Ultima"),
        )
        .group_by(cambios.c.Dominio)
        .cte("actividad")
    )
    act = actividad.c

    fin_base = case(
        (func.bool_or(vigencia.FechaHasta.is_(None)), literal(corte, Date)),
        else_=func.max(vigencia.FechaHasta),
    )

    autos = (
        select(
            vigencia.Dominio,
            func.min(vigencia.FechaPatentado).label("Patentado"),
            func.least(
                fin_base,
                func.max(act.Ultima) + literal(MARGEN_INACTIVIDAD_DIAS, Integer),
                type_=Date,
            ).label("Fin"),
        )
        .join(actividad, act.Dominio == vigencia.Dominio)
        .group_by(vigencia.Dominio)
        .having(func.min(vigencia.FechaPatentado) >= desde)
        .cte("autos")
    )
    cam, aut = cambios.c, autos.c
    valido = and_(aut.Dominio == cam.Dominio, cam.FechaCambio >= aut.Patentado)
    window = {
        "partition_by": [cam.IDRepuesto, cam.Dominio],
        "order_by": cam.FechaCambio,
    }

    inicio = func.coalesce(func.lag(cam.FechaCambio).over(**window), aut.Patentado)  # type: ignore
    cambio_cam = func.row_number().over(**window)  # type: ignore
    dias_cam = cam.FechaCambio - inicio
    censurado_cam = literal(False, Boolean)

    piezas_cambiadas = select(
        cam.IDRepuesto,
        cam.Dominio,
        cambio_cam.label("Cambio"),
        inicio.label("FechaInicio"),
        cam.FechaCambio,
        dias_cam.label("DuracionDias"),
        cam.Unidades,
        censurado_cam.label("Censurado"),
        aut.Patentado.label("FechaPatentado"),
    ).join(autos, valido)

    cambio_vig = func.count() + 1
    fecha_inicio_vig = func.max(cam.FechaCambio)
    dias_vig = aut.Fin - func.max(cam.FechaCambio)
    unidades_vig = literal(0, Integer)
    censurado_vig = literal(True, Boolean)

    piezas_vigentes = (
        select(
            cam.IDRepuesto,
            cam.Dominio,
            cambio_vig.label("Cambio"),
            fecha_inicio_vig.label("FechaInicio"),
            aut.Fin.label("FechaCambio"),
            dias_vig.label("DuracionDias"),
            unidades_vig.label("Unidades"),
            censurado_vig.label("Censurado"),
            aut.Patentado.label("FechaPatentado"),
        )
        .join(autos, valido)
        .group_by(cam.IDRepuesto, cam.Dominio, aut.Fin, aut.Patentado)
    )

    pm_cambio = aliased(ParqueMovilModel)
    pm_tot = aliased(ParqueMovilModel)
    pm_todos = aliased(ParqueMovilModel)

    # coches por (chasis, motor), solo los del análisis (patentados desde `desde`)
    total_grupo = (
        select(
            pm_tot.IDChasis.label("IDChasis"),
            pm_tot.IDMotor.label("IDMotor"),
            func.count(func.distinct(pm_tot.Dominio)).label("Total"),
        )
        .join(autos, aut.Dominio == pm_tot.Dominio)
        .where(pm_tot.IDChasis.is_not(None), pm_tot.IDMotor.is_not(None))
        .group_by(pm_tot.IDChasis, pm_tot.IDMotor)
        .cte("total_grupo")
    )
    tot = total_grupo.c

    con_cambio = func.count(func.distinct(cam.Dominio))
    modelos = (
        select(cam.IDRepuesto, pm_cambio.IDChasis, pm_cambio.IDMotor)
        .select_from(cambios)
        .join(autos, aut.Dominio == cam.Dominio)
        .join(pm_cambio, pm_cambio.Dominio == cam.Dominio)
        .join(
            total_grupo,
            and_(
                tot.IDChasis == pm_cambio.IDChasis,
                tot.IDMotor == pm_cambio.IDMotor,
            ),
        )
        .group_by(cam.IDRepuesto, pm_cambio.IDChasis, pm_cambio.IDMotor, tot.Total)
        .having(
            con_cambio >= MIN_COCHES_MODELO,
            con_cambio >= MIN_COBERTURA * tot.Total,
        )
        .cte("modelos")
    )
    mod = modelos.c

    nunca_cambiado = ~exists().where(
        cam.IDRepuesto == mod.IDRepuesto, cam.Dominio == pm_todos.Dominio
    )

    piezas_nunca = (
        select(
            mod.IDRepuesto,
            aut.Dominio,
            literal(1, Integer).label("Cambio"),
            aut.Patentado.label("FechaInicio"),
            aut.Fin.label("FechaCambio"),
            (aut.Fin - aut.Patentado).label("DuracionDias"),
            literal(0, Integer).label("Unidades"),
            literal(True, Boolean).label("Censurado"),
            aut.Patentado.label("FechaPatentado"),
        )
        .select_from(modelos)
        .join(
            pm_todos,
            and_(pm_todos.IDChasis == mod.IDChasis, pm_todos.IDMotor == mod.IDMotor),
        )
        .join(autos, aut.Dominio == pm_todos.Dominio)
        .where(nunca_cambiado, aut.Fin > aut.Patentado)
    )

    todas = union_all(piezas_cambiadas, piezas_vigentes, piezas_nunca)

    print("cambios:", db.scalar(select(func.count()).select_from(cambios)))
    print("autos:", db.scalar(select(func.count()).select_from(autos)))
    print(
        "nunca cambiadas:",
        db.scalar(select(func.count()).select_from(piezas_nunca.subquery())),
    )
    print("total:", db.scalar(select(func.count()).select_from(todas.subquery())))

    cols = [
        "IDRepuesto",
        "Dominio",
        "Cambio",
        "FechaInicio",
        "FechaCambio",
        "DuracionDias",
        "Unidades",
        "Censurado",
        "FechaPatentado",
    ]
    db.execute(delete(duracion))
    return db.execute(  # type: ignore
        insert(duracion.__table__).from_select(cols, todas)
    ).rowcount
