"""Sprint 4.1: movimientos de entrada y salida.

El cambio de stock y su evento embebido son atómicos en el producto.
La copia en 'movimientos' es una segunda escritura: en Atlas M0 no
se asume una transacción multidocumento.
"""
from datetime import datetime, timezone
from typing import Literal

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError

from app.core.auth_dependencies import require_admin
from app.core.config import get_settings

router = APIRouter(prefix="/api/movimientos", tags=["Movimientos"])


class MovimientoNuevo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    productoId: str
    tipo: Literal["entrada", "salida"]
    cantidad: int = Field(gt=0)
    motivo: str = Field(min_length=3, max_length=300)


def as_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=400, detail="ID de producto inválido.")
    return ObjectId(value)


def serialize(row: dict) -> dict:
    return {
        "id": str(row["_id"]),
        "productoId": str(row["productoId"]),
        "usuarioId": str(row["usuarioId"]),
        "tipo": row["tipo"],
        "cantidad": row["cantidad"],
        "stockAnterior": row["stockAnterior"],
        "stockPosterior": row["stockPosterior"],
        "motivo": row.get("motivo", ""),
        "creadoEn": row["creadoEn"],
    }


@router.post("", status_code=201)
def registrar_movimiento(body: MovimientoNuevo, admin: dict = Depends(require_admin)):
    if not body.motivo.strip():
        raise HTTPException(status_code=422, detail="El motivo es obligatorio.")

    product_id = as_id(body.productoId)
    user_id = ObjectId(admin["id"])
    now = datetime.now(timezone.utc)
    delta = body.cantidad if body.tipo == "entrada" else -body.cantidad
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    productos = client[settings.mongodb_db]["productos"]
    movimientos = client[settings.mongodb_db]["movimientos"]
    # El ID se genera antes para relacionar el evento atómico y la colección.
    event_id = ObjectId()
    event = {
        "movimientoId": event_id,
        "tipo": body.tipo,
        "cantidad": body.cantidad,
        "usuarioId": user_id,
        "motivo": body.motivo.strip(),
        "creadoEn": now,
    }
    try:
        condition = {"_id": product_id, "estado": "activo"}
        if delta < 0:
            condition["stock"] = {"$gte": body.cantidad}

        # find_one_and_update con stock anterior del documento retornado:
        # incremento + registro embebido son una sola modificación atómica.
        before = productos.find_one_and_update(
            condition,
            {"$inc": {"stock": delta}, "$push": {"historialCambios": event}},
            return_document=ReturnDocument.BEFORE,
        )
        if before is None:
            row = productos.find_one({"_id": product_id}, {"estado": 1, "stock": 1})
            if row is None or row.get("estado") != "activo":
                raise HTTPException(status_code=404, detail="Producto activo no encontrado.")
            raise HTTPException(status_code=409, detail="Stock insuficiente para la salida.")

        doc = {
            "_id": event_id,
            "productoId": product_id,
            "usuarioId": user_id,
            "tipo": body.tipo,
            "cantidad": body.cantidad,
            "stockAnterior": before["stock"],
            "stockPosterior": before["stock"] + delta,
            "motivo": body.motivo.strip(),
            "creadoEn": now,
        }
        try:
            movimientos.insert_one(doc)
        except PyMongoError:
            # No se revierte: la operación de stock ya fue aplicada.
            # Reintentar duplicaría existencias. Avisar explícitamente.
            raise HTTPException(
                status_code=503,
                detail="Stock actualizado, pero no se pudo guardar la copia del movimiento. No repitas la operación; revisa el historial embebido.",
            ) from None
        return serialize(doc)
    except PyMongoError:
        raise HTTPException(status_code=503, detail="No se pudo procesar el movimiento.") from None
    finally:
        client.close()


@router.get("")
def listar_movimientos(
    productoId: str | None = None,
    limite: int = Query(default=20, ge=1, le=100),
    admin: dict = Depends(require_admin),
):
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    try:
        query = {"productoId": as_id(productoId)} if productoId else {}
        rows = client[settings.mongodb_db]["movimientos"].find(query).sort("creadoEn", -1).limit(limite)
        return {"items": [serialize(row) for row in rows]}
    except PyMongoError:
        raise HTTPException(status_code=503, detail="No se pudo consultar movimientos.") from None
    finally:
        client.close()
