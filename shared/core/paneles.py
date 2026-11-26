PANELES_ROLES: dict[str, frozenset[str]] = {
    "fijados": frozenset({"admin", "compras"}),
    "importar": frozenset({"admin"}),
    "criticos": frozenset({"admin", "compras"}),
    "gasto": frozenset({"admin"}),
}


def paneles_permitidos(rol: str) -> set[str]:
    return {pid for pid, roles in PANELES_ROLES.items() if rol in roles}
