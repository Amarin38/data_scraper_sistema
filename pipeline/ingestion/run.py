import argparse
import logging
import os
import time

from src.core.enums import CabecerasEnum, ListadoExistencias, TipoScrap
from src.core.paths import CabecerasPathEnum
from src.db.session import SessionLocal, dbbase, engine
from src.db.views import crear_vistas, mantenimiento, refrescar_vistas
from src.ingestion.scrapers import GuardarLocal, Web
from src.repositories.existencia_stock_repository import ExistenciaStockRepository

logger = logging.getLogger("ingesta")


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
            "--archivos",
            default="todos",
            choices=["todos", "parcial"],
            help="Cantidad de archivos a utilizar en la ficha de stock.",
        )

    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(message)s",
        datefmt="%H:%M:%S",
    )
    dbbase.metadata.create_all(engine)

    args = parse_args()
    session = SessionLocal()
    u = engine.url
    logger.debug("DB %s@%s:%s/%s", u.username, u.host, u.port, u.database)

    match args.tipo:
        case TipoScrap.WEB:
            Web(session).scrap()
        case TipoScrap.LOCAL:
            if args.opcion == ListadoExistencias.EXISTENCIA_STOCK:
                n = ExistenciaStockRepository().insert_existencia(
                    session, CabecerasEnum.MEGABUS
                )
                print(f"✔ {n:,} repuestos con existencia".replace(",", "."))
            else:
                for datos_cabecera in CabecerasPathEnum:
                    guardar = GuardarLocal(session, datos_cabecera)

                    if args.opcion == ListadoExistencias.FICHA_STOCK:
                        guardar.ficha_stock(args.archivos)
                    elif args.opcion == ListadoExistencias.REPUESTOS:
                        guardar.repuestos()

            if args.opcion == ListadoExistencias.FICHA_STOCK:
                t0 = time.perf_counter()
                logger.info("views  recargando...")
                with session as db:
                    crear_vistas(db)
                    refrescar_vistas(db)
                mantenimiento()
                logger.info("views  refrescadas en %.0fs", time.perf_counter() - t0)
