"""CRUD inicial de productos, protegido con JWT de administrador."""
from datetime import datetime, timezone
from typing import Literal

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.core.auth_dependencies import require_admin
from app.core.config import get_settings

router = APIRouter(
    prefix="/api/productos",
    tags=["Productos"],
    dependencies=[Depends(require_admin)],
)
CATEGORIAS = Literal["camara", "dvr", "nvr", "accesorio"]
ESTADOS = Literal["activo", "inactivo"]


class ProductoNuevo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str = Field(min_length=1, max_length=50)
    nombre: str = Field(min_length=1, max_length=150)
    categoria: CATEGORIAS
    precio: float = Field(ge=0, allow_inf_nan=False)
    stockMinimo: int = Field(default=0, ge=0)
    marca: str | None = Field(default=None, max_length=80)
    modelo: str | None = Field(default=None, max_length=80)

    @field_validator("sku", "nombre", mode="after")
    @classmethod
    def no_vacio(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacío.")
        return value


class ProductoCambio(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str | None = Field(default=None, min_length=1, max_length=150)
    categoria: CATEGORIAS | None = None
    precio: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    stockMinimo: int | None = Field(default=None, ge=0)
    marca: str | None = Field(default=None, max_length=80)
    modelo: str | None = Field(default=None, max_length=80)

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío.")
        return value


def _id_valido(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=400, detail="Identificador inválido.")
    return ObjectId(value)


def _serialize(row: dict) -> dict:
    return {
        "id": str(row["_id"]),
        "sku": row["sku"],
        "nombre": row["nombre"],
        "categoria": row["categoria"],
        "precio": row["precio"],
        "stock": row["stock"],
        "stockMinimo": row["stockMinimo"],
        "estado": row["estado"],
        "marca": row.get("marca"),
        "modelo": row.get("modelo"),
    }


def _collection():
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    return client, client[settings.mongodb_db]["productos"]


@router.post("", status_code=201)
def crear_producto(body: ProductoNuevo):
    client, productos = _collection()
    try:
        doc = body.model_dump(exclude_none=True)
        doc.update({
            "stock": 0,
            "estado": "activo",
            "creadoEn": datetime.now(timezone.utc),
        })
        result = productos.insert_one(doc)
        return _serialize({**doc, "_id": result.inserted_id})
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="El SKU ya existe.") from None
    except PyMongoError:
        raise HTTPException(status_code=503, detail="No se pudo guardar el producto.") from None
    finally:
        client.close()


@router.get("")
def listar_productos(
    categoria: CATEGORIAS | None = None,
    estado: ESTADOS | None = None,
    buscar: str | None = Query(default=None, max_length=100),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=100),
):
    query = {}
    if categoria:
        query["categoria"] = categoria
    if estado:
        query["estado"] = estado
    if buscar:
        # Se usan coincidencias literales, sin permitir patrones regex del cliente.
        import re
        pattern = re.escape(buscar.strip())
        query["$or"] = [
            {"nombre": {"$regex": pattern, "$options": "i"}},
            {"sku": {"$regex": pattern, "$options": "i"}},
        ]
    client, productos = _collection()
    try:
        total = productos.count_documents(query)
        rows = productos.find(query).sort("_id", -1).skip((pagina - 1) * limite).limit(limite)
        return {"total": total, "pagina": pagina, "limite": limite,
                "items": [_serialize(row) for row in rows]}
    except PyMongoError:
        raise HTTPException(status_code=503, detail="No se pudo consultar productos.") from None
    finally:
        client.close()


@router.get("/{producto_id}")
def obtener_producto(producto_id: str):
    client, productos = _collection()
    try:
        row = productos.find_one({"_id": _id_valido(producto_id)})
        if not row:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        return _serialize(row)
    except PyMongoError:
        raise HTTPException(status_code=503, detail="No se pudo consultar el producto.") from None
    finally:
        client.close()


@router.patch("/{producto_id}")
def editar_producto(producto_id: str, body: ProductoCambio):
    cambios = body.model_dump(exclude_unset=True)
    if not cambios or any(value is None for value in cambios.values()):
        raise HTTPException(status_code=422, detail="Indica campos válidos para actualizar.")
    client, productos = _collection()
    try:
        row = productos.find_one_and_update(
            {"_id": _id_valido(producto_id), "estado": "activo"},
            {"$set": cambios},
            return_document=True,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Producto activo no encontrado.")
        return _serialize(row)
    except PyMongoError:
        raise HTTPException(status_code=503, detail="No se pudo actualizar el producto.") from None
    finally:
        client.close()


@router.delete("/{producto_id}")
def desactivar_producto(producto_id: str):
    client, productos = _collection()
    try:
        row = productos.find_one_and_update(
            {"_id": _id_valido(producto_id), "estado": "activo"},
            {"$set": {"estado": "inactivo"}},
            return_document=True,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Producto activo no encontrado.")
        return {"mensaje": "Producto desactivado.", "producto": _serialize(row)}
    except PyMongoError:
        raise HTTPException(status_code=503, detail="No se pudo desactivar el producto.") from None
    finally:
        client.close()
