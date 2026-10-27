from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import get_settings


def ping_mongodb() -> str:
    """Confirma conectividad, credenciales y seleccion de base de datos.

    No modifica documentos ni imprime la URI o credenciales.
    """
    settings = get_settings()
    client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
    )
    try:
        client.admin.command("ping")
        return settings.mongodb_db
    finally:
        client.close()
