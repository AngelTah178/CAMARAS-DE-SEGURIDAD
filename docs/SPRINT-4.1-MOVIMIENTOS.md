# Sprint 4.1 — Entradas y salidas de inventario

API protegida por JWT administrador. No se implementa aún ajuste de stock ni interfaz gráfica; serán incrementos siguientes.

- POST /api/movimientos — registra entrada o salida con cantidad positiva y motivo.
- GET /api/movimientos — últimos movimientos, opcional productoId y límite.

## Ejemplo entrada
```json
{"productoId":"ID_REAL_DEL_PRODUCTO_DE_PRUEBA","tipo":"entrada","cantidad":5,"motivo":"QA de entrada inicial"}
```
Después, prueba una salida de 2 unidades:
```json
{"productoId":"ID_REAL_DEL_PRODUCTO_DE_PRUEBA","tipo":"salida","cantidad":2,"motivo":"QA de salida controlada"}
```
Stock esperado: 0 → 5 → 3 si el producto de pruebas empieza en 0.

## Nota de integridad importante
La modificación de stock y la anotación en `productos.historialCambios` son atómicas en **un documento**, mediante $inc y $push.

La inserción paralela en la colección `movimientos` es una segunda escritura, sin transacción multidocumento en este incremento. Si esta segunda operación falla, el stock ya cambió: el API devuelve HTTP 503 con una advertencia explícita de **no repetir** la petición y revisar `historialCambios`. No se debe interpretar ese 503 como ausencia de cambio. Para producción, implementar idempotencia y reconciliación (siguiente endurecimiento).

## Cómo ejecutar
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
Abre http://127.0.0.1:8000/docs, POST /api/auth/login, luego Authorize.

## QA manual (usar solo producto de prueba)
1. Swagger muestra POST y GET /api/movimientos.
2. POST sin token → 401.
3. Entrada 5 con motivo → 201.
4. GET /api/productos/{id} refleja aumento.
5. La colección movimientos contiene entrada con stockAnterior y stockPosterior.
6. productos.historialCambios incluye el evento de entrada.
7. Salida 2 → 201.
8. Stock disminuye correctamente.
9. Salida mayor que stock → 409, sin modificar existencias.
10. Producto desactivado → 404.
11. Cantidad 0 o negativa → 422.
12. GET /api/movimientos?productoId=... muestra el historial.
13. GET /api/auth/me y frontend Productos continúan funcionando.

Nunca usar pruebas destructivas en inventario real. **No repetir llamadas ante errores 503** hasta comprobar existencias e historial.
