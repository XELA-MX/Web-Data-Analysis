"""Primitivas de seguridad: hashing de contraseñas (argon2id) y tokens de sesión.

- Las contraseñas se hashean con argon2id (salt automático). Nunca se guardan en claro.
- El token de sesión se genera aleatorio y en la DB se guarda solo su SHA-256:
  si la DB se filtra, los tokens no son reutilizables.
"""

from __future__ import annotations

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

_ph = PasswordHasher()  # argon2id con parámetros por defecto (seguros)


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except Argon2Error:
        return False


def new_session_token() -> str:
    """Token opaco de 256 bits (el que viaja en la cookie httpOnly)."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """SHA-256 del token: lo que se guarda/consulta en la tabla sessions."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
