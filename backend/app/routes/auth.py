from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.auth_dependencies import require_admin
from app.core.config import get_settings
from app.core.security import verify_password

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


class LoginRequest(BaseModel):
    usuario: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=1024)


@router.post("/login")
def login(datos: LoginRequest):
    settings = get_settings()
    if not settings.jwt_secret or len(settings.jwt_secret) < 32:
        raise HTTPException(status_code=503, detail="Autenticación no configurada.")

    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    try:
        user = client[settings.mongodb_db]["usuarios"].find_one(
            {"usuario": datos.usuario.strip()}
        )
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Servicio no disponible.") from None
    finally:
        client.close()

    if (
        not user
        or not user.get("activo")
        or user.get("rol") != "administrador"
        or not verify_password(datos.password, user.get("passwordHash", ""))
    ):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(user["_id"]),
            "role": "administrador",
            "iat": now,
            "exp": now + timedelta(minutes=30),
        },
        settings.jwt_secret,
        algorithm="HS256",
    )
    return {"access_token": token, "token_type": "bearer", "expires_in": 1800}


@router.get("/me")
def me(admin: dict = Depends(require_admin)):
    return admin
