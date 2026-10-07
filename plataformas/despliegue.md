# Despliegue

Cómo queda el servidor.

## Caddy

Estándares: de Caddy, [*Automatic HTTPS*](../estandares/caddy/automatic-https.md),
[*Keep Caddy Running*](../estandares/caddy/running.md),
[*Caddyfile Concepts*](../estandares/caddy/caddyfile-concepts.md), las
[opciones globales](../estandares/caddy/caddyfile-options.md) y las directivas
[`reverse_proxy`](../estandares/caddy/reverse_proxy.md),
[`file_server`](../estandares/caddy/file_server.md), [`encode`](../estandares/caddy/encode.md),
[`try_files`](../estandares/caddy/try_files.md), [`header`](../estandares/caddy/header.md) y
[`request_body`](../estandares/caddy/request_body.md); de OWASP,
[*HTTP Security Response Headers Cheat Sheet*](../estandares/owasp/HTTP_Headers.md) y
[*REST Security Cheat Sheet*](../estandares/owasp/REST_Security.md).

- Caddy pone las cabeceras con la directiva `header`, para la web y para la API.
- Caddy corta el cuerpo con `request_body`: 1 MB en la API y 10 MB en las rutas de subida. El
  límite actúa antes de que el cuerpo llegue a Python.
- Caddy nunca sirve el directorio de los archivos de los usuarios.

## Configuración

Estándares: [`systemd.exec`](../estandares/systemd/systemd.exec.xml), en *Environment* y
*Credentials*, y [*Secrets Management Cheat Sheet*](../estandares/owasp/Secrets_Management.md) de
OWASP.

- Los secretos viven solo en el `EnvironmentFile`.

## coturn

Estándares: [RFC 8656](../estandares/rfc/rfc8656.txt) y la
[documentación de coturn](../estandares/coturn/README.turnserver).

- coturn escucha en 3478 (UDP y TCP) y en 5349 (TLS), y niega relevar hacia direcciones privadas con
  `denied-peer-ip`. TURN no sirve de puente a la red interna.

## Datos

Estándares: de PostgreSQL, [*Client Authentication*](../estandares/postgresql/client-auth.sgml), y
[`systemd.exec`](../estandares/systemd/systemd.exec.xml).

- Los archivos de los usuarios viven en el `StateDirectory=` del servicio, `/var/lib/<app>/files/`.
  Están en la misma máquina y el respaldo los cubre junto con la base.

## Procesos

Estándares: de FastAPI, [*Deployments Concepts*](../estandares/fastapi/deployment-concepts.md) y
[*Run a Server Manually*](../estandares/fastapi/deployment-manually.md); de uv,
[*Locking and syncing*](../estandares/uv/sync.md); el
[FHS 3.0](../estandares/fhs/fhs-3.0.txt), y de systemd,
[`systemd.unit`](../estandares/systemd/systemd.unit.xml),
[`systemd.service`](../estandares/systemd/systemd.service.xml),
[`systemd.exec`](../estandares/systemd/systemd.exec.xml) y
[`systemd.timer`](../estandares/systemd/systemd.timer.xml).

- Un timer de systemd corre cada día el barrido de archivos de [fastapi.md](fastapi.md).

## Registros

Estándares: [`systemd.exec`](../estandares/systemd/systemd.exec.xml), en *Logging and Standard
Input/Output*.

## Respaldos

Estándares: de PostgreSQL, [*Backup and Restore*](../estandares/postgresql/backup.sgml),
[`pg_dump`](../estandares/postgresql/pg_dump.sgml) y
[`pg_restore`](../estandares/postgresql/pg_restore.sgml);
[`systemd.timer`](../estandares/systemd/systemd.timer.xml), y el
[ciclo de vida de objetos](../estandares/aws-s3/object-lifecycle-mgmt.md) de Amazon S3.

## Valkey

Estándares: de Valkey, [*Administration*](../estandares/valkey/admin.md) y
[*Security*](../estandares/valkey/security.md).

- El almacén en memoria de todas las piezas es Valkey.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Tamaño del cuerpo | `request_body` en el Caddyfile |
| Archivos sin fila | El timer de barrido |
