import numpy as np
import pandas as pd
from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from src.core.constants import (
    DROP_COLS_PARQUE,
    PAGE_LOGIN,
    PAGE_PARQUE_MOVIL,
    RENAME_CARROCERIA,
    RENAME_CHASIS,
    RENAME_CHASIS_MODELO,
    RENAME_COLS_PARQUE,
    RENAME_MARCA,
    RENAME_MOTOR,
    RENAME_MOTOR_MODELO,
    RENAME_TITULAR,
    TIPO_DATOS_PARQUE_MERGE,
    TIPOS_DATOS_PARQUE,
    TODAY,
)
from src.core.enums import ModoCargaEnum
from src.db.models.aseguradora_model import AseguradoraModel
from src.db.models.chasis_marca_model import ChasisMarcaModel
from src.db.models.chasis_modelo_model import ChasisModeloModel
from src.db.models.motor_marca_model import MotorMarcaModel
from src.db.models.motor_modelo_model import MotorModeloModel
from src.ingestion.scrapers.constants import (
    ASEGURADORA_COLS,
    CHASIS_COLS,
    CHASIS_FK_COLS,
    FECHAS_COLS,
    MOTOR_COLS,
    MOTOR_FK_COLS,
    NUMERIC_COLS,
    PARQUE_HISTORIAL_COLS,
    PASSWORD,
    PATH_PARQUE,
    URL_PARQUE,
    USUARIO,
    VIGENCIA_COLS,
)
from src.ingestion.scrapers.utils import _map_bool, _strip_and_replace
from src.repositories.aseguradora_repository import AseguradoraRepository
from src.repositories.chasis_repository import (
    ChasisMarcaRepository,
    ChasisModeloRepository,
)
from src.repositories.motor_repository import (
    MotorMarcaRepository,
    MotorModeloRepository,
)
from src.repositories.parque_movil_repository import (
    InternoVigenciaRepository,
    ParqueMovilHistorialRepository,
    ParqueMovilRepository,
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
        self.repo_interno_vigencia = InternoVigenciaRepository()

    def scrap(self):
        with sync_playwright() as playw:
            browser = playw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            context = browser.new_context(
                accept_downloads=True,
                viewport={"width": 1920, "height": 1080},
                locale="es-AR",
                timezone_id="America/Argentina/Buenos_Aires",
            )
            page = context.new_page()
            page.set_default_timeout(60000)

            # --- login ---
            page.goto(PAGE_LOGIN, wait_until="load")
            page.locator("#Username").fill(USUARIO)
            page.locator("#sa-password").fill(PASSWORD)
            page.get_by_role("button", name="Entrar").click()

            page.wait_for_load_state("load")

            with page.expect_navigation():
                page.get_by_role("button", name="Ingresar con San Antonio").click()
            page.wait_for_url("**/flota-web/**")

            page.goto(PAGE_PARQUE_MOVIL, wait_until="load")

            page.get_by_role("button", name="Buscar").click()

            try:
                page.locator("table.table tbody tr").first.wait_for(timeout=60000)
            except PWTimeout:
                raise

            with page.expect_download(timeout=180000) as parq:
                page.get_by_role("button", name="Descargar flota").click()

            PATH_PARQUE.parent.mkdir(parents=True, exist_ok=True)
            parq.value.save_as(PATH_PARQUE)

            self.guardar_parque(str(PATH_PARQUE))

            PATH_PARQUE.unlink(missing_ok=True)
            context.close()
            browser.close()

    def transformar_parque(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop(columns=DROP_COLS_PARQUE, errors="ignore")
        df = df.rename(columns=RENAME_COLS_PARQUE, errors="ignore")

        df["AireAcond"] = _map_bool(df["AireAcond"])
        df["Prendado"] = _map_bool(df["Prendado"])

        df = _strip_and_replace(df)

        df["Carroceria"] = df["Carroceria"].str.upper().replace(RENAME_CARROCERIA)

        df["ChasisMarca"] = df["ChasisMarca"].str.upper().replace(RENAME_MARCA)
        df["ChasisModelo"] = (
            df["ChasisModelo"].str.upper().replace(RENAME_CHASIS_MODELO)
        )

        df["MotorMarca"] = df["MotorMarca"].str.upper().replace(RENAME_MARCA)
        df["MotorModelo"] = df["MotorModelo"].str.upper().replace(RENAME_MOTOR_MODELO)

        fechas = [c for c, t in TIPOS_DATOS_PARQUE.items() if "datetime" in str(t)]

        for col in NUMERIC_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        for col in fechas:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

        df["Poliza"] = df["Poliza"].astype("Int32")
        df["CodCNRT"] = df["CodCNRT"].astype("Int32")

        df = df.astype(TIPOS_DATOS_PARQUE)
        df["Titular"] = df["Titular"].replace(RENAME_TITULAR)

        return df

    def create_vigencia(self, df_historial: pd.DataFrame) -> pd.DataFrame:
        df_historial = df_historial.sort_values(["Interno", "FechaHistorial"])

        cambio = df_historial["Dominio"].ne(
            df_historial.groupby("Interno")["Dominio"].shift()
        )
        df_historial["Tramo"] = cambio.cumsum()

        tramo = df_historial.groupby("Tramo").agg(
            Interno=("Interno", "first"),
            Dominio=("Dominio", "first"),
            FechaDesde=("FechaHistorial", "min"),
            Ultimo=("FechaHistorial", "max"),
            Patentado=("FechaPatentado", "min"),
        )
        sig = tramo.groupby("Interno")[["FechaDesde", "Patentado"]].shift(-1)

        hasta = tramo["Ultimo"] + pd.Timedelta(days=1)
        en_hueco = sig["Patentado"].gt(tramo["Ultimo"]) & sig["Patentado"].le(
            sig["FechaDesde"]
        )
        hasta = hasta.mask(en_hueco, sig["Patentado"])
        hasta = hasta.mask(tramo["Ultimo"].eq(df_historial["FechaHistorial"].max()))

        tramo["FechaHasta"] = hasta
        tramo["FechaPatentado"] = tramo["Patentado"]

        return tramo[VIGENCIA_COLS].reset_index(drop=True)

    def merge_and_create_aseguradora(
        self, df: pd.DataFrame, descartar=True
    ) -> pd.DataFrame:
        self.guardar_aseguradora(df[ASEGURADORA_COLS])
        df = self.repo_parque_movil.resolver_fk(
            self.session,
            df,
            AseguradoraModel,
            ASEGURADORA_COLS,
            descartar=descartar,
        )

        return df

    def merge_and_create_chasis(self, df: pd.DataFrame, descartar=True) -> pd.DataFrame:
        self.guardar_chasis(df[CHASIS_COLS])
        df = self.repo_parque_movil.resolver_fk(
            self.session,
            df,
            ChasisMarcaModel,
            ["ChasisMarca"],
            descartar=descartar,
        )

        df = self.repo_parque_movil.resolver_fk(
            self.session,
            df,
            ChasisModeloModel,
            CHASIS_FK_COLS,
            descartar=descartar,
        )

        df = df.rename(columns=RENAME_CHASIS)

        return df

    def merge_and_create_motor(self, df: pd.DataFrame, descartar=True) -> pd.DataFrame:
        self.guardar_motor(df[MOTOR_COLS])
        df = self.repo_parque_movil.resolver_fk(
            self.session,
            df,
            MotorMarcaModel,
            ["MotorMarca"],
            descartar=descartar,
        )

        df = self.repo_parque_movil.resolver_fk(
            self.session,
            df,
            MotorModeloModel,
            MOTOR_FK_COLS,
            descartar=descartar,
        )

        df = df.rename(columns=RENAME_MOTOR)

        return df

    def guardar_parque(self, ruta) -> None:
        df = pd.read_excel(ruta)
        df = self.transformar_parque(df)
        df = self.merge_and_create_aseguradora(df)
        df = self.merge_and_create_chasis(df)
        df = self.merge_and_create_motor(df)

        df = df.astype(TIPO_DATOS_PARQUE_MERGE)

        self.repo_parque_movil.load_df(
            self.session, df, ModoCargaEnum.UPSERT, claves=["Interno"]
        )

        df["FechaHistorial"] = TODAY
        self.repo_parque_movil_historial.load_df(
            self.session, df, ModoCargaEnum.UPSERT, PARQUE_HISTORIAL_COLS
        )

        self.guardar_interno_vigencia()

    def guardar_parque_historial_excel(self) -> None:
        df = pd.read_excel(URL_PARQUE)
        df = self.transformar_parque(df)
        df = self.merge_and_create_aseguradora(df, descartar=False)
        df = self.merge_and_create_chasis(df, descartar=False)
        df = self.merge_and_create_motor(df, descartar=False)

        df = df.astype(TIPO_DATOS_PARQUE_MERGE)

        self.repo_parque_movil_historial.load_df(
            self.session, df, ModoCargaEnum.UPSERT, PARQUE_HISTORIAL_COLS
        )

    def guardar_aseguradora(self, df: pd.DataFrame) -> None:
        df_copia = df.copy().drop_duplicates().dropna()
        df_copia = df_copia.sort_values(["Poliza"]).reset_index(drop=True)

        self.repo_aseguradora.load_df(
            self.session,
            df_copia,
            ModoCargaEnum.UPSERT,
            claves=ASEGURADORA_COLS,
        )

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

        self.repo_chasis_marca.load_df(
            self.session, df_marca, ModoCargaEnum.UPSERT, claves=["ChasisMarca"]
        )

        # --------- ChasisModelo ----------- DONE
        df_modelo = (
            df_copia.drop_duplicates()
            .dropna()
            .sort_values(by=["ChasisModelo"])
            .reset_index(drop=True)
        )

        df_modelo = self.repo_chasis_modelo.resolver_fk(
            self.session,
            df_modelo,
            ChasisMarcaModel,
            ["ChasisMarca"],
        )

        self.repo_chasis_modelo.load_df(
            self.session,
            df_modelo,
            ModoCargaEnum.UPSERT,
            claves=CHASIS_FK_COLS,
        )

    def guardar_motor(self, df: pd.DataFrame) -> None:
        df_copia: pd.DataFrame = df.copy()

        mask = df_copia["MotorModelo"] == "SIN MODELO"
        df_copia.loc[mask, MOTOR_COLS] = np.nan

        # --------- MotorMarca ----------- DONE
        df_marca = (
            df_copia[["MotorMarca"]]
            .drop_duplicates()
            .dropna()
            .sort_values(by=["MotorMarca"])
            .reset_index(drop=True)
        )

        self.repo_motor_marca.load_df(
            self.session,
            df_marca,
            ModoCargaEnum.UPSERT,
            claves=["MotorMarca"],
        )

        # --------- MotorModelo ----------- DONE
        df_modelo = (
            df_copia.drop_duplicates()
            .dropna()
            .sort_values(by=["MotorModelo"])
            .reset_index(drop=True)
        )

        df_modelo = self.repo_motor_modelo.resolver_fk(
            self.session,
            df_modelo,
            MotorMarcaModel,
            ["MotorMarca"],
        )

        self.repo_motor_modelo.load_df(
            self.session,
            df_modelo,
            ModoCargaEnum.UPSERT,
            claves=MOTOR_FK_COLS,
        )

    def guardar_interno_vigencia(self) -> None:
        df_historial = self.repo_parque_movil_historial.listar_internos_patentes(
            self.session
        )

        df_historial = df_historial[
            (df_historial["Interno"] > 0) & df_historial["Dominio"].notna()
        ]
        df_historial["FechaHistorial"] = pd.to_datetime(df_historial["FechaHistorial"])
        df_historial["FechaPatentado"] = pd.to_datetime(
            df_historial["FechaPatentado"], errors="coerce"
        )

        df = self.create_vigencia(df_historial)

        for col_fecha in FECHAS_COLS:
            df[col_fecha] = pd.to_datetime(
                df[col_fecha], errors="coerce", dayfirst=True
            ).dt.date

        self.repo_interno_vigencia.load_df(self.session, df, ModoCargaEnum.OVERWRITE)
