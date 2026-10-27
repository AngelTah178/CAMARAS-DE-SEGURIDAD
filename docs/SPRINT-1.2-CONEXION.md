# Sprint 1.2 — Conectar FastAPI con MongoDB Atlas

**Rama:** develop. **Estado:** pendiente de QA local.

## Alcance
- Leer la URI exclusivamente del archivo `backend/.env`.
- Conectar mediante PyMongo y ejecutar `ping` contra Atlas.
- Mantener `GET /api/health` para verificar la API sin depender de la base.
- Agregar `GET /api/health/database` para diagnosticar MongoDB. Durante este sprint es una ruta de desarrollo sin autenticación: deshabilitarla o protegerla antes de desplegar en producción.
- Ante errores de MongoDB, responder 503 sin exponer contraseñas, URI o detalles internos.

## Prueba local PowerShell
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```
En Swagger (http://127.0.0.1:8000/docs), probar `GET /api/health` y luego `GET /api/health/database`.

Resultado esperado si Atlas está accesible:
```json
{"status":"ok","database":"SecurityStockDB"}
```

Prueba negativa: detener el servidor, cambiar temporalmente el host en `backend/.env` por uno inválido (sin compartir credenciales) y ejecutar de nuevo el endpoint. Esperado: HTTP 503 y mensaje genérico. Restaurar el archivo después.

## QA
- [ ] API normal sigue devolviendo status ok.
- [ ] Swagger muestra ambos endpoints de salud.
- [ ] La conexión a Atlas devuelve status ok y SecurityStockDB.
- [ ] Con URI inválida o servidor inaccesible responde 503.
- [ ] La respuesta de error no filtra credenciales.
- [ ] .env permanece ignorado por Git.
- [ ] Frontend sigue compilando con npm run build.

**Importante:** el ping no crea colecciones ni garantiza permisos readWrite. Las pruebas de colecciones y escritura corresponden a Sprint 1.3.
