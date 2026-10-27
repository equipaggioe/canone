# Despliegue

Cómo queda el servidor. Una máquina aloja un solo producto: su servidor y sus superficies web.
`<app>` es el nombre del repositorio del producto.

## Proyecto

Estándar: del FHS 3.0, la versión que sigue Debian 13, las secciones 3.7, `/etc`; 3.15, `/run`;
3.17, `/srv`; 4.6, `/usr/lib`; 4.9, `/usr/local`, y 5.8, `/var/lib`, en
[*Filesystem Hierarchy Standard*](../fuentes/fhs/fhs-3.0.txt).

```
/etc/
├── <app>/
│   ├── allowed_signers
│   └── receivers                   las llaves de las receptoras
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
│   │   └── restic_password
│   └── <app>-deploy/
│       └── github_token            solo en un repositorio privado
├── nftables.conf
├── ssh/sshd_config.d/
│   ├── 00-<app>.conf               solo llaves, y root no entra
│   └── <app>-receiver.conf
├── sysctl.d/
│   └── valkey.conf
├── sysusers.d/
│   └── <app>.conf
├── systemd/system/
│   ├── <app>*.service, <app>*.timer, <app>-backup.path
│   └── valkey-server@<app>.service.d/
│       └── group.conf
├── tmpfiles.d/
│   └── <app>.conf
└── valkey/
    └── valkey-<app>.conf
/run/<app>-receiver/
└── request                         la receptora pide el respaldo
/srv/<app>/
├── current -> releases/<versión>
├── downloads/
│   └── desktop-<sistema>.<ext>
└── releases/
    └── <versión>/
        ├── server/
        ├── scripts/
        └── web/, panel/, landing/
/usr/local/lib/<app>/
└── backup-request                  el único comando de la receptora
/var/lib/
├── <app>/
│   ├── files/
│   └── last-backup                 su fecha es la del último respaldo
├── <app>-dump/
│   └── <app>.dump
└── valkey/
    └── <app>.rdb
```

Plantilla: [`plantilla/infra/`](../plantilla/infra/), con las unidades, los sitios de Caddy, la
configuración de Valkey y `install.py`, que los instala;
[`plantilla/receiver/`](../plantilla/receiver/), que corre en la receptora;
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
- `Permissions-Policy` nombra cada función de *Standardized Features* del
  [registro del W3C](../fuentes/w3c/permissions-policy-features.md), y `publickey-credentials-create`
  de Web Authentication Level 3: niega las que la app no usa, y permite con `(self)` las que declara
  con `install.py --allow`.
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
en *Environment* y *Credentials*, y la sección 2.7.1, *Creation*, del
[*Secrets Management Cheat Sheet*](../fuentes/owasp/Secrets_Management.md) de OWASP.

- Cada campo de `Settings` llega al servicio con `LoadCredentialEncrypted=`, cifrado con
  `systemd-creds encrypt`: no queda en claro en el disco.
- Las unidades cargan entera la carpeta `/etc/credstore.encrypted/<app>/` con el prefijo `app`: un
  campo nuevo de `Settings` no cambia las unidades. Cada archivo se llama como su campo y se cifra
  con `--name=app_<campo>`, el nombre con que lo carga systemd.
- Las credenciales que el servidor no usa, como las de las migraciones, el respaldo y el
  despliegue, van en otra carpeta: el servidor no las recibe. `<app>-migrate/database_url` también
  se cifra con `--name=app_database_url`, porque reemplaza al de la carpeta de la app.

## Coturn

Estándar: la sección 21.2, *Firewall Considerations*, del [RFC 8656](../fuentes/rfc/rfc8656.txt).

- coturn escucha en 3478 (UDP y TCP) y en 5349 (TLS), y niega relevar hacia direcciones privadas con
  `denied-peer-ip`, una restricción que el RFC deja al servidor: TURN no sirve de puente a la red
  interna.

## Datos

Estándar: la entrada de `StateDirectory=`, en *Sandboxing*, de
[`systemd.exec`](../fuentes/systemd/systemd.exec.xml).

- Los archivos de los usuarios viven en el `StateDirectory=` del servicio, `/var/lib/<app>/files/`.
  Están en la misma máquina y el respaldo los cubre junto con la base.

## Firewall

Estándar: la sección 4.1.3, *TCP and UDP*, de NIST SP 800-41 Rev. 1,
[*Guidelines on Firewalls and Firewall Policy*](../fuentes/nist/sp800-41r1.txt).

- El firewall es el nftables de Debian 13, con `/etc/nftables.conf`, que `install.py` instala y
  carga.
- Entran el 22 y el 80 por TCP, y el 443 por TCP y por UDP, el del HTTP/3 de Caddy. Con TURN entran
  también los puertos de «Coturn».
- ICMP entra entero: IPv6 lo necesita para encontrar a sus vecinos.
- Lo que sale no se filtra: la app habla con dominios de terceros, cuyas direcciones cambian.
- Nada pasa por la máquina hacia otra red.

## Máquina

- La máquina es Debian 13, y cada programa sale de sus paquetes: `caddy`, `postgresql`,
  `postgresql-17-postgis-3` si la app usa PostGIS, `valkey-server`, `restic`, `sudo`, `python3`,
  `nftables` y `unattended-upgrades`, y `coturn` si usa TURN.
- uv no está en Debian 13: sale del release de GitHub de la versión de
  [python.md](python.md#proyecto), con su SHA-256 comprobado.
- `unattended-upgrades` instala solo, cada día, las actualizaciones de Debian 13, y `install.py` lo
  enciende con `/etc/apt/apt.conf.d/20auto-upgrades`: una actualización de seguridad que espera a
  alguien deja la máquina expuesta mientras tanto. La del kernel se aplica al reiniciar la máquina,
  a mano.

## PostgreSQL

Estándares: de PostgreSQL 17, la versión de Debian 13, *Peer Authentication*, en
[*Client Authentication*](../fuentes/postgresql/client-auth.sgml), y la entrada *superuser status*
de *Role Attributes*, en [*Database Roles*](../fuentes/postgresql/user-manag.sgml).

- `install.py` crea la base `<app>`, el rol `<app>` del servidor y el rol `<app>_owner`, dueño de
  la base. Ninguno es superusuario: las migraciones y la purga no saltan los permisos ni salen de
  la base.
- Cada rol entra por el socket con `peer`, sin contraseña, desde la cuenta de su nombre: el
  servidor con `<app>`, y las migraciones, la purga y el volcado con `<app>_owner`. Una cuenta entra
  solo como su rol, y ningún rol tiene contraseña.
- `install.py` escribe la `database_url` del servidor en `<app>/`, y la del dueño en
  `<app>-migrate/`.
- `install.py` crea como `postgres` las extensiones que recibe con `--extension`: una extensión que
  no es *trusted*, como PostGIS, pide un superusuario.

## Procesos

Estándares: la sección *Sandboxing* de [`systemd.exec`](../fuentes/systemd/systemd.exec.xml), sin
la entrada de `StateDirectory=`, que cita «Datos», y la
sección *WebSocket Protocol Configuration* del
[*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

- Las unidades son las de `plantilla/infra/`, que `install.py` instala con el nombre y
  el dominio de la app, sin las de las piezas que no tiene.
- Las cuentas de la app las crea `systemd-sysusers` desde el `sysusers.conf` de
  `plantilla/infra/`, que `install.py` instala.
- El servidor arranca con
  `uvicorn app.main:app --port 8000 --ws-max-size 65536 --ws-per-message-deflate false`:
  `fastapi run` no le pasa a Uvicorn las opciones de WebSocket.
  - `--port` es 8000 en todo producto: la máquina no aloja otro servidor.
  - `--ws-max-size 65536` cumple el límite de mensaje de [fastapi.md](fastapi.md#websocket).
  - `--ws-per-message-deflate false` cumple *Compression security* de OWASP.
- Caddy le llega al servidor por loopback: nadie salta los límites de Caddy, y Uvicorn cree las
  cabeceras `X-Forwarded-*` solo de loopback, su valor por defecto.
- El timer del barrido de archivos de [fastapi.md](fastapi.md#archivos) corre
  `python -m app.tasks sweep` cada día.
- El timer de la purga de `event_log` de [fastapi.md](fastapi.md#registro-de-eventos) corre
  `python -m app.tasks purge` cada día. Su unidad corre con la cuenta `<app>_owner` y carga además
  `app_database_url` desde `<app>-migrate/`, como la de las migraciones.
- Cada unidad queda con una exposición de 2.0 o menos en `systemd-analyze security`.

## Respaldos

Estándar: la sección *SQL Dump* de [*Backup and Restore*](../fuentes/postgresql/backup.sgml) de
PostgreSQL.

- El respaldo de la base es un `pg_dump` en formato custom, que corre antes de cada respaldo:
  `pg_restore` puede restaurar solo una parte.
- El respaldo lleva el dump y `/var/lib/<app>/files/`, y sale de la máquina con `restic`, cifrado,
  hacia una receptora con `rest-server`. El código no va: está en los releases.
- La receptora pide el respaldo con `plantilla/receiver/`: abre `rest-server` en su puerto 8001 y
  un túnel `ssh -R` al 8001 del servidor, espera el resultado y cierra los dos.
- `rest-server` corre con `--append-only` y sin contraseña, y solo escucha en el loopback de la
  receptora: el servidor agrega respaldos, pero no borra ni reescribe los que hay, y restic los
  cifra.
- La receptora entra con la cuenta `<app>-receiver`, solo con una llave de
  `/etc/<app>/receivers`, y solo corre el comando que pide el respaldo, sin terminal ni otro túnel
  que el del 8001: una llave robada solo pide un respaldo.
- El comando comprueba el túnel antes de pedir el respaldo, y el respaldo se corta a las 4 h: un
  respaldo sin receptora no queda colgado.
- El primer respaldo crea el repositorio.
- Cada respaldo bueno cambia la fecha de `/var/lib/<app>/last-backup`, y el journal guarda cada
  corrida.
- El dump y `restic` son unidades distintas: el dump corre como `<app>_owner`, y `restic` solo
  puede leer, con `CAP_DAC_READ_SEARCH`.
- El dump no lleva los roles ni las extensiones: los crea `install.py`, y el dueño, que restaura,
  no puede crear una extensión que no es *trusted*.
- Se restaura en una máquina instalada con `install.py` y las mismas `--extension`:
  `restic restore` trae el dump y `/var/lib/<app>/files/`, y `<app>_owner` corre
  `pg_restore --exit-on-error` sobre la base que creó `install.py`.

## SSH

Estándar: de OpenSSH 10.0, la versión de Debian 13, [`sshd_config`](../fuentes/openssh/sshd_config.5).

- `sshd` solo acepta llaves, y `root` no entra: se entra con la cuenta que administra la máquina y
  `sudo`.
- La regla va en `/etc/ssh/sshd_config.d/00-<app>.conf`, que se lee antes que los archivos del
  proveedor, como `50-cloud-init.conf`: `sshd` se queda con el primer valor de cada opción.
- `install.py` crea la cuenta con `--admin`, en el grupo `sudo`, con las llaves de `--key` y la
  contraseña que pide al crearla. La primera vez corre como `root`, que entra con lo que da el
  proveedor; después, con `sudo` desde la cuenta, y `--admin` y `--key` solo agregan llaves.
- `sudo` pide la contraseña de la cuenta: una llave robada no da `root`.
- La cuenta nace con dos llaves: la de la computadora de quien administra y una guardada fuera de
  ella. Perder la computadora no deja fuera.
- `install.py` bloquea la contraseña de `root`: la consola web del proveedor, que no pasa por
  `sshd`, recibe la cuenta y su contraseña.
- `install.py` falla si la máquina no tiene `sudo`, si una llave no es válida, si no recibe
  `--admin` y no lo lanza `sudo` desde una cuenta con llave, o si la cuenta es `<app>`,
  `<app>_owner` o `<app>-receiver`: `systemd-sysusers` conserva una cuenta que ya existe, y la app
  correría con una cuenta del grupo `sudo`.

## Valkey

Estándares: de Valkey 8.1, la versión de Debian 13, la sección *Valkey setup tips* de
[*Administration*](../fuentes/valkey/admin.md) y [*Security*](../fuentes/valkey/security.md).

- El almacén en memoria de todas las piezas es Valkey.
- La app tiene su instancia, `valkey-server@<app>`, sin TCP y con el socket
  `/run/valkey-<app>/valkey-server.sock`, que solo abre el grupo de la app: el resto de los
  procesos de la máquina no lee sus claves. La instancia `valkey-server` del paquete queda apagada.
- Cada instancia tiene el `maxmemory` que recibe `install.py`, y la política `noeviction`, su valor
  por defecto: al llenarse, una escritura falla en vez de borrar un código o un contador.
- `vm.overcommit_memory = 1` va en `/etc/sysctl.d/valkey.conf`: Debian 13 no trae
  `/etc/sysctl.conf`.
- `install.py` falla si la máquina tiene menos swap que memoria, como pide *Valkey setup tips*.
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
- El artefacto no lleva el entorno del servidor: cada versión lo crea en la máquina con
  `uv sync --locked --no-dev`, con el Python 3.13 de Debian 13.
- `releases/` guarda las cinco versiones más recientes y la activa: las demás siguen en sus
  releases de GitHub.
- El `.sha256` del release se firma fuera de GitHub con `ssh-keygen -Y sign`, y el servidor solo
  instala el artefacto y los instalables que ese `.sha256` nombra, si lo firma una llave de
  `/etc/<app>/allowed_signers`: una cuenta de GitHub comprometida después de la firma no alcanza
  para desplegar otro archivo ni una versión anterior.
- `scripts/deploy.py` instala un tag en el servidor y se lanza por `ssh`, no desde el CI.
- Las migraciones corren en la unidad `<app>-migrate@<versión>.service`, con las credenciales del
  servidor, porque `alembic/env.py` lee `Settings`, salvo `database_url`, que es la del rol dueño
  del esquema. El rol del servidor no tiene DDL: un error o una inyección en la app no cambian el
  esquema.
- Una versión trae migraciones si sus heads de Alembic no son los de la activa, o si no hay una
  activa.
- Si la versión trae migraciones, el servidor se detiene antes de migrar: el código anterior no
  corre sobre la base migrada. Si la migración falla, la versión se borra y vuelve la anterior,
  porque `env.py` aplica todas las migraciones en una sola transacción.
- Si `GET /api/health` de la versión nueva no responde 204 en 30 intentos, uno por segundo,
  `current` vuelve a la anterior solo si no hubo migraciones: el código anterior no corre sobre la
  base migrada.
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
| `00-<app>.conf` y `<app>-receiver.conf` que lee `sshd` | `sshd -t` en el OpenSSH de Debian 13, en [`.github/workflows/infra.yml`](../.github/workflows/infra.yml) de canone |
| Solo llaves y sin `root`, aunque un archivo del proveedor permita contraseñas | `sshd -T` con un `50-cloud-init.conf` que las permite, en [`.github/workflows/infra.yml`](../.github/workflows/infra.yml) de canone |
| Los roles de «PostgreSQL», y que el dump del dueño se restaura en la base que crea `install.py` | Las cuentas de `sysusers.conf`, `create_database` de `install.py` y el `pg_dump` de la unidad, en el PostgreSQL y el PostGIS de Debian 13, en [`.github/workflows/infra.yml`](../.github/workflows/infra.yml) de canone |
| Exposición de cada unidad | `systemd-analyze security --offline=yes --threshold=20 <unidad>`, en [`.github/workflows/infra.yml`](../.github/workflows/infra.yml) de canone |
| Los puertos que entran, y que lo que sale no se filtra, de «Firewall» | `nftables.conf` cargado en el nftables de Debian 13, con conexiones desde otro namespace de red, en [`.github/workflows/infra.yml`](../.github/workflows/infra.yml) de canone |
