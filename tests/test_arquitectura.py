"""Reglas de dependencias entre capas (se verifican en cada deploy).

Paquetes: shared (core, db, repositories), pipeline (ingestion, compute), legacy_api.
Capas:    core <- db <- repositories <- ingestion / compute / api
"""

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# carpeta de primer nivel -> cómo se nombra la capa de cada subpaquete
CARPETAS = {
    "shared": {"core", "db", "repositories"},
    "pipeline": {"ingestion", "compute"},
}
CARPETA_API = "legacy_api"  # toda la carpeta es la capa "api"
SUELTOS = {"crear_usuario.py": "api"}  # archivos de la raíz y su capa

# capa -> capas de las que PUEDE importar (además de sí misma)
PERMITIDO = {
    "core": set(),
    "db": {"core"},
    "repositories": {"core", "db"},
    "ingestion": {"core", "db", "repositories"},
    "compute": {"core", "db", "repositories"},
    # compute: previsión exploratoria (acople temporal hasta decidir su destino)
    "api": {"core", "db", "repositories", "compute"},
}


def _capa_de_archivo(ruta: Path) -> str:
    partes = ruta.relative_to(RAIZ).parts
    if len(partes) == 1:
        assert partes[0] in SUELTOS, f"{partes[0]}: archivo suelto sin regla (SUELTOS)"
        return SUELTOS[partes[0]]
    if partes[0] == CARPETA_API:
        return "api"
    if len(partes) == 2:  # p. ej. shared/__init__.py
        return ""
    assert partes[1] in CARPETAS[partes[0]], (
        f"{partes[0]}/{partes[1]}: subpaquete sin regla (CARPETAS)"
    )
    return partes[1]


def _capa_de_modulo(trozos: list[str], nombres: list[str]) -> set[str]:
    """Capas a las que apunta un import ya resuelto a trozos absolutos."""
    if not trozos:
        return set()
    if trozos[0] == "src":
        return {"src (ruta vieja)"}
    if trozos[0] == CARPETA_API:
        return {"api"}
    if trozos[0] in CARPETAS:
        if len(trozos) > 1:
            return {trozos[1]}
        return set(nombres)  # from shared import core
    if trozos[0] == "crear_usuario":
        return {"api"}
    return set()


def _capas_importadas(ruta: Path) -> set[str]:
    partes = ruta.relative_to(RAIZ).with_suffix("").parts
    paquete = list(partes[:-1])
    encontradas: set[str] = set()
    for nodo in ast.walk(ast.parse(ruta.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                encontradas |= _capa_de_modulo(alias.name.split("."), [])
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.level:
                base = paquete[: len(paquete) - (nodo.level - 1)]
                trozos = base + (nodo.module.split(".") if nodo.module else [])
            else:
                trozos = (nodo.module or "").split(".")
            encontradas |= _capa_de_modulo(trozos, [a.name for a in nodo.names])
    return encontradas


def _archivos():
    for carpeta in [*CARPETAS, CARPETA_API]:
        for ruta in sorted((RAIZ / carpeta).rglob("*.py")):
            if "__pycache__" not in ruta.parts:
                yield ruta
    for nombre in SUELTOS:
        yield RAIZ / nombre


def test_dependencias_entre_capas():
    violaciones = []
    for ruta in _archivos():
        propia = _capa_de_archivo(ruta)
        if not propia:
            continue
        for destino in sorted(_capas_importadas(ruta) - {propia}):
            if destino not in PERMITIDO[propia]:
                violaciones.append(
                    f"{ruta.relative_to(RAIZ)}: {propia} no puede importar {destino}"
                )
    assert not violaciones, "\n" + "\n".join(violaciones)
