import argparse

import pandas as pd

from src.compute.duracion_repuestos import compute_duracion, view_duracion
from src.compute.indice_consumo import compute_indice_consumo
from src.compute.prevision import ComputePrevision
from src.core.enums import TipoCompute
from src.db.session import SessionLocal, dbbase, engine


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

            df = pd.read_sql(view_duracion(), session.bind)  # type: ignore
            print(
                df.loc[
                    (df["Descripcion"] == "DISCO FRENO AGRALE")
                    & (df["UnidadesFalladas"] > 10)
                ]
            )
        case TipoCompute.PREVISION:
            df = ComputePrevision().calcular_prevision(session, 12)
            session.commit()
            print(df)
        case TipoCompute.INDICE_CONSUMO:
            compute_indice_consumo(session)
            session.commit()
