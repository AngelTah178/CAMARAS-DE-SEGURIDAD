# Sprint 3.1 — API de productos

**Estado:** implementado, QA local pendiente.

## API
Rutas protegidas con JWT del administrador (Swagger: **Authorize**):
- POST /api/productos — crea producto, con stock inicial **0** y estado activo.
- GET /api/productos — listado paginado y filtros categoria, estado, buscar.
- GET /api/productos/{producto_id} — detalle por ObjectId.
- PATCH /api/productos/{producto_id} — actualiza metadatos de producto activo con operador $set.
- DELETE /api/productos/{producto_id} — desactiva sin eliminar físicamente.

Categorias permitidas: camara, dvr, nvr, accesorio. Se validan precios y stockMinimo no negativos, SKU único y datos obligatorios. **El stock no es editable por PATCH**: entradas, salidas y ajustes se gestionarán en un sprint de movimientos con trazabilidad.

Ejemplo POST:
```json
{
  "sku": "QA-CAM-001",
  "nombre": "Camara IP de prueba",
  "categoria": "camara",
  "precio": 1250,
  "stockMinimo": 2,
  "marca": "Marca de prueba",
  "modelo": "Modelo de prueba"
}
```

## QA manual
1. GET /api/productos sin token responde 401.
2. POST /api/productos sin token responde 401.
3. POST con token válido crea un documento y responde 201, stock 0.
4. Repetir SKU produce HTTP 409 (requiere índice único uq_sku).
5. Precio negativo produce HTTP 422.
6. GET /api/productos lista el producto.
7. GET /api/productos/{id} devuelve detalle correcto.
8. PATCH cambia precio/nombre, manteniendo stock.
9. GET filtros por categoria y buscar funcionan.
10. DELETE cambia estado a inactivo y preserva el documento en Atlas.
11. PATCH a producto inactivo devuelve 404.
12. GET /api/auth/me continúa funcionando.

IMPORTANTE: ejecutar QA sobre productos de prueba identificados con SKU QA-, nunca sobre inventario real. Es una API inicial sin auditoría completa de cambios (sprint posterior).

## Ejecución
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
Abrir http://127.0.0.1:8000/docs, ejecutar login y pulsar Authorize para probar productos.
