import argparse

from src.core.enums import CabecerasPathEnum, ListadoExistencias, TipoScrap
from src.db.session import SessionLocal, dbbase, engine
from src.ingestion.scrapers import LocalDBF, Web


def parse_args():
    pre = argparse.ArgumentParser(
        description="Extrae datos de el sistema y los transforma en un csv formateado.",
        add_help=False,
    )

    pre.add_argument(
        "--tipo",
        default="web",
        choices=[ch.value for ch in TipoScrap],
        help="Tipo de scrapeo a realizar.",
    )

    known, _ = pre.parse_known_args()
    parser = argparse.ArgumentParser(parents=[pre])

    if known.tipo == TipoScrap.LOCAL:
        parser.add_argument(
            "--opcion",
            default="ficha_stock",
            choices=[ls.value for ls in ListadoExistencias],
            help="Lugar de donde extraer los datos del sistema.",
        )

    return parser.parse_args()


if __name__ == "__main__":
    dbbase.metadata.create_all(engine)

    args = parse_args()
    session = SessionLocal()

    match args.tipo:
        case TipoScrap.WEB:
            Web(session).scrap()
        case TipoScrap.LOCAL:
            for datos_cabecera in CabecerasPathEnum:
                local = LocalDBF(session, datos_cabecera)

                if args.opcion == ListadoExistencias.FICHA_STOCK:
                    local.guardar_ficha_stock()  # type: ignore
                elif args.opcion == ListadoExistencias.EXISTENCIA_STOCK:
                    local.guardar_existencia_stock()  # type: ignore
