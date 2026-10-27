# Sprint 1.3 — Colecciones, validaciones e indices

**Rama:** `develop`. Estado: pendiente de QA local.

## Implementacion
Se crean las colecciones `usuarios`, `productos`, `movimientos` y `auditoria_logs` con validacion `$jsonSchema`. No se insertan productos ni usuarios.

- `usuarios`: nombre de usuario unico, hash de contrasena (nunca texto plano), rol administrador, estado y fecha.
- `productos`: SKU unico, datos comerciales, stock no negativo, especificaciones embebidas y arreglos de etiquetas/historial.
- `movimientos`: referencia a producto/usuario, tipo, cantidad, stock anterior/posterior y fecha.
- `auditoria_logs`: usuario, accion, entidad, detalle y fecha.

Las fechas se almacenaran como BSON Date en UTC. Los ids referenciados usan ObjectId.

## Uso en Windows PowerShell
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd backend
.\.venv\Scripts\python.exe -m app.database.setup
```
La salida debe informar cuatro colecciones creadas y sus indices. Vuelve a ejecutar el comando: debe decir "Conservada coleccion existente" sin errores (idempotencia).

## Verificacion en Atlas
En Atlas > Browse Collections > `SecurityStockDB` deben verse:
- usuarios
- productos
- movimientos
- auditoria_logs

Consulta en Atlas la pestaña **Validation** para comprobar que existe `$jsonSchema` en las colecciones nuevas; y **Indexes** para los indices `uq_usuario`, `uq_sku`, etc.

## QA manual
1. Las cuatro colecciones existen.
2. Todos los validadores se muestran en Atlas.
3. Los indices unicos `uq_usuario` y `uq_sku` existen.
4. Los indices de consulta se crearon.
5. Ejecutar dos veces el inicializador no produce errores.
6. No se insertaron productos ni usuarios de prueba.
7. GET /api/health/database sigue devolviendo 200.
8. `backend/.env` sigue ignorado por Git.

**Limitacion:** el inicializador conserva colecciones existentes. No comprueba ni modifica validadores antiguos; si existian previamente, verificar sus reglas manualmente. Los indices unicos pueden fallar si hay datos duplicados preexistentes. Esta etapa no implementa operaciones de stock ni auditoria transaccional.
