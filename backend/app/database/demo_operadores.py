"""Sprint 1.4: demostracion aislada de cuatro operadores MongoDB.

Ejecutar desde backend: python -m app.database.demo_operadores
No modifica colecciones operativas; crea y elimina una coleccion temporal de QA.
"""

from datetime import datetime, timezone
from uuid import uuid4

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import get_settings


def ejecutar_demo():
    settings = get_settings()
    client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
    )
    nombre = f"_qa_operadores_{uuid4().hex}"
    try:
        db = client[settings.mongodb_db]
        coleccion = db.create_collection(nombre)
        try:
            producto_id = coleccion.insert_one({
                "sku": "QA-CAM-001",
                "nombre": "Camara IP QA",
                "categoria": "Camaras IP",
                "precio": 1000,
                "stock": 10,
                "etiquetas": ["IP"],
                "historialCambios": [],
                "creadoEn": datetime.now(timezone.utc),
            }).inserted_id

            # $set: actualizar un campo.
            resultado = coleccion.update_one(
                {"_id": producto_id}, {"$set": {"precio": 1250}}
            )
            assert resultado.modified_count == 1
            assert coleccion.find_one({"_id": producto_id})["precio"] == 1250
            print("OK $set: precio actualizado a 1250")

            # $inc: incrementar existencias.
            resultado = coleccion.update_one(
                {"_id": producto_id}, {"$inc": {"stock": 5}}
            )
            assert resultado.modified_count == 1
            assert coleccion.find_one({"_id": producto_id})["stock"] == 15
            print("OK $inc: stock actualizado a 15")

            # $push: agregar un subdocumento al historial.
            resultado = coleccion.update_one(
                {"_id": producto_id}, {"$push": {"historialCambios": {
                    "accion": "ajuste_qa",
                    "cantidad": 5,
                    "fecha": datetime.now(timezone.utc),
                }}}
            )
            assert resultado.modified_count == 1
            assert len(coleccion.find_one(
                {"_id": producto_id})["historialCambios"]) == 1
            print("OK $push: evento agregado al historial")

            # $in: filtrar productos por categorias permitidas.
            encontrados = list(coleccion.find(
                {"categoria": {"$in": ["Camaras IP", "NVR"]}},
                {"sku": 1, "categoria": 1},
            ))
            assert len(encontrados) == 1
            assert encontrados[0]["sku"] == "QA-CAM-001"
            print("OK $in: producto encontrado por categoria")

            print("QA operadores: 4/4 APROBADOS")
        finally:
            db.drop_collection(nombre)
            print("Coleccion temporal de QA eliminada.")
    finally:
        client.close()


if __name__ == "__main__":
    try:
        ejecutar_demo()
    except (PyMongoError, AssertionError, ValueError) as exc:
        # No imprimir excepciones completas: pueden exponer datos de conexion.
        print(f"QA operadores FALLIDO: {type(exc).__name__}")
        raise SystemExit(1) from None
