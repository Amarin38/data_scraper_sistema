import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from repositories.parque_movil_historial_repository import (
    ParqueMovilHistorialRepository,
)
from repositories.parque_movil_repository import ParqueMovilRepository
from src.core.constants import (
    PAGE_LOGIN,
    PAGE_PARQUE_MOVIL,
    RENAME_COLS_PARQUE,
    RENAME_TITULAR,
    SI_NO,
    TIPOS_DATOS_PARQUE,
    TODAY,
)
from src.db.models.aseguradora_model import AseguradoraModel
from src.db.models.chasis_marca_model import ChasisMarcaModel
from src.db.models.chasis_modelo_model import ChasisModeloModel
from src.db.models.motor_marca_model import MotorMarcaModel
from src.db.models.motor_modelo_model import MotorModeloModel
from src.repositories.aseguradora_repository import AseguradoraRepository
from src.repositories.chasis_repository import (
    ChasisMarcaRepository,
    ChasisModeloRepository,
)
from src.repositories.motor_repository import (
    MotorMarcaRepository,
    MotorModeloRepository,
)


class Web:
    def __init__(self, session: Session):
        self.session = session
        self.repo_parque_movil = ParqueMovilRepository()
        self.repo_parque_movil_historial = ParqueMovilHistorialRepository()
        self.repo_aseguradora = AseguradoraRepository()
        self.repo_chasis_marca = ChasisMarcaRepository()
        self.repo_chasis_modelo = ChasisModeloRepository()
        self.repo_motor_marca = MotorMarcaRepository()
        self.repo_motor_modelo = MotorModeloRepository()

    def scrap(self):
        with sync_playwright() as playw:
            browser = playw.chromium.launch(headless=True, slow_mo=300)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            page.goto(PAGE_LOGIN)
            page.locator("#body_txt_usuario").fill("sergiop.dota@gmail.com")
            page.locator("#body_txt_pass").fill("123*")

            with page.expect_navigation(wait_until="load", timeout=30000):
                page.locator("#body_txt_pass").press("Enter")

            if "login" in page.url.lower():
                page.screenshot(path="login_fallido.png")
                raise RuntimeError("El login no pasó — seguimos en login.aspx")

            page.goto(PAGE_PARQUE_MOVIL, wait_until="domcontentloaded")

            page.locator("#body_btn_filtrar").click()
            page.locator("#body_grd_parque_movil tbody tr td").first.wait_for(
                timeout=30000
            )

            with page.expect_download(timeout=120000) as parq:
                page.click("#body_btn_descargar_excel")

            path_parque = parq.value.path()

            self.guardar_parque(path_parque)

            context.close()
            browser.close()

    def guardar_parque(self, ruta) -> None:
        df = pd.read_excel(ruta, dtype=str)
        df = df.drop(
            columns=[
                "Motor Nro. por cambio",
                "Comprobante",
                "Inicio",
                "Fin",
                "Oferta Libre",
                "Proveedor",
            ]
        )
        df = df.rename(columns=RENAME_COLS_PARQUE)

        df["AireAcond"] = self._map_bool(df["AireAcond"])
        df["Prendado"] = self._map_bool(df["Prendado"])

        df = self._strip_and_replace(df)

        df["ChasisMarca"] = df["ChasisMarca"].replace({"M.BENZ": "MERCEDES BENZ"})
        df["ChasisModelo"] = df["ChasisModelo"].replace(
            {
                "19-L914": "L914",
                "029-K280 B4X2 / TORINO": "K280 B4X2",
                "671-K280 B4X2": "K280 B4X2",
                "K280B": "K280 B4X2",
                "719-CONSTELATION": "CONSTELLATION",
            }
        )

        df["MotorMarca"] = df["MotorMarca"].replace({"MBENZ": "MERCEDES BENZ"})
        df["MotorModelo"] = df["MotorModelo"].replace(
            {
                "MWM 4 CIL": "4 CIL",
                "CUMMINS 4 CIL": "4 CIL",
                "CUMMINS 6 CIL": "6 CIL",
                "SCANNIA 6 CIL": "6 CIL",
                "DC 09 142 280CV": "K280 B4X2",
                "671-K280 B4X2": "K280 B4X2",
                "029-K280 B4X2 / TORINO": "K280 B4X2",
                "MBENZ": "MERCEDES BENZ",
                "MWM MAXFOR 4 CIL": "MAXXFORCE 4 CIL",
                "MWM MAXFOR 6 CIL": "MAXXFORCE 6 CIL",
            }
        )

        df = df.astype(TIPOS_DATOS_PARQUE)
        df["Titular"] = df["Titular"].replace(RENAME_TITULAR)

        # --------------- ASEGURADORA ------------------- DONE
        # Guardo las aseguradoras en la db
        self.guardar_aseguradora(df[["Aseguradora", "Poliza"]])

        df = self.repo_parque_movil.resolver_fk(  # Hago merge en la tabla principal de parque movil
            self.session, df, AseguradoraModel, ["Aseguradora", "Poliza"]
        )

        # --------------- CHASIS ------------------- DONE
        # Guardo los chasis en la db
        self.guardar_chasis(df[["ChasisMarca", "ChasisModelo"]])

        df = self.repo_parque_movil.resolver_fk(  # Hago el 1er merge en la tabla principal de parque movil
            self.session, df, ChasisMarcaModel, ["ChasisMarca"]
        )

        df = self.repo_parque_movil.resolver_fk(  # Hago el 2do merge en la tabla principal de parque movil
            self.session, df, ChasisModeloModel, ["IDChasisMarca", "ChasisModelo"]
        )

        df = df.rename(columns={"IDChasisModelo": "IDChasis"})

        # --------------- MOTOR ------------------- DONE
        self.guardar_motor(df[["MotorMarca", "MotorModelo"]])

        df = self.repo_parque_movil.resolver_fk(  # Hago el 1er merge en la tabla principal de parque movil
            self.session, df, MotorMarcaModel, ["MotorMarca"]
        )

        df = self.repo_parque_movil.resolver_fk(  # Hago el 2do merge en la tabla principal de parque movil
            self.session, df, MotorModeloModel, ["IDMotorMarca", "MotorModelo"]
        )

        df = df.rename(columns={"IDMotorModelo": "IDMotor"})

        self.repo_parque_movil.load_df_with_overwrite(df, self.session)

        df["FechaHistorial"] = TODAY
        self.repo_parque_movil_historial.load_df_with_overwrite(df, self.session)

    def guardar_aseguradora(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copia = df.copy().drop_duplicates().dropna()
        df_copia = df_copia.sort_values(["Poliza"]).reset_index(drop=True)

        self.repo_aseguradora.load_df_with_overwrite(df_copia, self.session)
        return df_copia

    def guardar_chasis(self, df: pd.DataFrame) -> None:
        df_copia: pd.DataFrame = df.copy()

        # --------- ChasisMarca ----------- DONE
        df_marca = (
            df_copia[["ChasisMarca"]]
            .drop_duplicates()
            .dropna()
            .sort_values(by=["ChasisMarca"])
            .reset_index(drop=True)
        )

        self.repo_chasis_marca.load_df_with_overwrite(df_marca, self.session)

        # --------- ChasisModelo ----------- DONE
        df_modelo = (
            df_copia.drop_duplicates()
            .dropna()
            .sort_values(by=["ChasisModelo"])
            .reset_index(drop=True)
        )

        df_modelo = self.repo_chasis_modelo.resolver_fk(
            self.session, df_modelo, ChasisMarcaModel, ["ChasisMarca"]
        )

        self.repo_chasis_modelo.load_df_with_overwrite(df_modelo, self.session)

    def guardar_motor(self, df: pd.DataFrame) -> None:
        df_copia: pd.DataFrame = df.copy()

        mask = df_copia["MotorModelo"] == "SIN MODELO"
        df_copia.loc[mask, ["MotorMarca", "MotorModelo"]] = np.nan

        # --------- MotorMarca ----------- DONE
        df_marca = (
            df_copia[["MotorMarca"]]
            .drop_duplicates()
            .dropna()
            .sort_values(by=["MotorMarca"])
            .reset_index(drop=True)
        )

        self.repo_motor_marca.load_df_with_overwrite(df_marca, self.session)

        # --------- MotorModelo ----------- DONE
        df_modelo = (
            df_copia.drop_duplicates()
            .dropna()
            .sort_values(by=["MotorModelo"])
            .reset_index(drop=True)
        )

        df_modelo = self.repo_motor_modelo.resolver_fk(
            self.session, df_modelo, MotorMarcaModel, ["MotorMarca"]
        )

        self.repo_motor_modelo.load_df_with_overwrite(df_modelo, self.session)

    def _map_bool(self, df) -> pd.DataFrame:
        return df.str.strip().str.lower().map(SI_NO)

    def _strip_and_replace(self, df: pd.DataFrame) -> pd.DataFrame:
        obj_cols = df.select_dtypes(["object", "string"]).columns
        df[obj_cols] = df[obj_cols].apply(lambda s: s.str.strip())

        no_bool = df.columns.difference(df.select_dtypes("bool").columns)
        df[no_bool] = df[no_bool].replace([0, 0.0, "N/A", "0", "", "-"], np.nan)

        return df

    def _limpiar_vacio(self, df) -> pd.DataFrame:
        return df.str.strip().replace([0, 0.0, "N/A", "0", "", "-"], np.nan)
