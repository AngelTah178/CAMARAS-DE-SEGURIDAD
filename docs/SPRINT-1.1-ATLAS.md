# Sprint 1.1 — Aprovisionamiento MongoDB Atlas

**Rama:** develop. **Estado:** pendiente de QA en Atlas.

## Objetivo
Preparar un clúster gratuito MongoDB Atlas para el proyecto, con acceso seguro desde el equipo de desarrollo. No implementar API ni CRUD en este incremento.

## Configuración
1. Entrar a https://cloud.mongodb.com y abrir o crear el proyecto `CAMARAS-DE-SEGURIDAD`.
2. Crear un clúster **Free (M0)** con nombre `SecurityStockCluster` (o documentar otro nombre si ya existe).
3. En Database Access, crear un usuario de base de datos dedicado; no usar credenciales de inicio de sesión de Atlas para la aplicación. Conceder `readWrite` únicamente en `SecurityStockDB` cuando sea posible.
4. En Network Access, agregar **solo la IP pública actual** del equipo de desarrollo. No habilitar indiscriminadamente `0.0.0.0/0`.
5. Usar `Connect > Drivers > Python` para copiar URI SRV. Rellenar usuario y contraseña únicamente en `backend/.env` local, nunca en commits, capturas ni mensajes públicos.
6. En el equipo: `Copy-Item backend/.env.example backend/.env` desde la raíz y sustituir marcadores. Si la contraseña contiene caracteres especiales, codificarla para URL.
7. Comprobar `git status --short --ignored` y verificar que el archivo local `backend/.env` está ignorado.

## QA manual (1.1)
- [ ] Proyecto de Atlas localizado.
- [ ] Clúster Free/M0 creado y disponible.
- [ ] Usuario específico para la aplicación creado.
- [ ] IP actual agregada a la lista de acceso.
- [ ] URI SRV colocada exclusivamente en `backend/.env` local.
- [ ] Archivo `backend/.env` aparece ignorado por Git.
- [ ] Ningún secreto agregado al repositorio.

**No compartir contraseñas ni URI con credenciales.** La prueba de conexión PyMongo corresponde al Sprint 1.2.
