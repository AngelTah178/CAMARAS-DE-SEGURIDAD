"""Inicializacion idempotente de colecciones e indices.

Ejecutar desde backend: python -m app.database.setup
"""

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import get_settings
from app.database.schemas import SCHEMAS, INDEXES


def initialize_database():
    settings = get_settings()
    client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
    )
    try:
        db = client[settings.mongodb_db]
        existing = set(db.list_collection_names())

        # Si una coleccion ya existe, no sustituir su validador ni borrar datos.
        for name, schema in SCHEMAS.items():
            if name not in existing:
                db.create_collection(
                    name,
                    validator={"$jsonSchema": schema},
                    validationLevel="strict",
                    validationAction="error",
                )
                print(f"Creada coleccion: {name}")
            else:
                print(f"Conservada coleccion existente: {name}")

            for index in INDEXES[name]:
                db[name].create_index(
                    index["keys"],
                    name=index["name"],
                    unique=index.get("unique", False),
                )
                print(f"  Indice verificado: {index['name']}")

        print(f"Configuracion finalizada para {settings.mongodb_db}")
    finally:
        client.close()


if __name__ == "__main__":
    try:
        initialize_database()
    except (PyMongoError, ValueError) as exc:
        # No mostrar excepciones completas: pueden incluir informacion sensible.
        print(f"No se pudo inicializar MongoDB ({type(exc).__name__}).")
        raise SystemExit(1) from None
