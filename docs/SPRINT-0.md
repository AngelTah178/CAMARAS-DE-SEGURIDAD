# Sprint 0 - Preparación del proyecto

## Alcance
Crear estructura inicial, API de salud y una pantalla de arranque React. No incluye aún autenticación ni conexión a MongoDB Atlas.

## Requisitos de desarrollo
- Python 3.11 o superior.
- Node.js compatible con Vite 7 (20.19+ o 22.12+).
- Git.

## Backend (PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```
Abrir http://127.0.0.1:8000/api/health y http://127.0.0.1:8000/docs.

## Frontend (otra terminal PowerShell)
```powershell
cd frontend
npm install
npm run dev
```
Abrir http://127.0.0.1:5173.

## Checklist QA manual
- [ ] /api/health devuelve status ok.
- [ ] /docs muestra Swagger con GET /api/health.
- [ ] React abre sin pantalla blanca ni errores de consola.
- [ ] npm run build finaliza sin error.
- [ ] .env no está versionado.

**Nota:** Las pruebas deben ejecutarse en el equipo local. Crear archivos en GitHub no significa que las pruebas se hayan aprobado.
