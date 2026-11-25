import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

_hasher = PasswordHash.recommended()

SECRET_KEY = os.environ["JWT_SECRET"]
ALGORITMO = "HS256"
DURACION_HORAS = int(os.getenv("JWT_HORAS", "12"))

# hash de una contraseña inventada, para gastar el mismo tiempo cuando el usuario no existe
_HASH_FALSO = _hasher.hash("contraseña-inexistente")


def hashear(password: str) -> str:
    return _hasher.hash(password)


def verificar(password: str, hash_guardado: str | None) -> bool:
    # si el usuario no existe, se verifica contra un hash falso: mismo tiempo de respuesta
    return (
        _hasher.verify(password, hash_guardado or _HASH_FALSO)
        and hash_guardado is not None
    )


def crear_token(id_usuario: int, tipo: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_usuario),
        "tipo": tipo,
        "iat": ahora,
        "exp": ahora + timedelta(hours=DURACION_HORAS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITMO)


def leer_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
    except jwt.PyJWTError:
        return None
