import csv
import io
import json
import os
import re
import tempfile
from enum import Enum

from fastapi import HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from sqlalchemy import func, literal, select
from starlette.background import BackgroundTask

from src.db.session import SessionLocal  # ajustá al nombre que exporte tu session.py

LOTE = 5000
MAX_FILAS_XLSX = 1_000_000  # Excel admite 1.048.576 por hoja
MIME = {
    "csv": "text/csv; charset=utf-8",
    "json": "application/json",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def limpiar_nombre(nombre):
    return re.sub(r"[^A-Za-z0-9_.\- ]", "", nombre or "").strip()[:80]


def iterar_filas(stmt, lote=LOTE):
    """Lee la consulta de a lotes, con una sesión propia que sigue abierta durante la descarga."""
    db = SessionLocal()
    resultado = None
    try:
        resultado = db.execute(stmt.execution_options(yield_per=lote)).mappings()
        yield from resultado
    finally:
        if resultado is not None:
            resultado.close()
        db.rollback()
        db.close()


def _validar_limite_xlsx(stmt):
    tope = (
        select(literal(1))
        .select_from(stmt.order_by(None).subquery())
        .limit(MAX_FILAS_XLSX + 1)
    )
    with SessionLocal() as db:
        n = db.execute(select(func.count()).select_from(tope.subquery())).scalar_one()
    if n > MAX_FILAS_XLSX:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Excel admite hasta {MAX_FILAS_XLSX:,} filas".replace(",", ".")
                + " y esta exportación las supera. Usá CSV o JSON, o agregá filtros."
            ),
        )


def _celda(v):
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, str):
        return ILLEGAL_CHARACTERS_RE.sub("", v)
    return v


def _json_default(o):
    return o.value if isinstance(o, Enum) else str(o)


def _csv_stream(filas, columnas):
    buf = io.StringIO()
    buf.write("\ufeff")
    w = csv.writer(buf, delimiter=";")
    w.writerow(columnas)
    n = 0
    for f in filas:
        w.writerow([_celda(f[c]) for c in columnas])
        n += 1
        if n % LOTE == 0:
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)
    yield buf.getvalue()


def _json_stream(filas, columnas):
    yield "["
    lote, primero = [], True
    for f in filas:
        s = json.dumps(
            {c: f[c] for c in columnas}, ensure_ascii=False, default=_json_default
        )
        lote.append(s if primero else "," + s)
        primero = False
        if len(lote) >= LOTE:
            yield "".join(lote)
            lote = []
    yield "".join(lote) + "]"


def _xlsx_a_archivo(filas, columnas):
    wb = Workbook(write_only=True)
    ws = wb.create_sheet("Datos")
    ws.append(columnas)
    for n, f in enumerate(filas, start=1):
        if n > MAX_FILAS_XLSX:
            raise HTTPException(
                status_code=400,
                detail="La exportación superó el límite de Excel. Usá CSV o JSON.",
            )
        ws.append([_celda(f[c]) for c in columnas])
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    tmp.close()
    wb.save(tmp.name)
    return tmp.name


def _aplicar(filas, fn):
    try:
        for f in filas:
            yield fn(f)
    finally:
        filas.close()


def exportacion(
    stmt, columnas, formato, nombre, transformar=None, extra=None, validar=False
):
    """`stmt` es la consulta (un Select), no filas ya cargadas."""
    formato = getattr(formato, "value", formato)
    if formato == "xlsx":
        _validar_limite_xlsx(stmt)
    if validar:
        return {"ok": True}

    filas = iterar_filas(stmt)

    if transformar:
        filas = _aplicar(filas, transformar)

    if formato == "xlsx":
        ruta = _xlsx_a_archivo(filas, columnas)
        return FileResponse(
            ruta,
            media_type=MIME["xlsx"],
            filename=f"{nombre}.xlsx",
            background=BackgroundTask(os.remove, ruta),
        )

    gen = (
        _csv_stream(filas, columnas)
        if formato == "csv"
        else _json_stream(filas, columnas)
    )
    return StreamingResponse(
        gen,
        media_type=MIME[formato],
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}.{formato}"',
            "X-Accel-Buffering": "no",
            **(extra or {}),
        },
    )
