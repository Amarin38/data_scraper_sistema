"""Reglas de dependencias entre los paquetes de src/ (se verifican en cada deploy).

Capas: core <- db <- repositories <- ingestion / compute / api.
"""

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "src"

# paquete -> paquetes de src de los que PUEDE importar (además de sí mismo)
PERMITIDO = {
    "core": set(),
    "db": {"core"},
    "repositories": {"core", "db"},
    "ingestion": {"core", "db", "repositories"},
    "compute": {"core", "db", "repositories"},
    # compute: previsión exploratoria (acople temporal hasta decidir su destino)
    "api": {"core", "db", "repositories", "compute"},
}
# archivos sueltos de la raíz de src y a qué paquete se asimilan
RAIZ_SUELTOS = {"crear_usuario": "api", "__init__": None}


def _paquete_de(ruta: Path) -> str | None:
    partes = ruta.relative_to(RAIZ).parts
    if len(partes) == 1:
        nombre = ruta.stem
        assert nombre in RAIZ_SUELTOS, (
            f"src/{ruta.name}: archivo suelto sin regla; agregalo a RAIZ_SUELTOS"
        )
        return RAIZ_SUELTOS[nombre]
    assert partes[0] in PERMITIDO, (
        f"src/{partes[0]}/: paquete nuevo sin regla; agregalo a PERMITIDO"
    )
    return partes[0]


def _paquetes_importados(ruta: Path) -> set[str]:
    """Paquetes de primer nivel de src que importa el archivo (absolutos o relativos)."""
    partes = ruta.relative_to(RAIZ.parent).with_suffix("").parts
    paquete = list(
        partes[:-1]
    )  # paquete que contiene al archivo (vale también para __init__)
    encontrados: set[str] = set()
    for nodo in ast.walk(ast.parse(ruta.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                trozos = alias.name.split(".")
                if trozos[0] == "src" and len(trozos) > 1:
                    encontrados.add(trozos[1])
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.level:
                base = paquete[: len(paquete) - (nodo.level - 1)]
                trozos = base + (nodo.module.split(".") if nodo.module else [])
            else:
                trozos = (nodo.module or "").split(".")
            if not trozos or trozos[0] != "src":
                continue
            if len(trozos) > 1:
                encontrados.add(trozos[1])
            else:  # from src import algo
                encontrados.update(a.name for a in nodo.names)
    return encontrados


def test_dependencias_entre_paquetes():
    violaciones = []
    for ruta in sorted(RAIZ.rglob("*.py")):
        if "__pycache__" in ruta.parts:
            continue
        propio = _paquete_de(ruta)
        if propio is None:
            continue
        for destino in sorted(_paquetes_importados(ruta) - {propio}):
            if destino not in PERMITIDO[propio]:
                violaciones.append(
                    f"{ruta.relative_to(RAIZ)}: {propio} no puede importar {destino}"
                )
    assert not violaciones, "\n" + "\n".join(violaciones)
