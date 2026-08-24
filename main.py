import argparse
import time

import pandas as pd
import pywinauto
from pywinauto import Application, win32api
from pywinauto.keyboard import send_keys

from constants import (
    COORDS_EXCEL_BTTN,
    DOWN_ARR,
    ENTER,
    ENTER2,
    RUTA_ARCHIVOS,
    RUTA_PROGRAMA,
    TAB,
    TODAY,
    ListadoExistencias,
)

app = Application(backend="win32").start(
    str(RUTA_PROGRAMA / "cargador.exe"), work_dir=str(RUTA_PROGRAMA)
)


def posicion_pantalla():
    for i in range(10):
        time.sleep(2)
        print(win32api.GetCursorPos())


def iniciar_sesion(user: str, passwd: str):
    inicio = app.window(title="STOCK - Inicio de Sesión")
    inicio.wait("ready", timeout=15)
    inicio.set_focus()
    time.sleep(0.5)

    send_keys(user + TAB)
    send_keys(passwd + ENTER2)


def pestaña_principal(
    opcion: str,
    deposito_inicio: str,
    deposito_final: str,
    cod_desde: str,
    cod_hasta: str,
    fecha_desde: str,
    fecha_hasta: str,
):
    main = app.window(title_re=r"Sistemas San Antonio - Stock.*")
    main.wait("ready", timeout=15)

    main_menu = main.menu()

    main.set_focus()
    time.sleep(0.3)

    match opcion:
        case ListadoExistencias.FICHA_STOCK:
            main_menu.item(1).sub_menu().item(11).click_input()

            send_keys(TAB)
            send_keys(cod_desde + ENTER)
            send_keys(cod_hasta + ENTER)
            send_keys(fecha_desde + ENTER)
            send_keys(fecha_hasta + ENTER)
            send_keys(deposito_inicio + ENTER)
            send_keys(deposito_final)

        case ListadoExistencias.EXISTENCIA_STOCK:
            main_menu.item(1).sub_menu().item(11).click_input()

            send_keys(DOWN_ARR)
            send_keys(TAB)
            send_keys(cod_desde + ENTER)
            send_keys(cod_hasta + ENTER)
            send_keys(fecha_hasta + ENTER)
            send_keys(deposito_final + ENTER)
            send_keys(DOWN_ARR)

    if main.is_minimized():
        main.restore()
    main.set_focus()
    time.sleep(0.3)

    main.click_input(coords=COORDS_EXCEL_BTTN)
    send_keys("s")

    guardar_excel(opcion, cod_desde, cod_hasta, fecha_desde, fecha_hasta)
    cerrar_app(main)


def guardar_excel(
    opcion, cod_desde: str, cod_hasta: str, fecha_desde: str, fecha_hasta: str
):
    def limpiar(s: str):
        return s.replace(".", "-").replace("/", "-")

    formated_name = f"{opcion} {limpiar(cod_desde)} a {limpiar(cod_hasta)}___{limpiar(fecha_desde)} a {limpiar(fecha_hasta)}"

    ruta_xls = RUTA_ARCHIVOS / f"{formated_name}.xls"
    ruta_xlsx = RUTA_ARCHIVOS / f"{formated_name}.xlsx"

    ruta_xls.unlink(missing_ok=True)

    save = app.window(title="Crear Archivo de Excel")
    save.wait("ready", timeout=10000)
    edit = save.child_window(best_match="Archivo:Edit")
    edit.set_text(str(ruta_xls))

    save.set_focus()
    time.sleep(0.3)
    save.child_window(title="Aceptar", class_name="Button").click_input()

    df = pd.read_excel(ruta_xls)
    df.to_excel(ruta_xlsx, index=False, engine="openpyxl")
    ruta_xls.unlink()


def cerrar_app(main: pywinauto.WindowSpecification):
    try:
        main.close()
        app.wait_for_process_exit(timeout=10)
    except Exception:
        print("No se pudo cerrar el programa, intentando terminar el proceso...")
    finally:
        if app.is_process_running():
            app.kill(soft=False)


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
    parser.add_argument("--dep-inicio", required=True)
    parser.add_argument("--dep-final", required=True)
    parser.add_argument("--cod-desde", required=True)
    parser.add_argument("--cod-hasta", required=True)
    parser.add_argument("--fecha-desde", help="dd/mm/AAAA", default=TODAY)
    parser.add_argument("--fecha-hasta", help="dd/mm/AAAA", default=TODAY)

    parser.add_argument("--user", default="auditoria")
    parser.add_argument("--passwd", default="3801")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    iniciar_sesion(args.user, args.passwd)
    pestaña_principal(
        ListadoExistencias[args.opcion],
        args.dep_inicio,
        args.dep_final,
        args.cod_desde,
        args.cod_hasta,
        args.fecha_desde,
        args.fecha_hasta,
    )
