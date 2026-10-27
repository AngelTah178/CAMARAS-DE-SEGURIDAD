from fastapi import FastAPI, HTTPException
from pymongo.errors import PyMongoError
from pydantic import ValidationError

from app.database.mongo import ping_mongodb

app = FastAPI(
    title="Cámaras de Seguridad - API",
    description="API para inventario de equipos de videovigilancia.",
    version="0.2.0",
)


@app.get("/api/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": "camaras-de-seguridad"}


@app.get("/api/health/database", tags=["Sistema"])
def database_health():
    """Endpoint de diagnóstico de desarrollo: proteger antes de producción."""
    try:
        database_name = ping_mongodb()
    except (PyMongoError, ValidationError, ValueError) as exc:
        # Nunca devolver str(exc): podría revelar partes de la URI.
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con la base de datos.",
        ) from None

    return {"status": "ok", "database": database_name}
