import time
from pathlib import Path

import pandas as pd
from pywinauto import Application, win32api
from pywinauto.application import WindowSpecification
from pywinauto.keyboard import send_keys

from constants import (
    COORDS_EXCEL_BTTN,
    DOWN_ARR,
    ENTER,
    ENTER2,
    RUTA_ARCHIVOS,
    RUTA_PROGRAMA,
    TAB,
    TITULO_GUARDAR,
    TITULO_LOGIN,
    TITULO_PRINCIPAL,
    ListadoExistencias,
)


class Local:
    def __init__(self) -> None:
        self.app = Application(backend="win32").start(
            str(RUTA_PROGRAMA / "cargador.exe"), work_dir=str(RUTA_PROGRAMA)
        )
        self.main: None | WindowSpecification = None


    def posicion_pantalla(self):
        for i in range(10):
            time.sleep(2)
            print(win32api.GetCursorPos())


    def iniciar_sesion(self, user: str, passwd: str):
        inicio = self.app.window(title=TITULO_LOGIN)
        inicio.wait("ready", timeout=15)
        inicio.set_focus()
        time.sleep(0.5)

        send_keys(user + TAB)
        send_keys(passwd + ENTER2)


    def pestaña_principal(
        self,
        opcion: str,
        deposito_inicio: str,
        deposito_final: str,
        cod_desde: str,
        cod_hasta: str,
        fecha_desde: str,
        fecha_hasta: str,
        ruta_salida: Path,
    ):
        self.main = self.app.window(title_re=TITULO_PRINCIPAL)
        self.main.wait("ready", timeout=15)

        main_menu = self.main.menu()

        self.main.set_focus()
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

        if self.main.is_minimized():
            self.main.restore()
        self.main.set_focus()
        time.sleep(0.3)

        self.main.click_input(coords=COORDS_EXCEL_BTTN)
        send_keys("s")

        self.guardar_excel(opcion, cod_desde, cod_hasta, fecha_desde, fecha_hasta, ruta_salida)
        self.cerrar_app()

    def guardar_excel(
        self,
        opcion,
        cod_desde: str,
        cod_hasta: str,
        fecha_desde: str,
        fecha_hasta: str,
        ruta_salida: Path,
    ):
        def limpiar(s: str):
            return s.replace(".", "-").replace("/", "-")

        formated_name = f"{opcion} {limpiar(cod_desde)} a {limpiar(cod_hasta)}___{limpiar(fecha_desde)} a {limpiar(fecha_hasta)}"

        ruta_xls = RUTA_ARCHIVOS / f"{formated_name}.xls"
        ruta_xlsx = ruta_salida / f"{formated_name}.xlsx"

        ruta_xls.unlink(missing_ok=True)

        save = self.app.window(title=TITULO_GUARDAR)
        save.wait("ready", timeout=10000)
        edit = save.child_window(best_match="Archivo:Edit")
        edit.set_text(str(ruta_xls))

        save.set_focus()
        time.sleep(0.3)
        save.child_window(title="Aceptar", class_name="Button").click_input()

        df = pd.read_excel(ruta_xls)
        df.to_excel(ruta_xlsx, index=False, engine="openpyxl")
        ruta_xls.unlink()


    def cerrar_app(self):
        try:
            if self.main:
                self.main.close()
                self.app.wait_for_process_exit(timeout=10)
        except Exception:
            print("No se pudo cerrar el programa, intentando terminar el proceso...")
        finally:
            if self.app.is_process_running():
                self.app.kill(soft=False)
