# Despliegue

Cómo queda el servidor.

## Caddy

Estándares: de OWASP, [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md), la sección
*HTTPS* del [*REST Security Cheat Sheet*](../fuentes/owasp/REST_Security.md) y la sección
*Infrastructure Configuration* del [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md).

- Caddy pone las cabeceras con la directiva `header`, para la web y para la API.
- `Permissions-Policy` niega cada función potente del navegador que la app no usa, y la que usa va
  con `(self)`. Contradice la recomendación de OWASP, que niega la cámara, el micrófono y la
  ubicación: WebRTC y los mapas los usan.
- No se envía `Cross-Origin-Embedder-Policy`. Contradice a OWASP: solo habilita el aislamiento entre
  orígenes, que ninguna pieza usa, y bloquea las teselas de OSM y el formulario de pago incrustado.
- Caddy corta el cuerpo con `request_body`: 1 MB en la API y 10 MB en las rutas de subida. El
  límite actúa antes de que el cuerpo llegue a Python.
- Caddy nunca sirve el directorio de los archivos de los usuarios: cada archivo pasa por el servidor,
  que aplica los permisos de su recurso.

## Configuración

Estándares: de systemd 257, la versión de Debian 13, [`systemd.exec`](../fuentes/systemd/systemd.exec.xml),
en *Environment* y *Credentials*, y la sección 2.7, *Secret Lifecycle*, del
[*Secrets Management Cheat Sheet*](../fuentes/owasp/Secrets_Management.md) de OWASP.

- Cada secreto llega al servicio con `LoadCredentialEncrypted=`, cifrado con `systemd-creds encrypt`:
  no queda en claro en el disco.
- `Settings` lee los secretos con `_secrets_dir=os.environ["CREDENTIALS_DIRECTORY"]`, y cada
  credencial se llama como su campo. En desarrollo, el `.env` apunta `CREDENTIALS_DIRECTORY` a una
  carpeta local que git ignora. Un `secrets_dir` que no existe solo da un aviso, y la variable
  leída así falla si falta.

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

Estándares: la sección *Sandboxing* de [`systemd.exec`](../fuentes/systemd/systemd.exec.xml) y la
sección *WebSocket Protocol Configuration* del
[*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

- Las unidades son las de `plantilla/infra/`, instaladas en `/etc/systemd/system/` con los datos
  de cada app.
- El servidor arranca con
  `uvicorn app.main:app --port <puerto> --ws-max-size 65536 --ws-per-message-deflate false`:
  `fastapi run` no le pasa a Uvicorn las opciones de WebSocket.
  - `--port` es propio de cada app: dos apps de la misma máquina no chocan.
  - `--ws-max-size 65536` cumple el límite de mensaje de [fastapi.md](fastapi.md#websocket).
  - `--ws-per-message-deflate false` cumple *Compression security* de OWASP.
- Caddy le llega al servidor por loopback: nadie salta los límites de Caddy, y Uvicorn cree las
  cabeceras `X-Forwarded-*` solo de loopback, su valor por defecto.
- El timer del barrido de archivos de [fastapi.md](fastapi.md#archivos) corre cada día.
- Cada unidad queda con una exposición de 2.0 o menos en `systemd-analyze security`.

## Respaldos

Estándar: la sección *SQL Dump* de [*Backup and Restore*](../fuentes/postgresql/backup.sgml) de
PostgreSQL.

- El respaldo de la base es un `pg_dump` diario en formato custom: `pg_restore` puede restaurar
  solo una parte.
- El respaldo sale de la máquina con `restic`, cifrado, hacia un repositorio S3 externo, con el
  dump y `/var/lib/<app>/files/` juntos. Corre cada día después del dump y conserva 7 diarios,
  4 semanales y 12 mensuales.
- El dump y `restic` son unidades distintas: el dump corre como `postgres`, y `restic` solo puede
  leer, con `CAP_DAC_READ_SEARCH`.

## Valkey

Estándares: de Valkey 8.1, la versión de Debian 13, la sección *Valkey setup tips* de
[*Administration*](../fuentes/valkey/admin.md) y [*Security*](../fuentes/valkey/security.md).

- El almacén en memoria de todas las piezas es Valkey.

## Versiones

- Se despliega un tag `vMAJOR.MINOR.PATCH`. El CI corre en ese tag los jobs de `ci.yml`, y solo si
  pasan construye un artefacto con el servidor, sus catálogos compilados y el build de la web, y lo
  publica en un release de GitHub con su SHA-256.
- Cada versión queda en `/srv/<app>/releases/<versión>/`, y el enlace `/srv/<app>/current` apunta
  a la activa. Los datos quedan fuera de las versiones, en `/var/lib/<app>/`.
- `releases/` guarda las cinco versiones más recientes y la activa: las demás siguen en sus
  releases de GitHub.
- Quien despliega firma el `.sha256` del release en su máquina con `ssh-keygen -Y sign`, y el
  servidor solo instala lo que firma una llave de `/etc/<app>/allowed_signers`: una cuenta de
  GitHub comprometida no alcanza para desplegar.
- `scripts/deploy.py` instala un tag en el servidor, y una persona lo lanza por `ssh`.
- Las migraciones corren en la unidad `<app>-migrate@<versión>.service`, con las credenciales del
  servidor, porque `alembic/env.py` lee `Settings`, salvo `database_url`, que es la del rol dueño
  del esquema. El rol del servidor no tiene DDL: un error o una inyección en la app no cambian el
  esquema.
- Si la versión nueva no pasa `GET /api/health`, `current` vuelve a la anterior solo si no hubo
  migraciones: el código anterior no corre sobre la base migrada.
- En un repositorio privado, el release se baja con un token de GitHub de solo lectura, cifrado
  con `systemd-creds`.
- Caddy sirve el build de cada superficie web, `web/`, `panel/` y `landing/`, desde
  `current/<pieza>/`. La PWA es `web/`.
- El CI construye del mismo tag los instalables de `desktop/` y los adjunta al release como
  `desktop-<sistema>.<ext>`. Caddy los sirve con ese nombre, igual en cada versión, desde
  `/srv/<app>/downloads/`, fuera de `releases/`: la landing enlaza siempre al mismo nombre.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Exposición de cada unidad | `systemd-analyze security --offline=yes --threshold=20 <unidad>` |
