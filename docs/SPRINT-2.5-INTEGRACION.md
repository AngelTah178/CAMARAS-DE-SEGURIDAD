# Sprint 2.5 — Integración final de autenticación

Este es el checklist final de integración. Los incrementos 2.1–2.4 ya fueron aprobados individualmente por QA manual. No se agregan límites de intentos.

1. POST /api/auth/login devuelve 200 con credenciales válidas.
2. POST /api/auth/login devuelve 401 con credenciales inválidas.
3. GET /api/auth/me sin token devuelve 401.
4. GET /api/auth/me con token válido devuelve 200.
5. GET /api/auth/me con token modificado o vencido devuelve 401.
6. En frontend, credenciales correctas muestran el panel.
7. Recargar la pestaña conserva temporalmente la sesión válida.
8. Cerrar sesión borra el token de sessionStorage.
9. npm run build termina sin errores.
10. GET /api/health y /api/health/database continúan funcionando.

Este checklist no equivale a pruebas ejecutadas automáticamente. Marcar aprobación solo después de revisar el flujo integrado en entorno local.

## Seguridad pendiente para producción
JWT en sessionStorage es provisional. Para producción se requerirá HTTPS, control de CORS, gestión más robusta de sesiones, protección de diagnósticos e instrumentación de auditoría. La exclusión de límites de intentos es decisión de alcance para este proyecto académico.
