"""Alta interactiva del administrador inicial.

Ejecutar una sola vez desde backend: python -m app.database.create_admin
No recibe contrasenas por argumentos o variables de entorno.
"""

from datetime import datetime, timezone
from getpass import getpass

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.core.config import get_settings
from app.core.security import hash_password, verify_password


def main() -> int:
    username = input("Usuario administrador (min. 3 caracteres): ").strip()
    if len(username) < 3 or len(username) > 64 or any(c.isspace() for c in username):
        print("Usuario invalido (3-64 caracteres, sin espacios).")
        return 1

    password = getpass("Contrasena (minimo 12 caracteres): ")
    confirm = getpass("Repetir contrasena: ")
    if password != confirm:
        print("Las contrasenas no coinciden.")
        return 1

    try:
        password_hash = hash_password(password)
    except ValueError as exc:
        print(str(exc))
        return 1
    if not verify_password(password, password_hash):
        print("Fallo la verificacion local del hash.")
        return 1
    password = None
    confirm = None

    settings = get_settings()
    client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
    )
    try:
        users = client[settings.mongodb_db]["usuarios"]
        if users.find_one({}, {"_id": 1}) is not None:
            print("Ya existe al menos un usuario. No se permite otra alta inicial.")
            return 1
        result = users.insert_one({
            "usuario": username,
            "passwordHash": password_hash,
            "rol": "administrador",
            "activo": True,
            "creadoEn": datetime.now(timezone.utc),
        })
        saved = users.find_one({"_id": result.inserted_id})
        if not saved or saved["passwordHash"] != password_hash:
            print("La verificacion del registro fallo.")
            return 1
        print("Administrador registrado correctamente. Hash Argon2id verificado.")
        print("Nunca compartas la contrasena ni el hash.")
        return 0
    except (PyMongoError, ValueError):
        print("No se pudo crear o verificar el administrador. Revisa MongoDB Atlas.")
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
