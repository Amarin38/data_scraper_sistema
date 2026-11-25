import argparse

from pipeline.compute.duracion_repuestos import compute_duracion
from pipeline.compute.indice_consumo import compute_indice_consumo
from pipeline.compute.max_min import compute_max_min
from pipeline.compute.prevision import ComputePrevision
from shared.core.enums import TipoCompute
from shared.db.session import SessionLocal, dbbase, engine
from shared.db.views import mantenimiento, refrescar_vistas


def parse_args():
    pre = argparse.ArgumentParser(
        description="Extrae datos de el sistema y los transforma en un csv formateado.",
        add_help=False,
    )

    pre.add_argument(
        "--tipo",
        choices=[ch.value for ch in TipoCompute],
        help="Tipo de compute a realizar.",
    )

    return pre.parse_args()


if __name__ == "__main__":
    dbbase.metadata.create_all(engine)

    args = parse_args()
    session = SessionLocal()

    match args.tipo:
        case TipoCompute.DURACION_REPUESTOS:
            compute_duracion(session)
            session.commit()
            with session as db:
                refrescar_vistas(db)
            mantenimiento()
        case TipoCompute.PREVISION:
            df = ComputePrevision().calcular_prevision(session, 12)
            session.commit()
            print(df)
        case TipoCompute.INDICE_CONSUMO:
            compute_indice_consumo(session)
            session.commit()
        case TipoCompute.MAXIMOS_MINIMOS:
            compute_max_min(session)
            session.commit()
