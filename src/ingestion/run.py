import argparse

from src.core.enums import CabecerasPathEnum, ListadoExistencias, TipoScrap
from src.db.session import SessionLocal, dbbase, engine_postgresql
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

        parser.add_argument(
            "--cabecera",
            default="Megabus",
            choices=[ca.value[0] for ca in CabecerasPathEnum],
            help="Cabecera de la cual vienen los datos.",
        )

    return parser.parse_args()


if __name__ == "__main__":
    dbbase.metadata.create_all(engine_postgresql)

    args = parse_args()
    session = SessionLocal()

    match args.tipo:
        case TipoScrap.WEB:
            Web(session).scrap()
        case TipoScrap.LOCAL:
            for path in CabecerasPathEnum:
                if args.cabecera == path.value[0]:
                    local = LocalDBF(session, path)
                    break
                else:
                    local = None

            if args.opcion == ListadoExistencias.FICHA_STOCK:
                local.guardar_ficha_stock()  # type: ignore
            elif args.opcion == ListadoExistencias.EXISTENCIA_STOCK:
                local.guardar_existencia_stock()  # type: ignore
