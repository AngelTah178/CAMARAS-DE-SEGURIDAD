# Sprint 4.3 — Interfaz React de movimientos

## Puesta en marcha
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd frontend
npm install
npm run build
npm run dev
```
Iniciar FastAPI en otra terminal desde backend. Acceder a http://127.0.0.1:5173 y abrir la pestaña **Movimientos** tras iniciar sesión.

## Funcionalidades
- Entrada o salida con cantidad positiva y motivo.
- Ajuste mediante stock objetivo no negativo.
- Selector de hasta 100 productos activos (primera página del endpoint).
- Historial de los últimos 100 movimientos.
- Generación de UUID por cada operación nueva; el mismo UUID se guarda en sessionStorage cuando una respuesta es incierta.
- Reintento de la solicitud pendiente, preservando datos originales.
- Ante un error 503 NO crear nuevo UUID ni registrar otra operación hasta reconciliar.

## QA manual
1. npm run build completa sin errores.
2. Login y navegación Dashboard/Productos siguen operativos.
3. Se muestra pestaña Movimientos.
4. Carga productos activos del inventario.
5. Se ven movimientos recientes, con motivo, stock previo y posterior.
6. Registrar entrada válida incrementa stock.
7. Registrar salida válida disminuye stock.
8. Registrar ajuste modifica stock a la cantidad objetivo.
9. Una salida mayor que el stock muestra mensaje de error.
10. Cantidad negativa o inválida se rechaza.
11. Motivo vacío o menor a 3 caracteres se rechaza.
12. Los formularios se limpian tras guardar correctamente.
13. El botón Actualizar recarga historial.
14. La operación pendiente conserva UUID incluso al refrescar pestaña.
15. Reintentar solicitud pendiente no duplica stock.
16. La interfaz se adapta a móvil.

## Precauciones
No provocar fallos artificiales de Atlas ni eliminar movimientos existentes para QA. La persistencia de solicitud pendiente es por pestaña en sessionStorage. La UI solo carga los primeros 100 productos activos y los últimos 100 movimientos: paginación/filtros avanzados son mejoras futuras. El token se guarda provisionalmente en sessionStorage como en el Sprint 2.4.
