from playwright.sync_api import sync_playwright

from constants import (
    PAGE_LOGIN,
    PAGE_PARQUE_MOVIL,
    RUTA_PARQUE,
    RUTA_PARQUE_HISTORIAL,
    TODAY,
)


def scrap_web():
    with sync_playwright() as playw:
        browser = playw.chromium.launch(headless=True, slow_mo=300)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # --- Login ---
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
        page.locator("#body_grd_parque_movil tbody tr td").first.wait_for(timeout=30000)

        # --- Descarga ---
        fecha_fmt = TODAY.replace("/", "-")

        with page.expect_download(timeout=120000) as parq:
            page.click("#body_btn_descargar_excel")

        download_parq = parq.value
        download_parq.save_as(RUTA_PARQUE / f"parque_movil_{fecha_fmt}.xlsx")

        with page.expect_download(timeout=120000) as hist:
            page.click("#body_btn_descargar_excel_historia")

        download_hist = hist.value
        download_hist.save_as(
            RUTA_PARQUE_HISTORIAL / f"historial_parque_movil_{fecha_fmt}.xlsx"
        )

        context.close()
        browser.close()
