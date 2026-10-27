# Sprint 2.3 — Protección de rutas JWT

El usuario solicitó explícitamente **no implementar límite de intentos**. La ruta POST /api/auth/login se conserva sin ese control.

## Actualización local
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Pruebas Swagger: http://127.0.0.1:8000/docs
1. Iniciar sesión con POST /api/auth/login y copiar el access_token de forma privada.
2. Entrar en **Authorize** e introducir el token en el esquema HTTP Bearer; Swagger puede agregar Bearer automáticamente.
3. Ejecutar GET /api/auth/me: HTTP 200, con id, usuario y rol administrador.
4. Sin token: 401.
5. Con token incorrecto o modificado: 401.
6. Con token vencido: 401.
7. Con token válido de otro rol: 403.
8. Si desactivas temporalmente tu único usuario en Atlas, GET /api/auth/me devuelve 403. Volver a activarlo inmediatamente.
9. GET /api/health sigue respondiendo 200.

No compartir tokens ni credenciales. La protección se aplica a /me y servirá como dependencia reutilizable para productos, movimientos y logs. Los endpoints del inventario se desarrollarán en sprints posteriores.

QA requerido: 9 verificaciones, con atención a autenticación y permisos.
