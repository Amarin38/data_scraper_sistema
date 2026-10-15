from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Integer,
    Numeric,
    and_,
    case,
    delete,
    func,
    insert,
    literal,
    or_,
    select,
    union_all,
)
from sqlalchemy.orm import Session

from src.core.enums import TipoDuracionEnum, TipoMovEnum, TipoUsuarioEnum
from src.db.models.estadisticas.duracion_repuestos_model import DuracionRepuestosModel
from src.db.models.ficha_stock_model import FichaStockModel
from src.db.models.interno_vigencia_model import InternoVigenciaModel
from src.db.models.repuesto_model import RepuestoModel
from src.db.models.repuesto_unidades_model import RepuestoUnidadesModel
from src.repositories.estadisticas import DuracionRepuestosRepository
from src.repositories.ficha_stock_repository import FichaStockRepository
from src.repositories.parque_movil_repository import ParqueMovilHistorialRepository

ficha_stock = FichaStockRepository()
parque_movil_historial = ParqueMovilHistorialRepository()
duracion_rep = DuracionRepuestosRepository()


# duración estimada = Σ días de exposición / Σ fallas observadas
def compute_duracion(
    db: Session, desde: date = date(2018, 1, 1), corte: date | None = None
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

    autos = (
        select(
            vigencia.Dominio,
            func.min(vigencia.FechaPatentado).label("Patentado"),
            case(
                (func.bool_or(vigencia.FechaHasta.is_(None)), literal(corte, Date)),
                else_=func.max(vigencia.FechaHasta),
            ).label("Fin"),
        )
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
        )
        .join(autos, valido)
        .group_by(cam.IDRepuesto, cam.Dominio, aut.Fin)
    )

    print("cambios:", db.scalar(select(func.count()).select_from(cambios)))
    print("autos:", db.scalar(select(func.count()).select_from(autos)))
    print(
        "total:",
        db.scalar(
            select(func.count()).select_from(
                union_all(piezas_cambiadas, piezas_vigentes).subquery()
            )
        ),
    )

    cols = [
        "IDRepuesto",
        "Dominio",
        "Cambio",
        "FechaInicio",
        "FechaCambio",
        "DuracionDias",
        "Unidades",
        "Censurado",
    ]
    db.execute(delete(duracion))
    return db.execute(  # type: ignore
        insert(duracion.__table__).from_select(
            cols, union_all(piezas_cambiadas, piezas_vigentes)
        )
    ).rowcount


def view_duracion():
    duracion, rep, rep_unid, int_vigen = (
        DuracionRepuestosModel,
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
    falla = ~duracion.Censurado
    unid_coche = func.coalesce(rep_unid.Unidades, 1)

    unidades = func.sum(func.least(duracion.Unidades, unid_coche)).filter(falla)
    exposicion = func.sum(duracion.DuracionDias * unid_coche)
    estimada = exposicion.cast(Numeric) / func.nullif(unidades, 0)

    coches = func.count(duracion.Dominio.distinct())
    duracion_dias = func.round(estimada, 1)
    duracion_años = func.round(estimada / 365, 2)

    dias_obs = func.max(duracion.DuracionDias)

    return (
        select(
            duracion.IDRepuesto,
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
        .join(rep, rep.IDRepuesto == duracion.IDRepuesto)
        .join(patentado, pat.Dominio == duracion.Dominio)
        .outerjoin(
            rep_unid,
            and_(
                rep_unid.IDRepuesto == duracion.IDRepuesto,
                pat.FechaPatentado >= rep_unid.FechaDesde,
                or_(
                    rep_unid.FechaHasta.is_(None),
                    pat.FechaPatentado < rep_unid.FechaHasta,
                ),
            ),
        )
        .group_by(
            duracion.IDRepuesto,
            rep.Descripcion,
            rep.Conjunto,
            rep.TipoDuracion,
        )
    )
