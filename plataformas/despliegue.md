# Despliegue

Cómo queda el servidor.

## Proyecto

```
/etc/
├── <app>/
│   └── allowed_signers
├── caddy/
│   ├── Caddyfile
│   └── sites/
│       └── <app>-<pieza>.caddy
├── credstore.encrypted/
│   ├── <app>/
│   │   └── <campo>                 uno por campo de Settings
│   ├── <app>-migrate/
│   │   └── database_url
│   ├── <app>-backup/
│   │   ├── restic_repository
│   │   ├── restic_password
│   │   ├── s3_key_id
│   │   └── s3_secret_key
│   └── <app>-deploy/
│       └── github_token            solo en un repositorio privado
├── sysctl.d/
│   └── valkey.conf
├── sysusers.d/
│   └── <app>.conf
├── systemd/system/
│   ├── <app>*.service, <app>*.timer
│   └── valkey-server@<app>.service.d/
│       └── group.conf
└── valkey/
    └── valkey-<app>.conf
/srv/<app>/
├── current -> releases/<versión>
├── downloads/
│   └── desktop-<sistema>.<ext>
└── releases/
    └── <versión>/
        ├── server/
        ├── scripts/
        └── web/, panel/, landing/
/var/lib/
├── <app>/
│   └── files/
├── <app>-dump/
│   ├── <app>.dump
│   └── globals.sql
└── valkey/
    └── <app>.rdb
```

Plantilla: [`plantilla/infra/`](../plantilla/infra/), con las unidades, los sitios de Caddy, la
configuración de Valkey y `install.py`, que los instala;
[`plantilla/.github/workflows/release.yml`](../plantilla/.github/workflows/release.yml) y
[`plantilla/scripts/deploy.py`](../plantilla/scripts/deploy.py).

## Caddy

Estándares: de OWASP, la sección *Security Headers* del
[*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md), la sección
*HTTPS* del [*REST Security Cheat Sheet*](../fuentes/owasp/REST_Security.md) y la sección
*Infrastructure Configuration* del [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md).

- Caddy es el 2.6.2 de Debian 13.
- Cada superficie tiene su host: `landing` en `<dominio>`, `web` en `app.<dominio>` y `panel` en
  `panel.<dominio>`. En cada uno, `/api/*` va al servidor de la app, en el mismo origen que la web
  ([transversal.md](transversal.md#sesión)), y `/downloads/*`, a `/srv/<app>/downloads/`.
- Caddy pone las cabeceras con la directiva `header`, para la web y para la API.
- `Permissions-Policy` niega cada función que la app no usa, y permite con `(self)` las que la app
  declara con `install.py --allow`.
- Caddy envía también `Content-Security-Policy: frame-ancestors 'none'`: la CSP de SvelteKit va en
  una etiqueta `meta`, que no admite `frame-ancestors`.
- No se envía `Cross-Origin-Embedder-Policy`. Contradice a OWASP: solo habilita el aislamiento entre
  orígenes, que ninguna pieza usa, y bloquea las teselas de OSM y el formulario de pago incrustado.
- Caddy corta el cuerpo de `/api/*` con `request_body`: 10 MB en una petición
  `multipart/form-data`, la forma en que se sube un archivo
  ([transversal.md](transversal.md#archivos)), y 1 MB en las demás. Lo que pasa del límite no llega
  a Python.
- Una petición cuyo `Content-Length` pasa el límite recibe 413 antes de `request_body`: al cortarla,
  `request_body` responde 502, y el cliente reintenta un 502
  ([transversal.md](transversal.md#reintentos)).
- Caddy no corta por tiempo una conexión WebSocket: Uvicorn manda un ping cada 20 s y cierra la
  que no responde en 20 s, sus valores por defecto. Una conexión viva no se corta, y una caída no
  queda abierta.
- Caddy nunca sirve el directorio de los archivos de los usuarios: cada archivo pasa por el servidor,
  que aplica los permisos de su recurso.

## Configuración

Estándares: de systemd 257, la versión de Debian 13, [`systemd.exec`](../fuentes/systemd/systemd.exec.xml),
en *Environment* y *Credentials*, y las secciones 2.7.1, *Creation*, y 2.9, *Downtime, Break-glass,
Backup and Restore*, del [*Secrets Management Cheat Sheet*](../fuentes/owasp/Secrets_Management.md)
de OWASP.

- Cada campo de `Settings` llega al servicio con `LoadCredentialEncrypted=`, cifrado con
  `systemd-creds encrypt`: no queda en claro en el disco.
- Las unidades cargan entera la carpeta `/etc/credstore.encrypted/<app>/` con el prefijo `app`: un
  campo nuevo de `Settings` no cambia las unidades. Cada archivo se llama como su campo y se cifra
  con `--name=app_<campo>`, el nombre con que lo carga systemd.
- Las credenciales que el servidor no usa, como las de las migraciones, el respaldo y el
  despliegue, van en otra carpeta: el servidor no las recibe. `<app>-migrate/database_url` también
  se cifra con `--name=app_database_url`, porque reemplaza al de la carpeta de la app.
- Cada credencial de `<app>-backup/` tiene una copia fuera del servidor, en el gestor de
  contraseñas de quien despliega: `systemd-creds` cifra con una llave de la máquina, y sin
  `restic_password` el respaldo no se lee en otra.
- Cada mes, quien despliega abre el repositorio de restic desde su máquina con esa copia, con
  `restic snapshots`: una copia que no abre el respaldo se descubre antes de necesitarla.

## coturn

Estándar: la sección 21.2, *Firewall Considerations*, del [RFC 8656](../fuentes/rfc/rfc8656.txt).

- coturn escucha en 3478 (UDP y TCP) y en 5349 (TLS), y niega relevar hacia direcciones privadas con
  `denied-peer-ip`, una restricción que el RFC deja al servidor: TURN no sirve de puente a la red
  interna.

## Datos

Estándar: la entrada de `StateDirectory=`, en *Sandboxing*, de
[`systemd.exec`](../fuentes/systemd/systemd.exec.xml).

- Los archivos de los usuarios viven en el `StateDirectory=` del servicio, `/var/lib/<app>/files/`.
  Están en la misma máquina y el respaldo los cubre junto con la base.

## Procesos

Estándares: la sección *Sandboxing* de [`systemd.exec`](../fuentes/systemd/systemd.exec.xml), sin
la entrada de `StateDirectory=`, que cita «Datos», y la
sección *WebSocket Protocol Configuration* del
[*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

- Las unidades son las de `plantilla/infra/`, que `install.py` instala con el nombre, el puerto y
  el dominio de cada app, sin las de las piezas que no tiene.
- El usuario de cada app lo crea `systemd-sysusers` desde el `sysusers.conf` de
  `plantilla/infra/`, que `install.py` instala.
- El servidor arranca con
  `uvicorn app.main:app --port <puerto> --ws-max-size 65536 --ws-per-message-deflate false`:
  `fastapi run` no le pasa a Uvicorn las opciones de WebSocket.
  - `--port` es propio de cada app: dos apps de la misma máquina no chocan. `deploy.py` lo lee de
    la unidad instalada.
  - `--ws-max-size 65536` cumple el límite de mensaje de [fastapi.md](fastapi.md#websocket).
  - `--ws-per-message-deflate false` cumple *Compression security* de OWASP.
- Caddy le llega al servidor por loopback: nadie salta los límites de Caddy, y Uvicorn cree las
  cabeceras `X-Forwarded-*` solo de loopback, su valor por defecto.
- El timer del barrido de archivos de [fastapi.md](fastapi.md#archivos) corre
  `python -m app.tasks sweep` cada día.
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
- Cada app tiene su instancia, `valkey-server@<app>`, sin TCP y con el socket
  `/run/valkey-<app>/valkey-server.sock`, que solo abre el grupo de la app: ninguna app lee ni pisa
  las claves de otra. La instancia `valkey-server` del paquete queda apagada.
- Cada instancia tiene el `maxmemory` que recibe `install.py`, y la política `noeviction`, su valor
  por defecto: al llenarse, una escritura falla en vez de borrar un código o un contador.
- `vm.overcommit_memory = 1` va en `/etc/sysctl.d/valkey.conf`: Debian 13 no trae
  `/etc/sysctl.conf`.
- Transparent Huge Pages no se apaga en la máquina. Deja sin efecto *Valkey setup tips*:
  `disable-thp yes`, el valor por defecto de Valkey 8.1, las apaga solo para su proceso, sin
  cambiar los demás.

## Versiones

- Se despliega un tag `vMAJOR.MINOR.PATCH`. El CI corre en ese tag los jobs de `ci.yml`, y solo si
  pasan construye un artefacto con el servidor, sus catálogos compilados y el build de la web, y lo
  publica en un release de GitHub. El `.sha256` del release lleva el SHA-256 de cada archivo, con
  los instalables.
- El release es un borrador hasta que tiene el `.sha256`: un job que falla no deja publicado un
  release a medias.
- Cada versión queda en `/srv/<app>/releases/<versión>/`, y el enlace `/srv/<app>/current` apunta
  a la activa. Los datos quedan fuera de las versiones, en `/var/lib/<app>/`.
- `releases/` guarda las cinco versiones más recientes y la activa: las demás siguen en sus
  releases de GitHub.
- Quien despliega firma el `.sha256` del release en su máquina con `ssh-keygen -Y sign`, y el
  servidor solo instala el artefacto y los instalables que ese `.sha256` nombra, si lo firma una
  llave de `/etc/<app>/allowed_signers`: una cuenta de GitHub comprometida después de la firma no
  alcanza para desplegar otro archivo ni una versión anterior.
- `scripts/deploy.py` instala un tag en el servidor, y una persona lo lanza por `ssh`.
- Las migraciones corren en la unidad `<app>-migrate@<versión>.service`, con las credenciales del
  servidor, porque `alembic/env.py` lee `Settings`, salvo `database_url`, que es la del rol dueño
  del esquema. El rol del servidor no tiene DDL: un error o una inyección en la app no cambian el
  esquema.
- Si la versión trae migraciones, el servidor se detiene antes de migrar: el código anterior no
  corre sobre la base migrada. Si la migración falla, la versión se borra y vuelve la anterior,
  porque `env.py` aplica todas las migraciones en una sola transacción.
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
| Exposición de cada unidad | `systemd-analyze security --offline=yes --threshold=20 <unidad>`, en [`.github/workflows/infra.yml`](../.github/workflows/infra.yml) de canone |
