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
    RENAME_COLS_PARQUE_HISTORIAL,
    RENAME_TITULAR,
    SI_NO,
    TIPOS_DATOS_PARQUE,
    TIPOS_DATOS_PARQUE_HIST,
)
from src.db.models.aseguradora_model import AseguradoraModel
from src.db.models.chasis_marca_model import ChasisMarcaModel
from src.db.models.chasis_modelo_model import ChasisModeloModel
from src.repositories.aseguradora_repository import AseguradoraRepository
from src.repositories.chasis_repository import (
    ChasisMarcaRepository,
    ChasisModeloRepository,
)


class Web:
    def __init__(self, session: Session):
        self.session = session
        self.repo_parque_movil = ParqueMovilRepository()
        self.repo_aseguradora = AseguradoraRepository()
        self.repo_chasis_marca = ChasisMarcaRepository()
        self.repo_chasis_modelo = ChasisModeloRepository()

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

            self.guardar_parque(parq.value.path())

            with page.expect_download(timeout=120000) as hist:
                page.click("#body_btn_descargar_excel_historia")

            self.guardar_parque_historial(hist.value.path())

            context.close()
            browser.close()

    def guardar_parque(self, ruta) -> None:
        df = pd.read_excel(ruta, dtype=str)
        df = df.drop(columns=["Motor Nro. por cambio"])
        df = df.rename(columns=RENAME_COLS_PARQUE)

        df["AireAcond"] = self._map_bool(df["AireAcond"])
        df["Prendado"] = self._map_bool(df["Prendado"])
        df["OfertaLibre"] = self._map_bool(df["OfertaLibre"])

        df = df.astype(TIPOS_DATOS_PARQUE)
        df["Titular"] = self._limpiar_vacio(df["Titular"])
        df["Titular"] = df["Titular"].replace(RENAME_TITULAR)

        df["EstadoHabilitacion"] = self._limpiar_vacio(df["EstadoHabilitacion"])

        # --------------- ASEGURADORA ------------------- DONE
        self.guardar_aseguradora(df[["Aseguradora", "Poliza"]]) # Guardo las asegurdadoras en la db

        df = self.repo_parque_movil.resolver_fk( # Hago merge en la tabla principal de parque movil
            self.session, df, AseguradoraModel, ["Aseguradora", "Poliza"]
        )

        # --------------- CHASIS ------------------- DONE
        self.guardar_chasis(df[["ChasisMarca", "ChasisModelo"]]) # Guardo los chasis en la db

        df = self.repo_parque_movil.resolver_fk( # Hago el 1er merge en la tabla principal de parque movil
            self.session, df, ChasisMarcaModel, ["ChasisMarca"]
        )

        df = self.repo_parque_movil.resolver_fk( # Hago el 2do merge en la tabla principal de parque movil
            self.session, df, ChasisModeloModel, ["IDChasisMarca", "ChasisModelo"]
        )

        df = df.rename(columns={"IDChasisModelo":"IDChasis"})

        # --------------- MOTOR ------------------- TODO

        self.guardar_motor(df[["MotorMarca", "MotorModelo"]])

        # self.repo_parque_movil.load_df_with_overwrite(df, self.session)

    def guardar_parque_historial(self, ruta) -> None:
        df = pd.read_excel(ruta, dtype=str)
        df = df.rename(columns=RENAME_COLS_PARQUE_HISTORIAL)

        df["Prendado"] = self.map_bool(df["Prendado"])
        df["OfertaLibre"] = self.map_bool(df["OfertaLibre"])

        df = df.astype(TIPOS_DATOS_PARQUE_HIST)

        df["Titular"] = df["Titular"].str.strip()
        df["Titular"] = df["Titular"].replace(RENAME_TITULAR)

        df["EstadoHabilitacion"] = (
            df["EstadoHabilitacion"].str.strip().replace("", np.nan)
        )

        # ParqueMovilHistorialRepository().load_df_with_overwrite(df, self.session)

    def guardar_aseguradora(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copia = df.copy().drop_duplicates().dropna()
        df_copia = (
            df_copia.sort_values(["NumPoliza"]).reset_index().drop("index", axis=1)
        )

        self.repo_aseguradora.load_df_with_overwrite(df_copia, self.session)
        return df_copia

    def guardar_chasis(self, df: pd.DataFrame) -> None:
        df_copia: pd.DataFrame = self._strip_strings(df.copy())

        # --------- ChasisMarca ----------- DONE
        df_marca = (
            df_copia[["ChasisMarca"]]
            .drop_duplicates()
            .dropna()
            .sort_values(by=["ChasisMarca"])
            .reset_index(drop=True)
            .replace({"M.BENZ": "MERCEDES BENZ"})
        )

        self.repo_chasis_marca.load_df_with_overwrite(df_marca, self.session)

        # --------- ChasisModelo ----------- DONE
        df_modelo = (
            df_copia
            .drop_duplicates()
            .dropna()
            .sort_values(by=["ChasisModelo"])
            .reset_index(drop=True)
        )

        df_modelo = self.repo_chasis_modelo.resolver_fk(
            self.session, df_modelo, ChasisMarcaModel, ["ChasisMarca"]
        )

        self.repo_chasis_modelo.load_df_with_overwrite(df_modelo, self.session)

    def guardar_motor(self, df: pd.DataFrame) -> None:
        # --------- MotorMarca ----------- TODO

        # --------- MotorModelo ----------- TODO

        ...


    def _map_bool(self, df) -> pd.DataFrame:
        return df.str.strip().str.lower().map(SI_NO)

    def _strip_strings(self, df: pd.DataFrame):
        for col in df.columns:
            df[col] = df[col].str.strip()
        return df

    def _limpiar_vacio(self, col) -> pd.DataFrame:
        return (col
            .str.strip()
            .replace(0, np.nan)
            .replace("0", np.nan)
            .replace("", np.nan)
            .replace(0.0, np.nan)
            .replace("-", np.nan)
        )
