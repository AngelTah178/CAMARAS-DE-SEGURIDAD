"""Movimientos atomicos por producto, con clave de idempotencia y reconciliacion.

No utiliza transacciones multidocumento: el historial del producto es fuente
canonica de operaciones. La coleccion movimientos es una proyeccion reparable.
"""
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.core.auth_dependencies import require_admin
from app.core.config import get_settings

router = APIRouter(prefix="/api/movimientos", tags=["Movimientos"])


class MovimientoNuevo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    productoId: str
    tipo: Literal["entrada", "salida", "ajuste"]
    cantidad: int | None = Field(default=None, gt=0)
    stockObjetivo: int | None = Field(default=None, ge=0)
    motivo: str = Field(min_length=3, max_length=300)
    solicitudId: UUID

    @model_validator(mode="after")
    def validar_operacion(self):
        if not self.motivo.strip():
            raise ValueError("El motivo no puede estar vacio.")
        if self.tipo == "ajuste":
            if self.stockObjetivo is None or self.cantidad is not None:
                raise ValueError("Para ajuste utiliza stockObjetivo, sin cantidad.")
        elif self.cantidad is None or self.stockObjetivo is not None:
            raise ValueError("Para entrada/salida utiliza cantidad, sin stockObjetivo.")
        return self


def as_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=400, detail="ID de producto invalido.")
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
        "solicitudId": row.get("solicitudId"),
    }


def from_event(product_id: ObjectId, event: dict) -> dict:
    return {
        "_id": event["movimientoId"],
        "productoId": product_id,
        "usuarioId": event["usuarioId"],
        "tipo": event["tipo"],
        "cantidad": event["cantidad"],
        "stockAnterior": event["stockAnterior"],
        "stockPosterior": event["stockPosterior"],
        "motivo": event["motivo"],
        "creadoEn": event["creadoEn"],
        "solicitudId": event["solicitudId"],
    }


def fingerprint(body: MovimientoNuevo, user_id: ObjectId) -> dict:
    return {
        "tipo": body.tipo,
        "cantidadSolicitada": body.cantidad,
        "stockObjetivoSolicitado": body.stockObjetivo,
        "motivo": body.motivo.strip(),
        "usuarioId": user_id,
    }


def existing_event(product: dict, request_id: str) -> dict | None:
    return next(
        (event for event in product.get("historialCambios", [])
         if event.get("solicitudId") == request_id),
        None,
    )


def ensure_projection(movimientos, product_id: ObjectId, event: dict) -> dict:
    doc = from_event(product_id, event)
    try:
        movimientos.update_one({"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True)
    except DuplicateKeyError:
        # Otra solicitud concurrente pudo completar la proyeccion.
        if movimientos.find_one({"_id": doc["_id"]}) is None:
            raise
    return doc


@router.post("", status_code=201)
def registrar_movimiento(body: MovimientoNuevo, admin: dict = Depends(require_admin)):
    product_id = as_id(body.productoId)
    user_id = ObjectId(admin["id"])
    request_id = str(body.solicitudId)
    signature = fingerprint(body, user_id)
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    productos = client[settings.mongodb_db]["productos"]
    movimientos = client[settings.mongodb_db]["movimientos"]
    try:
        # Una actualizacion externa concurrente obliga a volver a leer el stock.
        for _ in range(12):
            product = productos.find_one({"_id": product_id})
            if product is None:
                raise HTTPException(status_code=404, detail="Producto no encontrado.")
            previous_event = existing_event(product, request_id)
            if previous_event is not None:
                if any(previous_event.get(k) != v for k, v in signature.items()):
                    raise HTTPException(
                        status_code=409,
                        detail="solicitudId ya utilizado con datos diferentes.",
                    )
                try:
                    doc = ensure_projection(movimientos, product_id, previous_event)
                except PyMongoError:
                    raise HTTPException(
                        status_code=503,
                        detail="Operacion ya aplicada; proyeccion pendiente. Reintenta con el mismo solicitudId.",
                    ) from None
                return serialize(doc)

            if product.get("estado") != "activo":
                raise HTTPException(status_code=404, detail="Producto activo no encontrado.")

            before_stock = product["stock"]
            after_stock = (
                body.stockObjetivo if body.tipo == "ajuste"
                else before_stock + (body.cantidad if body.tipo == "entrada" else -body.cantidad)
            )
            if after_stock < 0:
                raise HTTPException(status_code=409, detail="Stock insuficiente.")
            quantity = abs(after_stock - before_stock) if body.tipo == "ajuste" else body.cantidad
            if quantity == 0:
                raise HTTPException(status_code=409, detail="El ajuste no modifica el stock.")

            event = {
                "movimientoId": ObjectId(),
                "solicitudId": request_id,
                **signature,
                "cantidad": quantity,
                "stockAnterior": before_stock,
                "stockPosterior": after_stock,
                "creadoEn": datetime.now(timezone.utc),
            }
            updated = productos.find_one_and_update(
                {
                    "_id": product_id,
                    "estado": "activo",
                    "stock": before_stock,
                    "historialCambios.solicitudId": {"$ne": request_id},
                },
                {"$set": {"stock": after_stock}, "$push": {"historialCambios": event}},
                return_document=ReturnDocument.AFTER,
            )
            if updated is None:
                continue

            try:
                doc = ensure_projection(movimientos, product_id, event)
            except PyMongoError:
                raise HTTPException(
                    status_code=503,
                    detail="Stock actualizado; copia del movimiento pendiente. Reintenta SOLO con el mismo solicitudId.",
                ) from None
            return serialize(doc)
        raise HTTPException(status_code=409, detail="Conflicto de concurrencia; reintenta con el mismo solicitudId.")
    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Estado de operacion incierto. Consulta historial y reintenta SOLO con el mismo solicitudId.",
        ) from None
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
