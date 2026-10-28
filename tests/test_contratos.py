import csv
import io
import re
from datetime import date, timedelta

import pytest


def test_repuestos_paginado(api):
    r = api.get("/repuestos", params={"limit": 5, "page": 0})
    d = r.json()
    assert r.status_code == 200
    assert {"items", "total"} <= set(d)
    assert 0 < len(d["items"]) <= 5
    assert d["total"] >= len(d["items"])
    assert {"IDRepuesto", "Codigo", "Descripcion"} <= set(d["items"][0])


def test_repuestos_paginas_distintas(api):
    a = api.get("/repuestos", params={"limit": 5, "page": 0}).json()["items"]
    b = api.get("/repuestos", params={"limit": 5, "page": 1}).json()["items"]
    assert {x["IDRepuesto"] for x in a}.isdisjoint({x["IDRepuesto"] for x in b})


def test_repuestos_filtro_descripcion(api, repuesto):
    palabra = repuesto["Descripcion"].split()[0]
    total = api.get("/repuestos", params={"limit": 5, "page": 0}).json()["total"]
    d = api.get(
        "/repuestos", params={"descripcion": palabra, "limit": 50, "page": 0}
    ).json()
    assert 0 < d["total"] <= total
    assert all(palabra.lower() in x["Descripcion"].lower() for x in d["items"])


def test_repuestos_filtro_codigo(api, repuesto):
    total = api.get("/repuestos", params={"limit": 5, "page": 0}).json()["total"]
    d = api.get(
        "/repuestos", params={"codigo": repuesto["Codigo"], "limit": 50, "page": 0}
    ).json()
    assert 1 <= d["total"] < total


def test_repuestos_critico(api):
    d = api.get("/repuestos", params={"critico": True, "limit": 50, "page": 0}).json()
    if not d["items"]:
        pytest.skip("No hay repuestos críticos")
    assert all(x["Critico"] is True for x in d["items"])


def test_parametro_invalido_da_422(api):
    assert api.get("/repuestos", params={"limit": "abc"}).status_code == 422


def test_conjuntos(api):
    d = api.get("/repuestos/conjuntos").json()
    assert isinstance(d, list) and d and all(isinstance(x, str) for x in d)


def test_existencia_stock(api):
    d = api.get("/existencia-stock", params={"limit": 5, "page": 0}).json()
    assert {"items", "total"} <= set(d) and d["items"]
    assert {"Codigo", "Descripcion", "Stock"} <= set(d["items"][0])


@pytest.mark.parametrize(
    "ruta,pk",
    [
        ("/ficha-stock", "IDFichaStock"),
        ("/parque-movil/historiales", "IDParqueMovilHistorial"),
    ],
)
def test_cursor_avanza_sin_repetir(api, ruta, pk):
    d = api.get(ruta, params={"limit": 5}).json()
    assert len(d["items"]) == 5 and d["next_cursor"] is not None
    c = d["next_cursor"]
    r2 = api.get(
        ruta, params={"limit": 5, "cursor_valor": c["valor"], "cursor_id": c["id"]}
    )
    assert r2.status_code == 200
    assert r2.elapsed.total_seconds() < 1.0
    ids1 = {x[pk] for x in d["items"]}
    ids2 = {x[pk] for x in r2.json()["items"]}
    assert ids2 and ids1.isdisjoint(ids2)


def test_datos_rapidos(api):
    d = api.get("/inicio/datos-rapidos").json()
    assert {"mayor_stock", "crit_sin_exist", "importar"} <= set(d)
    assert len(d["mayor_stock"]) <= 10 and len(d["importar"]) <= 10
    cant = [float(x["Cantidad"]) for x in d["mayor_stock"]]
    assert cant == sorted(cant, reverse=True)
    assert all(float(x["Faltante"]) > 0 for x in d["importar"])
    assert all(float(x["Stock"] or 0) == 0 for x in d["crit_sin_exist"])


def test_previsiones_usa_consumo(api, repuesto_con_consumo):
    r = api.get(f"/estadisticas/previsiones/{repuesto_con_consumo}")
    assert r.status_code == 200
    filas = r.json()
    assert any(f["Tipo"] == "Consumo" for f in filas), (
        "Sin filas de consumo: ¿vista desactualizada?"
    )
    for f in filas:
        assert f["Tipo"] in {"Consumo", "Prevision"}
        assert re.fullmatch(r"\d{4}-\d{2}", f["Mes"])


def test_duracion(api, repuesto):
    d = api.get(f"/estadisticas/duracion-repuestos/{repuesto['IDRepuesto']}").json()
    assert {"Media", "Desvio", "N"} <= set(d)
    assert d["N"] >= 0


@pytest.mark.parametrize(
    "formato,tipo",
    [("csv", "text/csv"), ("json", "application/json"), ("xlsx", "spreadsheetml")],
)
def test_exportar_repuestos(api, repuesto, formato, tipo):
    r = api.get(
        "/repuestos/exportar", params={"formato": formato, "codigo": repuesto["Codigo"]}
    )
    assert r.status_code == 200
    assert tipo in r.headers["content-type"]
    assert f".{formato}" in r.headers["content-disposition"]
    if formato == "csv":
        lineas = r.text.strip().splitlines()
        assert "Codigo" in lineas[0] and len(lineas) >= 2
    elif formato == "json":
        assert isinstance(r.json(), list) and r.json()
    else:
        assert r.content[:2] == b"PK"


def test_exportar_parque_con_filtro(api):
    h = api.get("/parque-movil/historiales", params={"limit": 1}).json()["items"][0]
    if h["Interno"] is None:
        pytest.skip("El primer historial no tiene interno")
    r = api.get(
        "/parque-movil/exportar", params={"formato": "csv", "interno": h["Interno"]}
    )
    assert r.status_code == 200
    assert len(r.text.strip().splitlines()) >= 2


def test_cabeceras(api):
    d = api.get("/cabeceras").json()
    assert isinstance(d, list) and d and all(isinstance(x, str) for x in d)


def test_total_no_depende_de_limit_ni_page(api):
    a = api.get("/repuestos", params={"limit": 5, "page": 0}).json()["total"]
    b = api.get("/repuestos", params={"limit": 50, "page": 3}).json()["total"]
    assert a == b


def test_datos_rapidos_cacheado(api):
    a = api.get("/inicio/datos-rapidos")
    b = api.get("/inicio/datos-rapidos")
    assert a.json() == b.json()
    assert b.elapsed.total_seconds() < 0.25


def test_exportar_csv_usa_punto_y_coma_y_bom(api, repuesto):
    r = api.get(
        "/repuestos/exportar", params={"formato": "csv", "codigo": repuesto["Codigo"]}
    )
    assert r.content.startswith(b"\xef\xbb\xbf")
    assert ";" in r.content.decode("utf-8-sig").splitlines()[0]


def test_exportar_formato_invalido_da_422(api):
    assert api.get("/repuestos/exportar", params={"formato": "pdf"}).status_code == 422


def test_exportar_respeta_nombre(api, repuesto):
    r = api.get(
        "/repuestos/exportar",
        params={"formato": "csv", "nombre": "prueba", "codigo": repuesto["Codigo"]},
    )
    assert "prueba.csv" in r.headers["content-disposition"]


def test_exportar_repuestos_coincide_con_listado(api, repuesto):
    filtro = {"codigo": repuesto["Codigo"]}
    total = api.get("/repuestos", params={**filtro, "limit": 5, "page": 0}).json()[
        "total"
    ]
    r = api.get("/repuestos/exportar", params={**filtro, "formato": "json"})
    assert len(r.json()) == total


def test_exportar_existencia_coincide_con_listado(api):
    total = api.get("/existencia-stock", params={"limit": 1, "page": 0}).json()["total"]
    r = api.get("/existencia-stock/exportar", params={"formato": "csv"})
    assert r.status_code == 200
    filas = list(csv.reader(io.StringIO(r.content.decode("utf-8-sig")), delimiter=";"))
    assert len(filas) == total + 1  # + encabezado


def test_exportar_ficha_con_filtro(api, repuesto):
    desde = (date.today() - timedelta(days=365)).isoformat()
    r = api.get(
        "/ficha-stock/exportar",
        params={"formato": "csv", "codigo": repuesto["Codigo"], "fecha_desde": desde},
    )
    assert r.status_code == 200
    assert (
        len(r.content.decode("utf-8-sig").splitlines()) >= 1
    )  # al menos el encabezado


def test_ficha_por_codigo_es_rapido(api):
    # red de seguridad antes de borrar idx_ficha_repuesto_fecha
    top = api.get("/inicio/datos-rapidos").json()["mayor_stock"]
    codigo = top[0].get("Codigo") if top else None
    if not codigo:
        pytest.skip("mayor_stock no trae Codigo")
    params = {"codigo": codigo, "limit": 50}
    api.get("/ficha-stock", params=params)  # calienta el caché de Postgres
    r = api.get("/ficha-stock", params=params)
    assert r.status_code == 200
    assert r.elapsed.total_seconds() < 0.5


def test_duracion_supervivencia(api, repuesto):
    d = api.get(f"/estadisticas/duracion-repuestos/{repuesto['IDRepuesto']}").json()
    if not d["Curva"]:
        pytest.skip("El repuesto no tiene fallas registradas")
    ys = [p[1] for p in d["Curva"]]
    assert d["Curva"][0] == [0.0, 1.0]
    assert ys == sorted(ys, reverse=True)  # nunca sube
    assert d["Mediana"] is None or d["Mediana"] > 0
