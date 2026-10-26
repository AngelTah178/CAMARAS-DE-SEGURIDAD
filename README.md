# CAMARAS-DE-SEGURIDAD

Sistema web de inventario de equipos de videovigilancia (cámaras, DVR, NVR y accesorios).

## Objetivo
Administrador con inicio de sesión, CRUD de productos, filtros, movimientos de inventario y bitácora de auditoría.

## Arquitectura (3 capas)
- Datos: MongoDB Atlas M0 y PyMongo.
- API: Python con FastAPI.
- Presentación: React, Vite y Bootstrap.

## Estructura
- `backend/`: API REST.
- `frontend/`: interfaz web.
- `docs/`: documentación y QA.

## Desarrollo
- `main`: rama estable.
- `develop`: incrementos en desarrollo.
- Configuración sensible únicamente mediante variables de entorno locales; nunca subir `.env`.

Consulta `docs/SPRINT-0.md` para iniciar las pruebas locales.
