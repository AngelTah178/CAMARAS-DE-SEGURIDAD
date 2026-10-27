"""Funciones de contrasenas para Sprint 2.1 (Argon2id)."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("La contrasena debe tener al menos 12 caracteres.")
    if len(password.encode("utf-8")) > 1024:
        raise ValueError("La contrasena es demasiado larga.")
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
