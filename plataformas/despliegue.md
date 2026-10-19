# Despliegue

Cómo queda el servidor.

## Caddy

Estándares: de Caddy, [*Automatic HTTPS*](../fuentes/caddy/automatic-https.md),
[*Keep Caddy Running*](../fuentes/caddy/running.md) y las secciones *Streaming* y *Defaults*, en
*Headers*, de [`reverse_proxy`](../fuentes/caddy/reverse_proxy.md); de OWASP,
[*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md),
[*REST Security Cheat Sheet*](../fuentes/owasp/REST_Security.md) y la sección *Infrastructure
Configuration* del [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md).

- Caddy pone las cabeceras con la directiva `header`, para la web y para la API.
- Caddy corta el cuerpo con `request_body`: 1 MB en la API y 10 MB en las rutas de subida. El
  límite actúa antes de que el cuerpo llegue a Python.
- Caddy nunca sirve el directorio de los archivos de los usuarios.

## Configuración

Estándares: [`systemd.exec`](../fuentes/systemd/systemd.exec.xml), en *Environment* y
*Credentials*, y [*Secrets Management Cheat Sheet*](../fuentes/owasp/Secrets_Management.md) de
OWASP.

- Los secretos viven solo en el `EnvironmentFile`.

## coturn

Estándares: [RFC 8656](../fuentes/rfc/rfc8656.txt) y la referencia de opciones de `turnserver`
de la [documentación de coturn](../fuentes/coturn/README.turnserver).

- coturn escucha en 3478 (UDP y TCP) y en 5349 (TLS), y niega relevar hacia direcciones privadas con
  `denied-peer-ip`. TURN no sirve de puente a la red interna.

## Datos

Estándares: de PostgreSQL, [*Client Authentication*](../fuentes/postgresql/client-auth.sgml), y
[`systemd.exec`](../fuentes/systemd/systemd.exec.xml).

- Los archivos de los usuarios viven en el `StateDirectory=` del servicio, `/var/lib/<app>/files/`.
  Están en la misma máquina y el respaldo los cubre junto con la base.

## Procesos

Estándares: de FastAPI, [*Deployments Concepts*](../fuentes/fastapi/deployment-concepts.md),
[*Run a Server Manually*](../fuentes/fastapi/deployment-manually.md) y la sección *Proxy
Forwarded Headers* de [*Behind a Proxy*](../fuentes/fastapi/behind-a-proxy.md); de Uvicorn, la
sección *Implementation* de [*Settings*](../fuentes/uvicorn/settings.md); de uv,
[*Locking and syncing*](../fuentes/uv/sync.md); el
[FHS 3.0](../fuentes/fhs/fhs-3.0.txt), y de systemd,
[`systemd.unit`](../fuentes/systemd/systemd.unit.xml),
[`systemd.service`](../fuentes/systemd/systemd.service.xml),
[`systemd.exec`](../fuentes/systemd/systemd.exec.xml) y
[`systemd.timer`](../fuentes/systemd/systemd.timer.xml).

- Antes de arrancar, el servidor compila sus catálogos con `pybabel compile -d src/app/locale`.
- El servidor arranca con
  `uvicorn app.main:app --host 127.0.0.1 --ws-max-size 65536 --ws-per-message-deflate false`:
  `fastapi run` no le pasa a Uvicorn las opciones de WebSocket.
- Caddy le llega al servidor por loopback: nadie salta los límites de Caddy, y Uvicorn cree las
  cabeceras `X-Forwarded-*` solo de loopback, su valor por defecto.
- Cada tarea periódica de [fastapi.md](fastapi.md#tareas-periódicas) tiene su timer de systemd.
  El del barrido de archivos corre cada día.

## Registros

Estándares: [`systemd.exec`](../fuentes/systemd/systemd.exec.xml), en *Logging and Standard
Input/Output*.

## Respaldos

Estándares: de PostgreSQL, [*Backup and Restore*](../fuentes/postgresql/backup.sgml),
[`pg_dump`](../fuentes/postgresql/pg_dump.sgml) y
[`pg_restore`](../fuentes/postgresql/pg_restore.sgml);
[`systemd.timer`](../fuentes/systemd/systemd.timer.xml), y el
[ciclo de vida de objetos](../fuentes/aws-s3/object-lifecycle-mgmt.md) de Amazon S3.

## Valkey

Estándares: de Valkey, [*Administration*](../fuentes/valkey/admin.md) y
[*Security*](../fuentes/valkey/security.md).

- El almacén en memoria de todas las piezas es Valkey.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Tamaño del cuerpo | `request_body` en el Caddyfile |
| Archivos sin fila | El timer de barrido |
