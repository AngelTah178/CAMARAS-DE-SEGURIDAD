# Sprint 2.4 — Login React y panel inicial

Diseño original provisional (no usa PROYECTO-WEB). React JSX, Bootstrap y CSS propio; sin nuevas dependencias.

## Puesta en marcha
En una terminal:
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
En otra:
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD\frontend
npm install
npm run dev
```
Visita http://127.0.0.1:5173 . Vite reenvía /api a http://127.0.0.1:8000, sin modificar CORS de FastAPI.

## QA
1. npm run build termina sin errores.
2. Página de login visible en escritorio.
3. Página de login usable en móvil (responsive).
4. Usuario y contraseña incorrectos presentan error genérico.
5. Backend apagado presenta mensaje de conexión.
6. Credenciales correctas llevan al panel administrativo.
7. Panel muestra usuario de /api/auth/me.
8. Recargar página durante sesión válida conserva acceso en la pestaña.
9. Cerrar sesión regresa a formulario y elimina token de sessionStorage.
10. Modificar token en sessionStorage y recargar invalida la sesión.

No pegar contraseñas ni tokens en capturas o reportes QA.
**Nota de seguridad:** sessionStorage es almacenamiento del navegador, accesible a JavaScript; no es una sesión con cookie HttpOnly. Se utiliza provisionalmente para desarrollo académico. Se debe endurecer la gestión de sesiones y usar HTTPS al publicar. Este sprint no implementa módulos CRUD ni modifica roles o límites de intentos.
