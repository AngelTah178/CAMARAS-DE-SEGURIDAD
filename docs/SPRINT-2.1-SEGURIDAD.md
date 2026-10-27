# Sprint 2.1 — Seguridad y administrador inicial

**Rama:** develop. Este incremento no implementa login ni emite tokens JWT.

## Funcionalidad
- Hash de contrasenas mediante Argon2id.
- Alta manual interactiva del primer administrador en MongoDB Atlas.
- Reutilizacion del esquema `usuarios` de Sprint 1.3.
- Se evita transmitir contrasenas por argumentos de consola, codigo o GitHub.
- El script rechaza el alta si ya hay algun usuario en la coleccion.

## Ejecutar (PowerShell)
```powershell
cd C:\Proyectos\CAMARAS-DE-SEGURIDAD
git switch develop
git pull origin develop
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app.database.create_admin
```
Introduce un usuario de 3-64 caracteres sin espacios y una contrasena unica de al menos 12 caracteres. No se mostraran las contrasenas en pantalla. La creacion se verifica al final solicitando de nuevo la contrasena.

## Seguridad
- No pegar contrasenas, hash o cadenas de conexion en chats o capturas.
- No almacenar el usuario o contrasena de administrador en `.env`.
- La creacion inicial es administrativa, desde una consola local; no hay endpoint publico de registro.
- Si ya existe un usuario, el comando se niega a crear otro; no borres usuarios para repetir QA.
- Se utilizara un secreto JWT distinto para Sprint 2.2, nunca hardcodeado ni versionado.
- Una interrupcion despues de insert_one puede dejar el usuario ya creado, aunque no haya aparecido el mensaje final. Confirmar en Atlas antes de reintentar.
- Esta version asume una unica ejecucion administrativa; no usar simultaneamente desde dos terminales.

## QA manual
1. Las dependencias se instalan correctamente.
2. Una contrasena de menos de 12 caracteres se rechaza antes de conectar.
3. Una confirmacion distinta se rechaza.
4. Se registra exactamente un administrador valido.
5. En Atlas el campo `passwordHash` contiene hash que inicia `$argon2id$`.
6. No existe campo de contrasena en texto plano.
7. Una segunda ejecucion con datos validos rechaza otra alta.
8. El endpoint GET /api/health/database sigue funcionando.
9. El archivo .env permanece ignorado y el frontend continua compilando.

El criterio 4 requiere inspeccion de Atlas; no publicar el documento completo de usuario, ni su hash.
