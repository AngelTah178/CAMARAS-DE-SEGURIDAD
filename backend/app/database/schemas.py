"""Esquemas MongoDB nativos: validacion con $jsonSchema (Sprint 1.3)."""

NUMERO = ["int", "long", "double", "decimal"]

SCHEMAS = {
    "usuarios": {
        "bsonType": "object",
        "required": ["usuario", "passwordHash", "rol", "activo", "creadoEn"],
        "properties": {
            "usuario": {"bsonType": "string", "minLength": 3},
            "passwordHash": {"bsonType": "string", "minLength": 1},
            "rol": {"enum": ["administrador"]},
            "activo": {"bsonType": "bool"},
            "creadoEn": {"bsonType": "date"},
        },
    },
    "productos": {
        "bsonType": "object",
        "required": ["sku", "nombre", "categoria", "precio", "stock", "stockMinimo", "estado", "creadoEn"],
        "properties": {
            "sku": {"bsonType": "string", "minLength": 1},
            "nombre": {"bsonType": "string", "minLength": 1},
            "marca": {"bsonType": "string"},
            "modelo": {"bsonType": "string"},
            "categoria": {"bsonType": "string", "minLength": 1},
            "precio": {"bsonType": NUMERO, "minimum": 0},
            "stock": {"bsonType": ["int", "long"], "minimum": 0},
            "stockMinimo": {"bsonType": ["int", "long"], "minimum": 0},
            "estado": {"enum": ["activo", "inactivo"]},
            "especificaciones": {"bsonType": "object"},
            "etiquetas": {"bsonType": "array", "items": {"bsonType": "string"}},
            "historialCambios": {"bsonType": "array", "items": {"bsonType": "object"}},
            "creadoEn": {"bsonType": "date"},
        },
    },
    "movimientos": {
        "bsonType": "object",
        "required": ["productoId", "tipo", "cantidad", "stockAnterior", "stockPosterior", "usuarioId", "creadoEn"],
        "properties": {
            "productoId": {"bsonType": "objectId"},
            "tipo": {"enum": ["entrada", "salida", "ajuste"]},
            "cantidad": {"bsonType": ["int", "long"], "minimum": 1},
            "stockAnterior": {"bsonType": ["int", "long"], "minimum": 0},
            "stockPosterior": {"bsonType": ["int", "long"], "minimum": 0},
            "usuarioId": {"bsonType": "objectId"},
            "motivo": {"bsonType": "string"},
            "creadoEn": {"bsonType": "date"},
        },
    },
    "auditoria_logs": {
        "bsonType": "object",
        "required": ["usuarioId", "accion", "entidad", "creadoEn"],
        "properties": {
            "usuarioId": {"bsonType": "objectId"},
            "accion": {"bsonType": "string", "minLength": 1},
            "entidad": {"bsonType": "string", "minLength": 1},
            "entidadId": {"bsonType": "objectId"},
            "detalle": {"bsonType": "object"},
            "creadoEn": {"bsonType": "date"},
        },
    },
}

INDEXES = {
    "usuarios": [
        {"keys": [("usuario", 1)], "name": "uq_usuario", "unique": True},
    ],
    "productos": [
        {"keys": [("sku", 1)], "name": "uq_sku", "unique": True},
        {"keys": [("categoria", 1), ("estado", 1)], "name": "idx_categoria_estado"},
        {"keys": [("nombre", 1)], "name": "idx_nombre"},
    ],
    "movimientos": [
        {"keys": [("productoId", 1), ("creadoEn", -1)], "name": "idx_producto_fecha"},
    ],
    "auditoria_logs": [
        {"keys": [("creadoEn", -1)], "name": "idx_fecha"},
        {"keys": [("usuarioId", 1), ("creadoEn", -1)], "name": "idx_usuario_fecha"},
    ],
}
