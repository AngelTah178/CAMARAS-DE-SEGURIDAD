"""Dependencia de autenticacion JWT para rutas privadas."""
import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticacion requerida o token invalido.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    settings = get_settings()
    if not settings.jwt_secret or len(settings.jwt_secret) < 32:
        raise HTTPException(status_code=503, detail="Autenticacion no configurada.")

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
            options={"require": ["exp", "iat", "sub"]},
        )
        user_id = ObjectId(payload["sub"])
    except (jwt.PyJWTError, ValueError, TypeError):
        raise unauthorized from None

    if payload.get("role") != "administrador":
        raise HTTPException(status_code=403, detail="Acceso no autorizado.")

    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    try:
        user = client[settings.mongodb_db]["usuarios"].find_one(
            {"_id": user_id},
            {"usuario": 1, "rol": 1, "activo": 1},
        )
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Servicio no disponible.") from None
    finally:
        client.close()

    if not user or not user.get("activo") or user.get("rol") != "administrador":
        raise HTTPException(status_code=403, detail="Acceso no autorizado.")
    return {"id": str(user["_id"]), "usuario": user["usuario"], "rol": user["rol"]}
