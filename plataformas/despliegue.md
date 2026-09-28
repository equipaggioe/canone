# Despliegue

Cómo queda el servidor.

## Caddy

Estándares: de Caddy, [*Automatic HTTPS*](../estandares/caddy/automatic-https.md),
[*Keep Caddy Running*](../estandares/caddy/running.md),
[*Caddyfile Concepts*](../estandares/caddy/caddyfile-concepts.md), las
[opciones globales](../estandares/caddy/caddyfile-options.md) y las directivas
[`reverse_proxy`](../estandares/caddy/reverse_proxy.md), [`header`](../estandares/caddy/header.md),
[`file_server`](../estandares/caddy/file_server.md), [`encode`](../estandares/caddy/encode.md) y
[`try_files`](../estandares/caddy/try_files.md).

- Caddy se configura con un Caddyfile.
- Caddy y coturn son lo único expuesto a internet. El servidor de FastAPI escucha en `127.0.0.1`.
- La web se sirve con `file_server` y `try_files {path} /200.html`, el `fallback` de
  [sveltekit.md](sveltekit.md).

## Procesos

Estándares: [`systemd.unit`](../estandares/systemd/systemd.unit.xml),
[`systemd.service`](../estandares/systemd/systemd.service.xml) y
[`systemd.exec`](../estandares/systemd/systemd.exec.xml).

- Cada servidor es un servicio de systemd con su propio usuario de sistema, y corre
  `fastapi run`.
- El código va en `/opt/<app>/`, instalado con `uv sync --locked --no-dev`.
- `ExecStartPre` aplica las migraciones con `alembic upgrade head`.
- El servicio lleva `NoNewPrivileges=yes`, `ProtectSystem=strict`, `ProtectHome=yes` y
  `PrivateTmp=yes`. Endurece los valores por defecto de systemd: el proceso solo escribe donde se
  le permite.

## Configuración

- Las variables de entorno de [fastapi.md](fastapi.md) salen de un `EnvironmentFile` en
  `/etc/<app>/env`, legible solo por root.

## Datos

- PostgreSQL y Redis son los de Debian 13, en la misma máquina. La app entra a PostgreSQL por el
  socket Unix con autenticación `peer`: no hay contraseña que guardar y la base no escucha en la
  red.

## Registros

- Los registros salen por stderr y los guarda journald. journald les pone la hora y los rota.

## Respaldos

Estándares: de PostgreSQL, [*Backup and Restore*](../estandares/postgresql/backup.sgml),
[`pg_dump`](../estandares/postgresql/pg_dump.sgml) y
[`pg_restore`](../estandares/postgresql/pg_restore.sgml);
[`systemd.timer`](../estandares/systemd/systemd.timer.xml), y el
[ciclo de vida de objetos](../estandares/aws-s3/object-lifecycle-mgmt.md) de Amazon S3.
