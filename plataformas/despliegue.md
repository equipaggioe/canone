# Despliegue

Cómo queda el servidor.

## Caddy

Estándares: de Caddy, [*Automatic HTTPS*](../estandares/caddy/automatic-https.md),
[*Keep Caddy Running*](../estandares/caddy/running.md),
[*Caddyfile Concepts*](../estandares/caddy/caddyfile-concepts.md), las
[opciones globales](../estandares/caddy/caddyfile-options.md) y las directivas
[`reverse_proxy`](../estandares/caddy/reverse_proxy.md),
[`file_server`](../estandares/caddy/file_server.md), [`encode`](../estandares/caddy/encode.md) y
[`try_files`](../estandares/caddy/try_files.md).

## Procesos

Estándares: de FastAPI, [*Deployments Concepts*](../estandares/fastapi/deployment-concepts.md) y
[*Run a Server Manually*](../estandares/fastapi/deployment-manually.md); de uv,
[*Locking and syncing*](../estandares/uv/sync.md); el
[FHS 3.0](../estandares/fhs/fhs-3.0.txt), y de systemd,
[`systemd.unit`](../estandares/systemd/systemd.unit.xml),
[`systemd.service`](../estandares/systemd/systemd.service.xml) y
[`systemd.exec`](../estandares/systemd/systemd.exec.xml).

## Configuración

Estándares: [`systemd.exec`](../estandares/systemd/systemd.exec.xml), en *Environment* y
*Credentials*.

## Datos

Estándares: de PostgreSQL, [*Client Authentication*](../estandares/postgresql/client-auth.sgml).

## Registros

Estándares: [`systemd.exec`](../estandares/systemd/systemd.exec.xml), en *Logging and Standard
Input/Output*.

## Respaldos

Estándares: de PostgreSQL, [*Backup and Restore*](../estandares/postgresql/backup.sgml),
[`pg_dump`](../estandares/postgresql/pg_dump.sgml) y
[`pg_restore`](../estandares/postgresql/pg_restore.sgml);
[`systemd.timer`](../estandares/systemd/systemd.timer.xml), y el
[ciclo de vida de objetos](../estandares/aws-s3/object-lifecycle-mgmt.md) de Amazon S3.
