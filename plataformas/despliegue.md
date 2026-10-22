# Despliegue

Cómo queda el servidor.

## Caddy

Estándares: de OWASP, [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md), la sección
*HTTPS* del [*REST Security Cheat Sheet*](../fuentes/owasp/REST_Security.md) y la sección
*Infrastructure Configuration* del [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md).

- Caddy pone las cabeceras con la directiva `header`, para la web y para la API.
- Caddy corta el cuerpo con `request_body`: 1 MB en la API y 10 MB en las rutas de subida. El
  límite actúa antes de que el cuerpo llegue a Python.
- Caddy nunca sirve el directorio de los archivos de los usuarios.

## Configuración

Estándares: de systemd 257, la versión de Debian 13, [`systemd.exec`](../fuentes/systemd/systemd.exec.xml),
en *Environment* y *Credentials*, y la sección 2.7, *Secret Lifecycle*, del
[*Secrets Management Cheat Sheet*](../fuentes/owasp/Secrets_Management.md) de OWASP.

- Cada secreto llega al servicio con `LoadCredential=`, y la aplicación lo lee de
  `$CREDENTIALS_DIRECTORY`.

## coturn

Estándar: la sección 21.2, *Firewall Considerations*, del [RFC 8656](../fuentes/rfc/rfc8656.txt).

- coturn escucha en 3478 (UDP y TCP) y en 5349 (TLS), y niega relevar hacia direcciones privadas con
  `denied-peer-ip`. Endurece el RFC, que deja la restricción al administrador: TURN no sirve de
  puente a la red interna.

## Datos

Estándar: `StateDirectory=` de [`systemd.exec`](../fuentes/systemd/systemd.exec.xml).

- Los archivos de los usuarios viven en el `StateDirectory=` del servicio, `/var/lib/<app>/files/`.
  Están en la misma máquina y el respaldo los cubre junto con la base.

## Procesos

Estándares: la sección *Proxy Forwarded Headers* de
[*Behind a Proxy*](../fuentes/fastapi/behind-a-proxy.md) de FastAPI, y de systemd, `ExecStart=` y
`ExecStartPre=` de [`systemd.service`](../fuentes/systemd/systemd.service.xml), la sección
*Sandboxing* de [`systemd.exec`](../fuentes/systemd/systemd.exec.xml) y `OnCalendar=` de
[`systemd.timer`](../fuentes/systemd/systemd.timer.xml).

- Antes de arrancar, el servidor compila sus catálogos con `pybabel compile -d src/app/locale`.
- El servidor arranca con
  `uvicorn app.main:app --host 127.0.0.1 --ws-max-size 65536 --ws-per-message-deflate false`:
  `fastapi run` no le pasa a Uvicorn las opciones de WebSocket.
  - `--ws-max-size 65536` cumple el límite de mensaje de [fastapi.md](fastapi.md#websocket).
  - `--ws-per-message-deflate false` apaga la compresión: junto a datos secretos filtra
    información, como en CRIME y BREACH.
- Caddy le llega al servidor por loopback: nadie salta los límites de Caddy, y Uvicorn cree las
  cabeceras `X-Forwarded-*` solo de loopback, su valor por defecto.
- Cada tarea periódica de [fastapi.md](fastapi.md#tareas-periódicas) tiene su timer de systemd.
  El del barrido de archivos corre cada día.

## Registros

Estándares: [`systemd.exec`](../fuentes/systemd/systemd.exec.xml), en *Logging and Standard
Input/Output*.

## Respaldos

Estándar: la sección *SQL Dump* de [*Backup and Restore*](../fuentes/postgresql/backup.sgml) de
PostgreSQL.

## Valkey

Estándares: de Valkey 8.1, la versión de Debian 13, [*Administration*](../fuentes/valkey/admin.md)
y [*Security*](../fuentes/valkey/security.md).

- El almacén en memoria de todas las piezas es Valkey.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Tamaño del cuerpo | `request_body` en el Caddyfile |
| Archivos sin fila | El timer de barrido |
