import argparse
from pathlib import Path

import pandas as pd

from constants import (
    RUTA_ARCHIVOS,
    RUTA_SERVER,
    TODAY,
    TODAY_MINUS_ONE,
    ListadoExistencias,
)
from get_dbf import buscar_dbf, inspeccionar
from local import Local
from web import Web


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extrae datos de el sistema y los transforma en un .xlsx"
    )

    parser.add_argument(
        "--opcion",
        default="FICHA_STOCK",
        choices=[ch.name for ch in ListadoExistencias],
        help="Lugar de donde extraer los datos del sistema.",
    )
    parser.add_argument("--dep-inicio")
    parser.add_argument("--dep-final")

    parser.add_argument("--cod-desde")
    parser.add_argument("--cod-hasta")

    parser.add_argument("--fecha-desde", help="dd/mm/AAAA", default=TODAY_MINUS_ONE)
    parser.add_argument("--fecha-hasta", help="dd/mm/AAAA", default=TODAY)

    parser.add_argument("--user", default="auditoria")
    parser.add_argument("--passwd", default="3801")

    parser.add_argument("--salida", type=Path, default=RUTA_ARCHIVOS)
    parser.add_argument("--tipo-scrap", choices=["local", "web"])

    parser.add_argument("--dbf")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.tipo_scrap == "web":
        Web().scrap()
    else:
        local = Local()
        local.iniciar_sesion(args.user, args.passwd)
        local.pestaña_principal(
            ListadoExistencias[args.opcion],
            args.dep_inicio,
            args.dep_final,
            args.cod_desde,
            args.cod_hasta,
            args.fecha_desde,
            args.fecha_hasta,
            Path(args.salida),
        )
