# Sprint 1.4 — Operadores MongoDB

## Objetivo
Demostrar los operadores MongoDB `$set`, `$inc`, `$push` y `$in` con PyMongo sobre datos temporales. No implementa todavía CRUD ni modifica productos reales.

## Ejecución local (PowerShell)
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd backend
.\.venv\Scripts\python.exe -m app.database.demo_operadores
```

## Resultado esperado
```text
OK $set: precio actualizado a 1250
OK $inc: stock actualizado a 15
OK $push: evento agregado al historial
OK $in: producto encontrado por categoria
QA operadores: 4/4 APROBADOS
Coleccion temporal de QA eliminada.
```

## Qué demuestra cada operador
- **$set**: actualiza el precio de 1000 a 1250.
- **$inc**: incrementa el inventario de 10 a 15.
- **$push**: añade un subdocumento al arreglo historialCambios.
- **$in**: encuentra una cámara al consultar varias categorías.

## Seguridad
El script utiliza una colección temporal con nombre aleatorio `_qa_operadores_<UUID>`, creada específicamente para la prueba. No toca las colecciones `productos`, `usuarios`, `movimientos` ni `auditoria_logs`. La colección temporal se elimina con `finally` si el proceso puede completar la limpieza. Ante un corte abrupto, revisa Atlas por colecciones con este prefijo; no elimines otras colecciones. Se requieren permisos para crear y eliminar colecciones.

## Checklist de QA
- [ ] Los cambios están en develop.
- [ ] $set actualiza el precio.
- [ ] $inc incrementa las existencias.
- [ ] $push añade exactamente un evento.
- [ ] $in encuentra el producto correcto.
- [ ] Aparece "QA operadores: 4/4 APROBADOS".
- [ ] La colección temporal desaparece de Atlas.
- [ ] Las cuatro colecciones operativas mantienen sus documentos y validadores.
- [ ] GET /api/health/database continúa respondiendo 200.

No dar por aprobado el sprint sin ejecutar el script y registrar estos resultados.
