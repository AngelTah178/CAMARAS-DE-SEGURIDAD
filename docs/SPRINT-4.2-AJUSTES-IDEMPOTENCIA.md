# Sprint 4.2 — Ajustes e idempotencia de movimientos

Rama: `develop`. Incremento publicado, **pendiente QA manual**.

## Cambio de contrato IMPORTANTE
`POST /api/movimientos` ahora exige `solicitudId`, un UUID generado por la aplicación cliente **para cada operación nueva**. Al reintentar la *misma* operación, reutilizar **exactamente ese mismo UUID y el mismo cuerpo**.

Este cambio es incompatible con el POST de Sprint 4.1 sin `solicitudId`. En Swagger, un POST viejo sin este campo recibirá 422. GET sigue siendo compatible y los registros anteriores continúan intactos.

Generar UUID desde PowerShell:
```powershell
[guid]::NewGuid().ToString()
```

Ejemplo de entrada:
```json
{
  "productoId": "ID_DEL_PRODUCTO_QA_ACTIVO",
  "tipo": "entrada",
  "cantidad": 5,
  "motivo": "Entrada de prueba Sprint 4.2",
  "solicitudId": "ed980d8e-3d57-4ae5-8f26-c960db83e034"
}
```

Ejemplo de ajuste a stock objetivo (usar **otro UUID nuevo**):
```json
{
  "productoId": "ID_DEL_PRODUCTO_QA_ACTIVO",
  "tipo": "ajuste",
  "stockObjetivo": 8,
  "motivo": "Conteo fisico de prueba",
  "solicitudId": "65a7c215-97a6-490f-82f8-a1e04c6d9069"
}
```

El ajuste calcula `cantidad=abs(stockObjetivo-stockAnterior)` y registra stock anterior y posterior. No se aceptan ajustes sin cambio, objetivos negativos, stock insuficiente, productos inactivos ni motivos en blanco.

## Consistencia y recuperación

En el mismo documento `productos`, la modificación de stock y el evento en `historialCambios` son atómicos. Se usa comparación de stock anterior y condición `historialCambios.solicitudId != UUID` para impedir aplicar dos veces la misma solicitud incluso si llegan peticiones concurrentes con el mismo UUID.

`movimientos` es una segunda escritura separada. Si falla después de actualizar stock, la API retorna HTTP 503 con la instrucción de **reintentar solo con idéntico UUID y cuerpo**. El reintento intenta reparar el registro faltante sin volver a cambiar stock. La respuesta no debe interpretarse como que no se aplicó la operación.

**Limitaciones:** no hay transacción multidocumento ni tarea automática de reconciliación. Errores de conexión pueden dejar un movimiento aplicado pero no reflejado en GET hasta recuperarlo mediante el reintento. Los movimientos antiguos del Sprint 4.1 carecen de `solicitudId`. No borrar el historial embebido de los productos. La colección `movimientos` conserva su esquema existente.

## QA manual (solo producto QA)
1. Swagger solicita `solicitudId` para POST.
2. POST sin JWT devuelve 401.
3. Entrada válida con UUID nuevo devuelve 201.
4. El stock se incrementa una sola vez.
5. Repetir *idéntico POST* (mismo UUID) no cambia el stock nuevamente.
6. Repetir UUID con diferente cantidad/motivo devuelve 409.
7. Ajuste a stock objetivo mayor funciona; historial contiene estado anterior/posterior.
8. Ajuste a objetivo menor funciona sin stock negativo.
9. Ajuste sin diferencia devuelve 409.
10. Objetivo negativo o `cantidad` junto a `stockObjetivo` devuelve 422.
11. Salida mayor que existencias devuelve 409.
12. GET /api/movimientos muestra entradas, salidas y ajustes.
13. `movimientos` e `historialCambios` comparten `movimientoId`.
14. Login, GET /api/productos y frontend continúan funcionando.

Para simular recuperación de un registro faltante, no elimines documentos reales ni provoques un fallo en Atlas. Esa ruta requiere pruebas aisladas; QA manual ordinario valida la reejecución idempotente.

## Ejecutar
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
Abre http://127.0.0.1:8000/docs. Inicia sesión y usa Authorize.

La UI para estos movimientos será implementada en Sprint 4.3.
