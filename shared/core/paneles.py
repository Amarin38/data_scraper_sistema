from shared.core.enums import TipoUsuarioLoginEnum as Rol

_TODOS = frozenset(Rol)
_GESTION = frozenset({Rol.ADMIN, Rol.OWNER})

PANELES_ROLES: dict[str, frozenset[Rol]] = {
    "fijados": _TODOS,
    "importar": _TODOS,
    "criticos": _TODOS,
    "gasto": _TODOS,
}


def paneles_permitidos(rol: Rol) -> set[str]:
    return {pid for pid, roles in PANELES_ROLES.items() if rol in roles}
