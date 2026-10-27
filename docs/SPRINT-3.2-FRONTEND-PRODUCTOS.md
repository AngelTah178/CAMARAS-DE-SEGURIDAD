# Sprint 3.2 — Módulo visual de productos

Implementación React/Bootstrap para CRUD de productos; no se utilizó PROYECTO-WEB.

## Ejecutar
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd frontend
npm install
npm run build
npm run dev
```
En otra terminal ejecutar FastAPI desde backend con uvicorn. Abrir http://127.0.0.1:5173, iniciar sesión y abrir **Productos**.

## QA manual
1. npm run build sin errores.
2. Login existente funciona.
3. Navegación Dashboard/Productos.
4. Tabla de productos carga desde MongoDB Atlas.
5. Registro válido y mensaje de éxito.
6. SKU duplicado muestra error.
7. Edición de nombre/precio sin editar stock.
8. Filtros de categoría y estado funcionan.
9. Buscar SKU/nombre funciona.
10. Paginación Anterior/Siguiente funciona.
11. Desactivar pide confirmación, cambia estado y aparece en filtro Inactivos.
12. Cancelar formulario no modifica datos.
13. Token inválido devuelve al login.
14. Diseño funcional en móvil.

Crear productos de prueba con SKU QA-... para no alterar inventario real. Los productos inactivos no se pueden editar. No incluye movimientos de stock ni auditoría completa, que pertenecen a sprints posteriores.

Seguridad: el token sigue guardándose en sessionStorage de forma provisional para uso local académico; no se publica ninguna credencial.
