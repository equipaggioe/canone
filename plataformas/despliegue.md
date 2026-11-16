# Despliegue

Cómo queda el servidor. Una máquina aloja un solo producto: su servidor y sus superficies web. `<app>` es el nombre del repositorio del producto.

## Proyecto

Estándar: el [*Filesystem Hierarchy Standard*](../fuentes/fhs/fhs-3.0.txt) 3.0.

- La máquina queda así:

```
/etc/
├── <app>/
│   ├── allowed_signers
│   ├── development                 solo en desarrollo
│   └── receivers                   las llaves de las receptoras
├── apt/apt.conf.d/
│   ├── 20auto-upgrades
│   └── 52automatic-reboot
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
│       └── github_token            solo con --private
├── fstab                           la línea de /swapfile
├── nftables.conf
├── nftables.d/
│   └── turn.nft                    solo con TURN
├── postgresql/17/main/
│   ├── conf.d/
│   │   └── <app>.conf
│   ├── pg_hba.conf                 la línea de <app>_read
│   └── pg_ident.conf               la línea de la cuenta que administra
├── ssh/sshd_config.d/
│   ├── 00-<app>.conf               solo llaves, y root no entra
│   └── <app>-receiver.conf
├── sysctl.d/
│   └── valkey.conf
├── sysusers.d/
│   └── <app>.conf
├── systemd/
│   ├── journal-upload.conf.d/
│   │   └── 00-<app>.conf           solo con --logs
│   ├── journald.conf.d/
│   │   └── 00-<app>.conf
│   └── system/
│       ├── <app>*.service, <app>*.timer, <app>-backup.path
│       ├── systemd-journal-upload.service.d/
│       │   └── <app>.conf          solo con --logs
│       └── valkey-server@<app>.service.d/
│           └── group.conf
├── tmpfiles.d/
│   └── <app>.conf
├── turnserver.conf                 solo con TURN
├── valkey/
│   └── valkey-<app>.conf
└── wireguard/
    └── logs.conf                   solo con --logs
/home/<admin>/.ssh/
└── authorized_keys                 la cuenta que administra
/root/.ssh/
└── authorized_keys                 solo con authorize.py
/run/
├── <app>-receiver/
│   └── request                     la receptora pide el respaldo
└── valkey-<app>/
    ├── valkey-server.pid
    └── valkey-server.sock
/srv/<app>/
├── current -> releases/<versión>
├── downloads/
│   └── desktop-<sistema>.<ext>
└── releases/
    └── <versión>/
        ├── server/
        ├── web/, panel/, landing/
        └── <pieza>/                cada pieza en Java
/swapfile                           si la máquina tenía menos swap que memoria
/usr/local/
├── bin/
│   └── uv
├── lib/<app>/
│   └── backup-request              el único comando de la receptora
└── sbin/
    ├── <app>-database              database.py
    └── <app>-deploy                deploy.py
/var/
├── cache/private/<app>-backup/     la caché de restic
└── lib/
    ├── <app>/
    │   ├── files/
    │   └── last-backup             su fecha es la del último respaldo
    ├── <app>-dump/
    │   └── <app>.dump
    └── valkey/
        └── <app>.rdb
```

- La configuración propia de la app va en una carpeta suya, `/etc/<app>/` ([FHS §3.7.1](../fuentes/fhs/fhs-3.0.txt)).
- Lo que existe solo mientras la máquina corre, como un socket o la petición de la receptora, va en una carpeta de su programa en `/run` ([FHS §3.15.1](../fuentes/fhs/fhs-3.0.txt) y [§3.15.2](../fuentes/fhs/fhs-3.0.txt)).
- Un programa que lanza quien administra, como `deploy.py` y `database.py`, va en `/usr/local/sbin` con el nombre de la app delante, y uno que solo lanza otro programa, como `backup-request`, en `/usr/local/lib/<app>/` ([FHS §3.16.1](../fuentes/fhs/fhs-3.0.txt) y [§4.6.1](../fuentes/fhs/fhs-3.0.txt)).
- La app no crea carpetas ni archivos especiales en `/` ([FHS §3.1](../fuentes/fhs/fhs-3.0.txt)).
- Nada que se ejecuta va en `/etc` ([FHS §3.7.2](../fuentes/fhs/fhs-3.0.txt)).
- Lo que la máquina sirve, las versiones y los instalables, va en `/srv/<app>/` ([FHS §3.17.1](../fuentes/fhs/fhs-3.0.txt)).
- Lo que se instala fuera de los paquetes de Debian, como uv y los programas de la app, va en `/usr/local` ([FHS §4.9.1](../fuentes/fhs/fhs-3.0.txt)).
- Una caché que se puede rehacer, como la de restic, va en `/var/cache` ([FHS §5.5.1](../fuentes/fhs/fhs-3.0.txt)).
- El estado de la app va en sus carpetas de `/var/lib`, y nadie lo edita para configurarla ([FHS §5.8.1](../fuentes/fhs/fhs-3.0.txt)).

Plantilla: [plantilla/infra/](../plantilla/infra/), con las unidades, los sitios de Caddy, la configuración de Valkey, `install.py`, que los instala, `credentials.py`, que cifra las credenciales, `deploy.py`, que instala cada versión, `database.py`, que vacía la base de una máquina en desarrollo, `packages.py`, que instala los paquetes de la máquina, `swap.py`, que le da tanto swap como memoria, `uv.py`, que instala uv, `authorize.py`, que deja entrar a `root` con una llave antes de `install.py`, y `uninstall.py`, que deshace todo eso; [plantilla/receiver/](../plantilla/receiver/), que corre en la receptora, [plantilla/.github/workflows/release.yml](../plantilla/.github/workflows/release.yml), [plantilla/scripts/play.py](../plantilla/scripts/play.py), que sube cada app de `mobile/` a Play y baja su APK universal, y [plantilla/scripts/java.py](../plantilla/scripts/java.py), que compila cada pieza en Java de [java.md](java.md).

## Caddy

Estándares: de OWASP, el [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md) y el [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md).

- Cada superficie tiene su host: `landing` en `<dominio>`, `web` en `app.<dominio>` y `panel` en `panel.<dominio>`. En cada uno, `/api/*` va al servidor de la app, en el mismo origen que la web ([autenticacion.md](autenticacion.md#sesión)), y `/downloads/*`, a `/srv/<app>/downloads/`.
- Una petición por HTTP recibe un 308 hacia la misma URL por HTTPS, la redirección de Caddy por defecto.
- Caddy pone las cabeceras con la directiva `header`, para la web y para la API.
- No se envía `Cross-Origin-Embedder-Policy`: solo habilita el aislamiento entre orígenes, que ninguna pieza usa, y bloquea las teselas de OpenFreeMap y el formulario de pago incrustado.
- Caddy corta el cuerpo de `/api/*` con `request_body`: 10 MB en una petición `multipart/form-data`, la forma en que se sube un archivo ([transversal.md](transversal.md#archivos)), y 1 MB en las demás. Lo que pasa del límite no llega a Python.
- Una petición que pasa el límite recibe 413 de `request_body`, por su `Content-Length` antes de leer el cuerpo, o al cortarlo si no lo declara: un 413 no se reintenta ([transversal.md](transversal.md#reintentos)). [Caddy 2.11.9](https://raw.githubusercontent.com/caddyserver/caddy/v2.11.9/modules/caddyhttp/requestbody/requestbody.go)
- Caddy nunca sirve el directorio de los archivos de los usuarios: cada archivo pasa por el servidor, que aplica los permisos de su recurso.
- Toda respuesta lleva `Content-Security-Policy: frame-ancestors 'none'` y `X-Frame-Options: DENY`. `frame-ancestors` va en la cabecera: la CSP de SvelteKit va en una etiqueta `meta`, que no lo admite ([HTTP Security Response Headers Cheat Sheet, *X-Frame-Options*](../fuentes/owasp/HTTP_Headers.md)).
- `/api/*` lleva `Cache-Control: no-store` si el servidor no puso otro: toda respuesta de la API se trata como sensible ([HTTP Security Response Headers Cheat Sheet, *Cache-Control*](../fuentes/owasp/HTTP_Headers.md)).
- La landing lleva `X-Robots-Tag: index, follow`, y `app.<dominio>`, `panel.<dominio>` y `/api/*`, `X-Robots-Tag: noindex, nofollow`: solo la landing es pública ([HTTP Security Response Headers Cheat Sheet, *X-Robots-Tag*](../fuentes/owasp/HTTP_Headers.md)).
- `Permissions-Policy` nombra cada función de *Standardized Features* del [registro del W3C](../fuentes/w3c/permissions-policy-features.md), y `publickey-credentials-create` de Web Authentication Level 3: niega las que la app no usa, y permite con `(self)` las que recibe con `install.py --allow`, las del archivo `permissions` de [repositorio.md](../repositorio.md#archivos-del-raíz) ([HTTP Security Response Headers Cheat Sheet, *Permissions-Policy*](../fuentes/owasp/HTTP_Headers.md)).
- Caddy no corta por tiempo una conexión WebSocket: el ping de Uvicorn de «Procesos» cierra la que se cayó ([WebSocket Security, *Infrastructure Configuration*](../fuentes/owasp/WebSocket_Security.md)).
- Toda respuesta lleva `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` ([HTTP Security Response Headers Cheat Sheet, *Strict-Transport-Security (HSTS)*](../fuentes/owasp/HTTP_Headers.md)).
- Toda respuesta lleva `X-Content-Type-Options: nosniff` y el `Content-Type` de lo que contiene ([HTTP Security Response Headers Cheat Sheet, *X-Content-Type-Options*](../fuentes/owasp/HTTP_Headers.md)).
- Una página HTML se sirve como `text/html; charset=utf-8` ([HTTP Security Response Headers Cheat Sheet, *Content-Type*](../fuentes/owasp/HTTP_Headers.md)).
- Toda respuesta lleva `Referrer-Policy: strict-origin-when-cross-origin` ([HTTP Security Response Headers Cheat Sheet, *Referrer-Policy*](../fuentes/owasp/HTTP_Headers.md)).
- Toda respuesta lleva `Cross-Origin-Opener-Policy: same-origin` ([HTTP Security Response Headers Cheat Sheet, *Cross-Origin-Opener-Policy (COOP)*](../fuentes/owasp/HTTP_Headers.md)).
- Toda respuesta lleva `Cross-Origin-Resource-Policy: same-site` ([HTTP Security Response Headers Cheat Sheet, *Cross-Origin-Resource-Policy (CORP)*](../fuentes/owasp/HTTP_Headers.md)).
- Caddy quita la cabecera `Server` ([HTTP Security Response Headers Cheat Sheet, *Server*](../fuentes/owasp/HTTP_Headers.md)).
- Ninguna respuesta lleva `X-Powered-By` ([HTTP Security Response Headers Cheat Sheet, *X-Powered-By*](../fuentes/owasp/HTTP_Headers.md)).
- Ninguna respuesta lleva `X-XSS-Protection`, `Expect-CT` ni `Public-Key-Pins` ([HTTP Security Response Headers Cheat Sheet, *X-XSS-Protection*](../fuentes/owasp/HTTP_Headers.md), [*Expect-CT*](../fuentes/owasp/HTTP_Headers.md) y [*Public-Key-Pins (HPKP)*](../fuentes/owasp/HTTP_Headers.md)).
- Caddy pasa al servidor el upgrade de WebSocket, con `Upgrade` y `Connection: upgrade` ([WebSocket Security, *Infrastructure Configuration*](../fuentes/owasp/WebSocket_Security.md)).

## Configuración

Estándar: [systemd.exec](../fuentes/systemd/systemd.exec.xml) de systemd.

- Las unidades cargan entera la carpeta `/etc/credstore.encrypted/<app>/` con el prefijo `app`: un campo nuevo de `Settings` no cambia las unidades. Cada archivo se llama como su campo y se cifra con `--name=app_<campo>`, el nombre con que lo carga systemd, que `systemd-creds` compara al descifrar. [systemd 257](https://raw.githubusercontent.com/systemd/systemd/v257.13/man/systemd-creds.xml)
- Las credenciales que el servidor no usa, como las de las migraciones, el respaldo y el despliegue, van en otra carpeta: el servidor no las recibe. `<app>-migrate/database_url` también se cifra con `--name=app_database_url`, porque reemplaza al de la carpeta de la app.
- `credentials.py <app>` cifra las credenciales que lee por stdin, una línea `campo=valor` por credencial y el valor sin comillas: cada campo de `Settings` en `<app>/`, `restic_password` en `<app>-backup/` y `github_token` en `<app>-deploy/`, estas dos con su propio nombre en `--name`. Escribe solo los campos que recibe y reinicia el servidor si corre, así que cambiar un secreto no pasa por `install.py`.
- `credentials.py` falla sin escribir nada si una línea no es `campo=valor`, si un valor está vacío o un campo repetido, o si recibe `database_url`, `turn_secret` o `valkey_url`, que escribe `install.py`. Su mensaje nunca lleva el valor.
- Cada campo de `Settings` llega al servicio con `LoadCredentialEncrypted=`, desde `/etc/credstore.encrypted/` y cifrado con `systemd-creds encrypt`: no queda en claro en el disco ([systemd.exec, *Credentials*](../fuentes/systemd/systemd.exec.xml)).
- Ningún secreto llega a una unidad por una variable de entorno ([systemd.exec, *Environment*](../fuentes/systemd/systemd.exec.xml)).

## Coturn

Estándar: [RFC 8656](../fuentes/rfc/rfc8656.txt).

- Solo una app con llamadas usa coturn: `install.py --turn` instala `/etc/turnserver.conf` y abre sus puertos con `/etc/nftables.d/turn.nft`.
- `install.py` genera el secreto de las credenciales la primera vez y lo conserva, para que una credencial ya entregada siga sirviendo. Va en `static-auth-secret` de `/etc/turnserver.conf`, que solo lee el grupo `turnserver`, y como `turn_secret` en la carpeta de credenciales de la app. El `realm` es el dominio de la app.
- En una máquina cuya interfaz tiene solo una dirección privada, porque la pública le llega por NAT, `install.py --turn-ip <pública>` agrega `external-ip=<pública>/<privada>`, con la privada por la que la máquina sale a internet: sin ella, coturn entrega su dirección privada, y la otra parte de la llamada no lo alcanza.
- coturn no abre su consola de administración (`no-cli`), que por defecto escucha en el 5766 de la máquina, sin contraseña, para cualquier cuenta de ella. [coturn 4.6.1](https://raw.githubusercontent.com/coturn/coturn/4.6.1/examples/etc/turnserver.conf)
- coturn no envía el atributo `SOFTWARE` (`no-software-attribute`): viaja sin cifrar y nombra su versión.
- coturn exige una credencial en cada petición: solo releva con las temporales de [transversal.md](transversal.md#llamadas-de-voz-y-video) ([RFC 8656 §7.2](../fuentes/rfc/rfc8656.txt) y [§21.1.1](../fuentes/rfc/rfc8656.txt)).
- El secreto son 256 bits aleatorios ([RFC 8656 §21.1.2](../fuentes/rfc/rfc8656.txt)).
- coturn escucha solo en el 3478, por UDP y por TCP, sin TLS: WebRTC ya cifra la llamada, y TLS pediría el certificado de Caddy, que vive en una carpeta interna suya ([RFC 8656 §3.1](../fuentes/rfc/rfc8656.txt) y [§21.1.6](../fuentes/rfc/rfc8656.txt)).
- Releva solo por UDP, del 49152 al 65535: WebRTC no releva por TCP ([RFC 8656 §3.1](../fuentes/rfc/rfc8656.txt) y [§7.2](../fuentes/rfc/rfc8656.txt)).
- Una credencial tiene a lo sumo 10 asignaciones, y cada una 500 000 bytes por segundo, 4 Mbit/s: `user-quota` y `max-bps` ([RFC 8656 §7.2](../fuentes/rfc/rfc8656.txt), [§21.1.7](../fuentes/rfc/rfc8656.txt) y [§21.3.1](../fuentes/rfc/rfc8656.txt)).
- coturn niega relevar hacia cada bloque que los registros de direcciones de uso especial de IANA, [IPv4](../fuentes/iana/iana-ipv4-special-registry.csv) e [IPv6](../fuentes/iana/iana-ipv6-special-registry.csv), marcan como no alcanzable globalmente, y hacia 6to4, `2002::/16`, que el registro marca como alcanzable: TURN no sirve de puente a la red interna ni a un túnel. Las direcciones sin especificar, `0.0.0.0` y `::`, no van en `denied-peer-ip`, porque coturn las lee como cualquier dirección: la primera queda dentro de `0.0.0.0/8`, y la segunda coturn la niega por sí mismo ([RFC 8656 §21.1.4](../fuentes/rfc/rfc8656.txt) y [§21.4](../fuentes/rfc/rfc8656.txt)).
- `no-multicast-peers` niega las direcciones de multicast, y coturn niega por defecto las de loopback ([RFC 8656 §21.1.4](../fuentes/rfc/rfc8656.txt)). [coturn 4.6.1](https://raw.githubusercontent.com/coturn/coturn/4.6.1/examples/etc/turnserver.conf)
- Una asignación dura a lo sumo una hora sin refrescarse, el `max-allocate-lifetime` de coturn por defecto ([RFC 8656 §7.2](../fuentes/rfc/rfc8656.txt)). [coturn 4.6.1](https://raw.githubusercontent.com/coturn/coturn/4.6.1/examples/etc/turnserver.conf)
- `turn.nft` descarta lo que llega al 3478 desde Teredo, `2001::/32`, o 6to4, `2002::/16`: coturn acepta una petición desde un túnel ([RFC 8656 §21.4](../fuentes/rfc/rfc8656.txt)).

## Datos

- Los archivos de los usuarios viven en la máquina, en `/var/lib/<app>/files/`, y el respaldo los cubre junto con la base.

## Desinstalar

- `sudo python3 uninstall.py <app> database|app|machine` deshace lo que dejan los demás programas, y cada nivel incluye al anterior. Con `--dry-run` imprime lo que haría, sin hacerlo.
- `database` detiene el servidor y sus timers, y borra la base, sus tres roles, sus credenciales `<app>/database_url` y `<app>-migrate/`, su línea de `pg_hba.conf` y de `pg_ident.conf`, `/var/lib/<app>/files/` y el dump. `install.py` los vuelve a crear.
- `app` borra además cada unidad, sitio, credencial, cuenta y carpeta de la app.
- `machine` borra además el swap, uv, los archivos que `install.py` escribe para toda la máquina y ningún paquete trae, y el túnel del journal. Los paquetes quedan, con lo que `install.py` sobrescribió en ellos, como el `Caddyfile` o `nftables.conf`: dejar la máquina como la entrega el proveedor es reinstalarla desde su panel.
- Ningún nivel toca la cuenta que administra, sus llaves ni `00-<app>.conf`, y `root` sigue bloqueado: son la entrada a la máquina.

## Firewall

Estándar: NIST SP 800-41 Rev. 1, [*Guidelines on Firewalls and Firewall Policy*](../fuentes/nist/sp800-41r1.txt).

- El firewall es el nftables de Debian 13, con `/etc/nftables.conf`, que `install.py` instala y carga. Incluye `/etc/nftables.d/*.nft`, donde una pieza que la app puede no tener agrega sus reglas.
- Entran el 22 y el 80 por TCP, y el 443 por TCP y por UDP, el del HTTP/3 de Caddy. Con TURN entran también los puertos de «Coturn».
- Lo que sale no se filtra: la app habla con dominios de terceros, cuyas direcciones cambian.
- ICMP entra entero: IPv6 lo necesita para encontrar a sus vecinos ([NIST SP 800-41 §4.1.4](../fuentes/nist/sp800-41r1.txt)).
- Lo que entra se descarta salvo lo que deja entrar esta sección, con las mismas reglas en IPv4 y en IPv6 ([NIST SP 800-41 §4](../fuentes/nist/sp800-41r1.txt), [§4.1.2](../fuentes/nist/sp800-41r1.txt) y [§4.1.3](../fuentes/nist/sp800-41r1.txt)).
- Entran solo TCP, UDP e ICMP ([NIST SP 800-41 §4.1](../fuentes/nist/sp800-41r1.txt)).
- Fuera del loopback no entra nada con origen o destino en `0.0.0.0/8`, `127.0.0.0/8`, `169.254.0.0/16` ni `::1` ([NIST SP 800-41 §4.1.1](../fuentes/nist/sp800-41r1.txt) y [§4.1.2](../fuentes/nist/sp800-41r1.txt)).
- Nada pasa por la máquina hacia otra red ([NIST SP 800-41 §4](../fuentes/nist/sp800-41r1.txt)).

## Máquina

- Cada programa sale de los paquetes de Debian, salvo Caddy: `postgresql`, `postgresql-17-postgis-3` si la app usa PostGIS, `valkey-server`, `restic`, `sudo`, `python3`, `nftables`, `unattended-upgrades`, `systemd-timesyncd` y `ca-certificates`, con el que `deploy.py` comprueba el certificado de GitHub; `coturn` si usa TURN, `systemd-journal-remote` y `wireguard-tools` si envía su journal con `--logs`, y `openjdk-21-jre-headless` si tiene una pieza en Java ([java.md](java.md)).
- `caddy` sale de su repositorio APT: recibe cada petición de internet, el de Debian 13 es el 2.6.2, de 2022, y Debian da a sus paquetes en Go un soporte de seguridad limitado, con los arreglos en sus actualizaciones menores. [Debian 13, *Go- and Rust-based packages*](https://www.debian.org/releases/trixie/release-notes/issues.en.html#go-and-rust-based-packages)
- Antes de instalar, `packages.py` escribe en apt el repositorio de Caddy, `caddy.sources`, con su llave, `caddy.asc`, y la serie de [stack.md](../stack.md#despliegue), en `caddy.pref`: apt no instala otra serie ni el `caddy` de Debian, y sin la serie falla.
- `unattended-upgrades` instala también cada versión de Caddy de esa serie, por el origen de su repositorio en `/etc/apt/apt.conf.d/51caddy-upgrades`: sin él, Caddy queda en la versión que se instaló. Una serie nueva espera a que la fije stack.md.
- `sudo python3 packages.py` instala esos paquetes antes de `install.py`, con las mismas `--extension`, `--turn`, `--logs` y `--java` que recibe `install.py`. `packages.py --list` los nombra sin instalarlos, en cualquier sistema: quien despliega ve qué instala antes de entrar a la máquina. `--all` vale por todas las opciones: con `--list`, nombra todo lo que `packages.py` puede instalar.
- `sudo python3 swap.py` crea `/swapfile` con lo que le falta al swap para llegar a la memoria, como pide «Valkey», y lo agrega a `/etc/fstab`. Un `/swapfile` que no alcanza lo vuelve a crear, y con tanto swap como memoria no cambia nada.
- La máquina llega a `install.py` con los paquetes de `packages.py` y el swap de `swap.py`, e `install.py` falla si faltan, o si Caddy no es de la serie de `caddy.pref`.
- El host de cada superficie que la app tiene, `<dominio>`, `app.<dominio>` y `panel.<dominio>`, apunta a la máquina antes de `install.py`: Caddy obtiene el certificado de cada host por ACME, y reintenta mientras el host no la alcanza.
- `systemd-timesyncd` sincroniza la hora, e `install.py` falla si no está habilitado: las credenciales temporales de TURN, las sesiones y las fechas del journal dependen del reloj. `systemd-timesyncd` choca con cualquier otro paquete de hora, como `chrony`, y lo reemplaza.
- uv no está en Debian 13: `sudo python3 uv.py` lo instala en `/usr/local/bin/uv`, desde el release de GitHub de la versión de [stack.md](../stack.md#python), y falla sin instalar nada si el archivo no tiene el SHA-256 que `uv.py` fija para el procesador, `x86_64` o `aarch64`. Lo corre quien prepara la máquina, antes del primer `deploy.py`, y otra vez cuando cambia la versión: `deploy.py` crea el entorno de cada versión con `uv sync`, y otra versión de uv falla por el `required-version` del `pyproject.toml`.
- `unattended-upgrades` instala solo, cada día, las actualizaciones de Debian 13, y `install.py` lo enciende con `/etc/apt/apt.conf.d/20auto-upgrades`: una actualización de seguridad que espera a alguien deja la máquina expuesta mientras tanto.
- Un kernel nuevo corre solo después de reiniciar, y `unattended-upgrades` reinicia la máquina a las 04:00, en la hora de la máquina, cuando una actualización lo pide, con `Automatic-Reboot` y `Automatic-Reboot-Time` en `/etc/apt/apt.conf.d/52automatic-reboot`. El gancho del kernel de `unattended-upgrades` lo pide con `/var/run/reboot-required`. La app cae alrededor de un minuto y corta las llamadas y el respaldo en curso, y el siguiente respaldo corre igual.

## PostgreSQL

- `install.py` crea la base `<app>`, el rol `<app>` del servidor y el rol `<app>_owner`, dueño de la base. Ninguno es superusuario: las migraciones y la purga no saltan los permisos ni salen de la base.
- Cada rol entra por el socket con `peer`, sin contraseña, desde la cuenta de su nombre: el servidor con `<app>`, y las migraciones, la purga y el volcado con `<app>_owner`. Una cuenta entra solo como su rol, y ningún rol tiene contraseña.
- `install.py` crea además `<app>_read`, que lee todo lo que crea `<app>_owner`, salvo `event_log` ([fastapi.md](fastapi.md#registro-de-eventos)), y no cambia nada. La cuenta que administra entra solo como `<app>_read`, por `peer` con un mapa de `pg_ident.conf`, también por un túnel de `ssh` al socket: PostgreSQL ve la cuenta con la que `sshd` abre el túnel. Así se exploran los datos sin `sudo` y sin poder cambiarlos.
- `install.py` escribe la `database_url` del servidor en `<app>/`, y la del dueño en `<app>-migrate/`.
- `install.py` crea como `postgres` las extensiones que recibe con `--extension`: una extensión que no es *trusted*, como PostGIS, pide un superusuario.
- `install.py --development` deja la marca `/etc/<app>/development`, y sin `--development` la borra: una máquina que pasa a producción se instala otra vez sin la bandera.
- `database.py empty` corre solo en una máquina con la marca. Detiene `<app>.service`, borra la base y `/var/lib/<app>/files/`, cuyos archivos apuntan a filas que dejan de existir, y crea la base otra vez como `install.py`, con las extensiones que creó `postgres`. La deja vacía y sin migrar: al juntar las migraciones, la versión activa todavía tiene el historial viejo, y migrarla dejaría en `alembic_version` una revisión que la versión nueva no conoce.
- `database.py migrate` corre las migraciones y los seeders de la versión activa con `<app>-migrate@<versión>` y arranca el servidor. `database.py seed` los corre sin tocar el servidor, y `seed --mock` corre los datos de ejemplo de [fastapi.md](fastapi.md#seeders) con `<app>-mock@<versión>`, solo en una máquina con la marca. La unidad corre con la cuenta del servidor y su `StateDirectory=`: los datos de ejemplo son filas y archivos como los que escribe la app, y el dueño del esquema no puede escribir la carpeta de los archivos ([ADR-0157](../adr/0157-los-datos-de-ejemplo-entran-como-el-servidor.md)).

## Procesos

Estándares: [systemd.exec](../fuentes/systemd/systemd.exec.xml) de systemd y el [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

- Las unidades son las de `plantilla/infra/`, que `install.py` instala con el nombre y el dominio de la app, sin las de las piezas que no tiene.
- Cada pieza en Java corre en `<app>-java@<pieza>.service`, que `install.py --java <pieza>` habilita y `deploy.py` reinicia antes que el servidor ([java.md](java.md)).
- `install.py` escribe con la umask 022, sea cual sea la de quien despliega: cada servicio lee su configuración con su propia cuenta, y con la 077 Valkey no lee la suya y no arranca. Lo secreto lleva sus propios permisos, como `logs.conf` con 600 y `turnserver.conf` con 640.
- El servidor arranca con `uvicorn app.main:app --port 8000 --ws-max-size 65536 --ws-per-message-deflate false`: `fastapi run` no le pasa a Uvicorn las opciones de WebSocket. [fastapi-cli 0.0.32](https://raw.githubusercontent.com/fastapi/fastapi-cli/0.0.32/src/fastapi_cli/cli.py)
- `--port` es 8000 en todo producto: la máquina no aloja otro servidor.
- Caddy le llega al servidor por loopback: nadie salta los límites de Caddy, y Uvicorn cree las cabeceras `X-Forwarded-*` solo de loopback, su valor por defecto. [Uvicorn 0.54.0](https://raw.githubusercontent.com/encode/uvicorn/0.54.0/docs/settings.md)
- Uvicorn manda un ping cada 20 s y cierra la conexión que no responde en 20 s, sus valores por defecto. [Uvicorn 0.54.0](https://raw.githubusercontent.com/encode/uvicorn/0.54.0/docs/settings.md)
- `install.py` falla si `<app>` pasa de 22 caracteres o no cumple el nombre de una cuenta: `<app>-receiver` suma 9.
- `/run/<app>-receiver/` la crea `tmpfiles.d`: la escribe la cuenta de la receptora, que entra por `ssh`, y no una unidad.
- El timer del barrido de archivos de [fastapi.md](fastapi.md#archivos) corre `python -m app.tasks sweep` cada día.
- El timer de la purga de `event_log` de [fastapi.md](fastapi.md#registro-de-eventos) corre `python -m app.tasks purge` cada día. Su unidad corre con la cuenta `<app>_owner` y carga además `app_database_url` desde `<app>-migrate/`, como la de las migraciones.
- Otra tarea de [fastapi.md](fastapi.md#tareas-periódicas) corre en `<app>-task@<tarea>.service`, con la cuenta del servidor, y su timer, con el calendario de `install.py --task <tarea>=<OnCalendar>`, que va en `<app>-task@<tarea>.timer.d/calendar.conf`. Una tarea que ya no nombra ningún `--task` pierde su timer, y una con unidad propia, como `purge`, o con un calendario que systemd no lee, hace fallar `install.py` ([ADR-0151](../adr/0151-una-tarea-con-otro-calendario-corre-en-su-instancia-de-task.md)).
- Cada unidad queda con una exposición de 2.0 o menos en `systemd-analyze security`.
- Cada unidad activa toda opción de *Sandboxing* que no le impide funcionar ([systemd.exec, *Sandboxing*](../fuentes/systemd/systemd.exec.xml)).
- Cada unidad lleva `ProtectSystem=strict` y `ProtectProc=invisible` ([systemd.exec, *Sandboxing*](../fuentes/systemd/systemd.exec.xml) y [*Paths*](../fuentes/systemd/systemd.exec.xml)).
- Cada unidad filtra sus llamadas al sistema con una lista permitida que parte de `@system-service`, y solo con la arquitectura nativa ([systemd.exec, *System Call Filtering*](../fuentes/systemd/systemd.exec.xml)).
- Cada unidad que corre Python de la app permite además `mbind`, del grupo `@resources`: el OpenBLAS de numpy la llama al importarse, y una llamada negada mata el proceso con `SIGSYS` ([ADR-0149](../adr/0149-las-unidades-de-la-app-permiten-mbind.md)). [numpy 2.5.4](https://raw.githubusercontent.com/numpy/numpy/v2.5.4/pyproject.toml)
- Las cuentas de la app las crea `systemd-sysusers` desde el `sysusers.conf` de `plantilla/infra/`, que `install.py` instala antes de arrancar las unidades ([systemd.exec, *User/Group Identity*](../fuentes/systemd/systemd.exec.xml)).
- Un mensaje de WebSocket tiene a lo sumo 64 KiB: `--ws-max-size 65536` ([WebSocket Security, *Input Validation*](../fuentes/owasp/WebSocket_Security.md) y [*Denial-of-Service Protection*](../fuentes/owasp/WebSocket_Security.md)).
- El WebSocket no usa `permessage-deflate`: `--ws-per-message-deflate false` ([WebSocket Security, *WebSocket Protocol Configuration*](../fuentes/owasp/WebSocket_Security.md)).
- Uvicorn cierra con ping y pong la conexión WebSocket que se cayó ([WebSocket Security, *Denial-of-Service Protection*](../fuentes/owasp/WebSocket_Security.md)).
- El nombre de cada cuenta, como `<app>-receiver`, tiene a lo sumo 31 caracteres, solo letras ASCII, dígitos, `_` y `-`, y empieza por una letra o por `_` ([systemd.exec, *User/Group Identity*](../fuentes/systemd/systemd.exec.xml)).
- Ninguna cuenta fija usa el rango 61184–65519, el de las cuentas dinámicas ([systemd.exec, *User/Group Identity*](../fuentes/systemd/systemd.exec.xml)).
- La unidad del respaldo, con `DynamicUser=`, no deja archivos de su cuenta fuera de su `CacheDirectory=` ([systemd.exec, *User/Group Identity*](../fuentes/systemd/systemd.exec.xml)).
- Cada carpeta que una unidad escribe es su `StateDirectory=` o su `CacheDirectory=` ([systemd.exec, *Sandboxing*](../fuentes/systemd/systemd.exec.xml)).
- `KeyringMode=` queda en `private`, su valor por defecto en un servicio ([systemd.exec, *Process Properties*](../fuentes/systemd/systemd.exec.xml)).
- Ninguna unidad usa `LimitDATA=`, `LimitNOFILE=` ni `LimitAS=` ([systemd.exec, *Process Properties*](../fuentes/systemd/systemd.exec.xml)).

## Registros

- journald guarda en disco: `Storage=persistent` en `/etc/systemd/journald.conf.d/00-<app>.conf`. Con `auto`, el valor por defecto, guarda en memoria si falta `/var/log/journal`, sin avisar.
- `install.py` reinicia journald solo si cambió su archivo, y `uninstall.py` solo si lo borra: journald lee su configuración solo al arrancar, y systemd rechaza un sexto arranque en diez segundos, el límite por defecto de `DefaultStartLimitBurst=` y `DefaultStartLimitIntervalSec=`.
- El journal guarda a lo sumo 365 días, como `event_log` en [fastapi.md](fastapi.md#registro-de-eventos): también guarda direcciones IP de personas, como las que registra `sshd`. Son `MaxRetentionSec=365day` y `MaxFileSec=1day`: journald borra un archivo entero cuando su primera entrada pasa la retención, y con el mes de `MaxFileSec=` por defecto una entrada se borraría hasta un mes antes o un mes después.
- journald borra antes si el journal llega a `SystemMaxUse=`, que queda en su valor por defecto: el 10 % del disco, y a lo sumo 4G. La copia que vale es la de equipaggio, y un límite mayor le quitaría disco a la app. Lo que no salió todavía se pierde si el túnel sigue caído hasta llenar ese límite.
- PostgreSQL escribe en el journal, con `log_destination = 'syslog'` en `/etc/postgresql/17/main/conf.d/<app>.conf`, y su registro sale de la máquina con el resto. Con una carga extrema, syslog descarta mensajes en vez de frenar a PostgreSQL. Lo que escribe al arrancar, antes de leer la configuración, sigue en `/var/log/postgresql/`.
- Con `install.py --logs <host:puerto> --logs-key <llave> --logs-ip <dirección>`, el journal sale al registro central de equipaggio: `wg-quick@logs` abre un túnel de WireGuard con `/etc/wireguard/logs.conf`, y `systemd-journal-upload` envía a `http://10.77.0.1:19532`, el extremo de equipaggio. La dirección es una constante del túnel; la de la máquina, `--logs-ip`, la da equipaggio. Sin `--logs` no sale: la máquina de equipaggio se instala igual y no se envía a sí misma.
- Detectar que una máquina dejó de enviar le toca a equipaggio, por la hora de la última entrada que recibió de ella: cada máquina escribe en el journal al menos una vez por día, con el timer de la purga de `event_log`.
- Una máquina que envía no se reinstala sin `--logs`: `install.py` falla si existe `/etc/wireguard/logs.conf`, porque equipaggio ya registró la llave de su túnel. Para dejar de enviar, se apagan `wg-quick@logs` y `systemd-journal-upload` y se borra ese archivo.
- Equipaggio reconoce cada máquina por la llave de su túnel: el `systemd-journal-remote` de Debian 13 no verifica certificados de cliente, porque está compilado sin GnuTLS.
- `install.py` genera la llave privada del túnel la primera vez, la conserva en `logs.conf`, con permisos 600, e imprime la pública para registrarla en equipaggio. Con esa llave solo se agregan entradas: no se lee ni se borra lo que ya se envió.
- `systemd-journal-upload` reintenta sin límite, con `StartLimitIntervalSec=0` en `systemd-journal-upload.service.d/<app>.conf`: la unidad de Debian deja de reintentar después de cinco fallos rápidos, y no vuelve a enviar aunque equipaggio responda de nuevo.

## Respaldos

Estándares: [*Backup and Restore*](../fuentes/postgresql/backup.sgml) de PostgreSQL y NIST IR 7966, [*Security of Interactive and Automated Access Management Using Secure Shell (SSH)*](../fuentes/nist/ir7966.txt).

- El respaldo lleva el dump y `/var/lib/<app>/files/`, y sale de la máquina con `restic`, cifrado, hacia una receptora con `rest-server`. El código no va: está en los releases.
- La receptora pide el respaldo con `plantilla/receiver/`: abre `rest-server` en su puerto 8001 y un túnel `ssh -R` al 8001 del servidor, espera el resultado y cierra los dos.
- `rest-server` corre con `--append-only` y sin contraseña, y solo escucha en el loopback de la receptora: el servidor agrega respaldos, pero no borra ni reescribe los que hay, y restic los cifra.
- `backup.sh` y `backup.ps1` fallan si la receptora no tiene rest-server 0.14.0.
- La llave de la receptora no se limita por dirección: la receptora puede estar detrás de una IP dinámica, y su llave solo pide un respaldo.
- El comando comprueba el túnel antes de pedir el respaldo, y el respaldo se corta a las 4 h: un respaldo sin receptora no queda colgado.
- El primer respaldo crea el repositorio.
- Cada respaldo bueno cambia la fecha de `/var/lib/<app>/last-backup`, y el journal guarda cada corrida.
- El dump y `restic` son unidades distintas: `restic` solo puede leer, con `CAP_DAC_READ_SEARCH`.
- El dump no lleva los roles ni las extensiones: los crea `install.py`, y el dueño, que restaura, no puede crear una extensión que no es *trusted*.
- Se restaura en una máquina instalada con `install.py` y las mismas `--extension`: `restic restore` trae el dump y `/var/lib/<app>/files/`.
- El respaldo de la base es un `pg_dump` en formato custom, que corre antes de cada respaldo: `pg_restore` puede restaurar solo una parte ([Backup and Restore, *Handling Large Databases*](../fuentes/postgresql/backup.sgml)).
- `<app>_owner` restaura el dump con `pg_restore --exit-on-error` sobre la base que creó `install.py`: el primer error detiene la restauración ([Backup and Restore, *Restoring the Dump*](../fuentes/postgresql/backup.sgml)).
- El dump corre como `<app>_owner`, dueño de cada tabla: `pg_dump` tiene que leer todas las que respalda ([Backup and Restore, *SQL Dump*](../fuentes/postgresql/backup.sgml)).
- Antes de restaurar existen los roles que tienen objetos o permisos en la base: los crea `install.py` ([Backup and Restore, *Restoring the Dump*](../fuentes/postgresql/backup.sgml)).
- Después de restaurar corre `ANALYZE` ([Backup and Restore, *Restoring the Dump*](../fuentes/postgresql/backup.sgml)).
- La receptora entra con la cuenta `<app>-receiver`, solo con una llave de `/etc/<app>/receivers`, un archivo de `root`, y solo corre el comando que pide el respaldo, sin terminal ni otro túnel que el del 8001: una llave robada solo pide un respaldo ([NIST IR 7966 §5.1.2](../fuentes/nist/ir7966.txt)).

## SSH

Estándar: NIST IR 7966, [*Security of Interactive and Automated Access Management Using Secure Shell (SSH)*](../fuentes/nist/ir7966.txt).

- Esta configuración va en `/etc/ssh/sshd_config.d/00-<app>.conf`, que se lee antes que los archivos del proveedor, como `50-cloud-init.conf`: `sshd` se queda con el primer valor de cada opción. [OpenSSH 10.0](https://raw.githubusercontent.com/openssh/openssh-portable/V_10_0_P1/sshd_config.5)
- Una máquina nueva del proveedor puede aceptar solo la contraseña de `root`. Quien la prepara entra una vez con ella y corre `python3 authorize.py '<llave pública>'` como `root`, que agrega la llave a su `authorized_keys` una sola vez, con modos 700 y 600, y no escribe nada si la línea no es una llave. Desde ahí `packages.py`, `swap.py` e `install.py` entran con la llave.
- `install.py` crea la cuenta con `--admin`, en el grupo `sudo`, con las llaves de `--key` y la contraseña que pide al crearla. La primera vez corre como `root`, que entra con lo que da el proveedor; después, con `sudo` desde la cuenta, y `--admin` y `--key` solo agregan llaves.
- `sudo` pide la contraseña de la cuenta: una llave robada no da `root`.
- `install.py` bloquea la contraseña de `root`: la consola web del proveedor, que no pasa por `sshd`, recibe la cuenta y su contraseña.
- `install.py` falla si la máquina no tiene `sudo`, si una llave no es válida, si la cuenta queda sin llaves, si no recibe `--admin` y no lo lanza `sudo` desde una cuenta con llave, o si la cuenta es `<app>`, `<app>_owner` o `<app>-receiver`: `systemd-sysusers` conserva una cuenta que ya existe, y la app correría con una cuenta del grupo `sudo`.
- La cuenta que administra abre túneles locales, como el que lleva al socket de PostgreSQL de «PostgreSQL»: OpenSSH no abre uno hacia un socket si no abre también los de TCP. [OpenSSH 10.0](https://raw.githubusercontent.com/openssh/openssh-portable/V_10_0_P1/session.c)
- `sshd` solo acepta llaves ([NIST IR 7966 §3.4](../fuentes/nist/ir7966.txt) y [§5.1.1](../fuentes/nist/ir7966.txt)).
- `root` no entra: se entra con la cuenta que administra la máquina y `sudo` ([NIST IR 7966 §5.1.1](../fuentes/nist/ir7966.txt)).
- Las llaves de una cuenta viven en `/etc/ssh/authorized_keys/<cuenta>`, un archivo de `root` que la cuenta no puede cambiar, y `sshd` no las busca en otro lugar ([NIST IR 7966 §5.1.2](../fuentes/nist/ir7966.txt)).
- Una llave es Ed25519, ECDSA o RSA de 2048 bits o más, la de `--key` y la de `--signer`, e `install.py` falla con otra ([NIST IR 7966 §5.1.2](../fuentes/nist/ir7966.txt)).
- Una llave se reemplaza a más tardar a los 2 años: `--key` agrega la nueva, y la vieja se retira borrando su línea ([NIST IR 7966 §5.1.2](../fuentes/nist/ir7966.txt)).
- Una sesión sin tráfico, o una conexión sin canales, se cierra a los 30 minutos, salvo la sesión de la receptora, que espera su respaldo sin tráfico ([NIST IR 7966 §5.1.1](../fuentes/nist/ir7966.txt)).
- Los cifrados, los MAC y los intercambios de llaves son los que OpenSSH 10.0 trae por defecto ([NIST IR 7966 §5.1.1](../fuentes/nist/ir7966.txt)).
- La cuenta nace con dos llaves distintas, ninguna copia de la otra: la de la computadora de quien administra y una guardada fuera de ella. Perder la computadora no deja fuera ([NIST IR 7966 §5.1.2](../fuentes/nist/ir7966.txt)).
- Solo entran la cuenta que administra y la receptora: ninguna otra cuenta tiene llaves ([NIST IR 7966 §5.1.1](../fuentes/nist/ir7966.txt)).
- Ninguna cuenta redirige el agente ni X11, ni abre túneles, salvo los locales de la cuenta que administra y el de la receptora de «Respaldos» ([NIST IR 7966 §5.1.1](../fuentes/nist/ir7966.txt)).
- `sshd` acepta del cliente solo las variables de idioma y de color, `LANG`, `LC_*`, `COLORTERM` y `NO_COLOR`, las del `sshd_config` de Debian ([NIST IR 7966 §5.1.1](../fuentes/nist/ir7966.txt)).
- `sshd` registra la huella de la llave de cada entrada ([NIST IR 7966 §5.1.2](../fuentes/nist/ir7966.txt)).
- La llave de quien administra está protegida con una frase de paso ([NIST IR 7966 §5.1.2](../fuentes/nist/ir7966.txt)).
- Una llave que pudo filtrarse se reemplaza en el momento ([NIST IR 7966 §5.1.2](../fuentes/nist/ir7966.txt)).
- Ninguna cuenta de la máquina guarda una llave para entrar a otra máquina ([NIST IR 7966 §5.1.2](../fuentes/nist/ir7966.txt)).

## Valkey

Estándares: de Valkey, [*Administration*](../fuentes/valkey/admin.md) y [*Security*](../fuentes/valkey/security.md).

- El almacén en memoria de todas las piezas es Valkey.
- La instancia `valkey-server` del paquete queda apagada.
- `install.py` escribe en `<app>/` la `valkey_url` del socket de la app, `unix:///run/valkey-<app>/valkey-server.sock`.
- La política es `noeviction`, el valor por defecto: al llenarse, una escritura falla en vez de borrar un código o un contador. [Valkey 8.1.1](https://raw.githubusercontent.com/valkey-io/valkey/8.1.1/valkey.conf)
- Transparent Huge Pages no se apaga en la máquina: `disable-thp yes`, el valor por defecto de Valkey 8.1, las apaga solo para su proceso, sin cambiar los demás. [Valkey 8.1.1](https://raw.githubusercontent.com/valkey-io/valkey/8.1.1/valkey.conf)
- `vm.overcommit_memory = 1` va en `/etc/sysctl.d/valkey.conf`: Debian 13 ya no lee `/etc/sysctl.conf`. [Debian 13](https://www.debian.org/releases/trixie/release-notes/issues.en.html)
- La app tiene su instancia, `valkey-server@<app>`, sin TCP y con el socket `/run/valkey-<app>/valkey-server.sock`, que solo abre el grupo de la app: el resto de los procesos de la máquina no lee sus claves ([Security, *Security model*](../fuentes/valkey/security.md) y [*Network security*](../fuentes/valkey/security.md)).
- La máquina tiene al menos tanto swap como memoria, e `install.py` falla si tiene menos ([Administration, *Memory*](../fuentes/valkey/admin.md)).
- Valkey corre en Linux ([Administration, *Linux*](../fuentes/valkey/admin.md)).
- El kernel corre con `vm.overcommit_memory = 1` ([Administration, *Linux*](../fuentes/valkey/admin.md)).
- Cada instancia tiene un `maxmemory` explícito, el que recibe `install.py`, que descuenta de la memoria libre lo que Valkey ocupa además de los datos y su fragmentación ([Administration, *Memory*](../fuentes/valkey/admin.md)).
- Valkey corre con la cuenta `valkey` del paquete, que solo usa Valkey ([Security, *Code security*](../fuentes/valkey/security.md)).

## Versiones

- Se despliega un tag `vMAJOR.MINOR.PATCH`. El CI corre en ese tag los jobs de `ci.yml`, y solo si pasan construye un artefacto con el servidor, sus catálogos compilados, el build de la web y el jar de cada pieza en Java, y lo publica en un release de GitHub. El `.sha256` del release lleva el SHA-256 de cada archivo, con los instalables.
- El release es un borrador hasta que tiene el `.sha256`: un job que falla no deja publicado un release a medias.
- Cada versión queda en `/srv/<app>/releases/<versión>/`, y el enlace `/srv/<app>/current` apunta a la activa. Los datos quedan fuera de las versiones, en `/var/lib/<app>/`.
- El artefacto no lleva el entorno del servidor: cada versión lo crea en la máquina con `uv sync --locked --no-dev --no-editable --compile-bytecode`, con el Python 3.13 de Debian 13. Las unidades no pueden escribir en el entorno, por `ProtectSystem=strict`, así que sin el bytecode compilado cada proceso vuelve a compilar cada módulo que importa: en concordia, una vuelta de una tarea baja de 1,8 s a 1,2 s de CPU. La app va sin modo editable, dentro del entorno, para que su código también quede compilado. Cuesta unos 10 s más por versión y unos 100 MB más de disco. [uv 0.13](https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode)
- `releases/` guarda las cinco versiones más recientes y la activa: las demás siguen en sus releases de GitHub.
- `deploy.py` con una versión que `releases/` guarda la vuelve a activar sin instalarla, si sus heads de Alembic son los de la activa: así se vuelve atrás ante una versión mala. Si no lo son, falla: su código correría sobre un esquema que no conoce. Baja otra vez del release los instalables de esa versión, con el `.sha256` firmado, porque al publicarlos salen de su carpeta. La versión activa no se vuelve a instalar.
- El `.sha256` del release se firma fuera de GitHub con `ssh-keygen -Y sign`, y el servidor solo instala el artefacto y los instalables que ese `.sha256` nombra, si lo firma una llave de `/etc/<app>/allowed_signers`: una cuenta de GitHub comprometida después de la firma no alcanza para desplegar otro archivo ni una versión anterior.
- `install.py --signer` agrega cada llave que firma a `allowed_signers`, solo para el espacio de nombres `deploy`, el que firma y comprueba `deploy.py`. Una máquina nueva necesita dos: la de la computadora de quien firma y una guardada fuera de ella. Perder la computadora no impide desplegar. Después, `--signer` solo agrega llaves, y una llave se retira borrando su línea.
- `<app>-deploy`, el `deploy.py` que instala `install.py`, instala un tag en el servidor y se lanza por `ssh`, no desde el CI. `install.py` lo instala con el dueño del repositorio en GitHub que recibe con `--owner`. Con `--private`, el script baja el release con el token de `<app>-deploy/`, cada `--desktop` nombra un instalable que el release trae: `linux`, `windows` o `macos`, y cada `--mobile`, una app de `mobile/` con descarga directa. Reinicia `<app>.service`, la única unidad del servidor.
- Las migraciones y los seeders corren en la unidad `<app>-migrate@<versión>.service`, con `python -m app.tasks migrate` y las credenciales del servidor, porque `alembic/env.py` lee `Settings`, salvo `database_url`, que es la del rol dueño del esquema. El rol del servidor no tiene DDL: un error o una inyección en la app no cambian el esquema.
- Una versión trae migraciones si sus heads de Alembic no son los de la activa, o si no hay una activa.
- Si la versión trae migraciones, el servidor se detiene antes de migrar: el código anterior no corre sobre la base migrada. Si una migración o un seeder falla, la versión se borra y vuelve la anterior, porque `app.tasks migrate` aplica todas las migraciones y los seeders en una sola transacción.
- Si `GET /api/health` de la versión nueva no responde 204 en 30 intentos, uno por segundo, `current` vuelve a la anterior solo si no hubo migraciones: el código anterior no corre sobre la base migrada. Una versión nueva que vuelve así se borra, y el mismo tag se puede volver a desplegar.
- En un repositorio privado, el release se baja con un token de GitHub de solo lectura, cifrado con `systemd-creds`.
- Caddy sirve el build de cada superficie web, `web/`, `panel/` y `landing/`, desde `current/<pieza>/`. La PWA es `web/`. Una pieza sin `index.html` sirve `200.html` también en su raíz. Una página prerenderizada es `<página>.html` o `<página>/index.html`: una carpeta sin `index.html`, como la del `__data.json` de una página con datos, no es una página. Una pieza sin `200.html` responde a una ruta que no existe con su `404.html` y un 404, con las mismas cabeceras ([ADR-0142](../adr/0142-una-pieza-prerenderizada-responde-404-con-su-pagina.md)).
- El CI construye del mismo tag los instalables de `desktop/` y los adjunta al release como `desktop-<sistema>.<ext>`. Caddy los sirve con ese nombre, igual en cada versión, desde `/srv/<app>/downloads/`, fuera de `releases/`: la landing enlaza siempre al mismo nombre.
- El CI sube a la pista interna de Google Play la versión de cada app de `mobile/` del mismo tag, con `scripts/play.py`, y adjunta al release, como `<pieza>.apk`, el APK universal que Play genera de ella ([transversal.md](transversal.md#distribución)). Caddy lo sirve con ese nombre desde `/srv/<app>/downloads/`, como los instalables de `desktop/`. La versión pasa a producción en Play Console.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Valkey 8.1, también en el CI | [scripts/verificar.py](../scripts/verificar.py) |
| `scripts/play.py` igual al de la plantilla | [scripts/verificar.py](../scripts/verificar.py) |
| Que cada host sirve su pieza con `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `frame-ancestors`, `Referrer-Policy`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Resource-Policy` y `Permissions-Policy`, sin `Server` ni `Cross-Origin-Embedder-Policy`, y su HTML con su charset; que HTTP redirige con 308; que solo la landing se indexa; que una pieza sin `index.html` sirve `200.html`; que una página con datos se sirve aunque tenga su carpeta, y que una pieza sin `200.html` responde con su `404.html` y un 404; que `/api/*` lleva las mismas cabeceras y `no-store`; que un cuerpo que pasa su límite recibe 413 y no llega entero al servidor, y que `/downloads/` sirve los instalables | El `Caddyfile` y los sitios en el Caddy que instala `packages.py`, con certificados propios de Caddy y un servidor en el 8000 que registra lo que le llega, con [scripts/infra/caddy.sh](../scripts/infra/caddy.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que una máquina nueva necesita dos `--signer`, que cada llave firma solo para `deploy` y que después solo se agregan; que `install.py` falla sin `systemd-timesyncd` habilitado, sin `ca-certificates` o con un Caddy de otra serie; que apt lee el reinicio automático de las 04:00; que `credentials.py` cifra cada campo en su carpeta y con el nombre que carga su unidad, escribe solo lo que recibe y no escribe nada si una línea está mal; que Valkey no abre TCP, que su socket solo lo abre el grupo de la app, que tiene su `maxmemory` con `noeviction` y `vm.overcommit_memory = 1`, y que la instancia del paquete queda apagada; que `root` no tiene contraseña y una cuenta de la app no puede ser la que administra; que `install.py` falla con un `<app>` que no da nombres de cuenta válidos; y que las llaves de la cuenta quedan en un archivo de `root` y una llave débil falla | `install.py` en un Debian 13 con systemd, arrancado con `systemd-nspawn`, con [scripts/infra/install.sh](../scripts/infra/install.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que `packages.py --list` nombra los paquetes de cada opción sin instalarlos, que `--all` nombra los de todas, y que sin `--list` los instala, con Caddy de su repositorio, en la serie de `caddy.pref`, y su origen en `unattended-upgrades` | `packages.py` en el apt de Debian 13, con [scripts/infra/packages.sh](../scripts/infra/packages.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que `swap.py` deja tanto swap como memoria con un `/swapfile` de `root` y modo 600, que lo anota una sola vez en `/etc/fstab`, que vuelto a correr no cambia nada y que rehace un `/swapfile` que no alcanza | `swap.py` en el runner de GitHub, que tiene menos swap que memoria, con [scripts/infra/swap.sh](../scripts/infra/swap.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que `uv.py` instala en `/usr/local/bin`, de `root`, la versión de uv que pide cada `pyproject.toml` de la plantilla, también sobre sí misma, y que un archivo que no tiene su SHA-256 no instala nada y deja el uv que había | `uv.py` en el Python de Debian 13, con el archivo de GitHub y el mismo archivo con un byte más servido desde la máquina, con [scripts/infra/uv.sh](../scripts/infra/uv.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que `deploy.py` migra y publica la primera versión, con las credenciales de `credentials.py`, que los timers de la purga y el barrido son diarios y sus unidades terminan bien sobre esa versión, que una tarea de `--task` corre en su calendario con la cuenta del servidor y la reinstalación sin ella le quita el timer, que no vuelve a instalar la versión activa, vuelve a la anterior y borra la nueva si no responde y no trae migraciones, borra la versión cuya migración falla, vuelve a activar una versión guardada con sus instalables solo si sus heads son los de la activa, no instala nada firmado por una llave ajena ni con el `.sha256` de otra versión, conserva las cinco versiones más recientes, y que en un repositorio privado despliega solo con `--private` y su token, que no sigue la redirección de una descarga a otro host; que `database.py empty` falla sin la marca de `--development` y con ella deja la base vacía, con las extensiones de `install.py`, y sin los archivos, que `migrate` vuelve a migrar la versión activa, que cada despliegue corre los seeders sin duplicar filas y un seeder que falla deshace las migraciones y deja la versión anterior, que `seed --mock` corre solo con la marca, y que la cuenta que administra lee como `<app>_read`, también por un túnel al socket, y no cambia nada | El `deploy.py` y el `database.py` que instala `install.py`, con los releases servidos desde la misma máquina en vez de GitHub, sus descargas redirigidas a otro host, y los paquetes del servidor en la caché de uv, con [scripts/infra/deploy.sh](../scripts/infra/deploy.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que sin túnel no arranca un respaldo, que la receptora guarda el dump y los archivos y el servidor no los borra, que su llave no abre una terminal ni otro túnel, que un respaldo cortado mientras tiene su lock no frena el siguiente, que un respaldo que llega a su límite falla, y que lo que trae `restic restore` vuelve sobre la base que crea `install.py` y se analiza | `plantilla/receiver/backup.sh` desde otro namespace de red, con rest-server 0.14.0 y el límite reducido de 4 h a 5 s, con [scripts/infra/backup.sh](../scripts/infra/backup.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que `uninstall.py --dry-run` no cambia nada; que `database` borra la base, sus roles, sus credenciales y su línea de `pg_hba.conf` y deja lo demás de la app; que `app` borra cada unidad, sitio, credencial, cuenta y carpeta de la app; que `machine` borra uv y los archivos de `install.py` para la máquina, deja los paquetes y lo que `install.py` sobrescribió en ellos, y que `install.py` vuelve a instalar la app sobre ella; y que cada nivel deja la cuenta que administra, sus llaves, `00-<app>.conf` y `root` bloqueado | `uninstall.py` en un Debian 13 arrancado por `systemd-nspawn`, después de `install.py`, con [scripts/infra/uninstall.sh](../scripts/infra/uninstall.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que `authorize.py` agrega la llave a `/root/.ssh/authorized_keys` una sola vez, con modos 700 y 600, conserva las que había y no escribe nada si la línea no es una llave | `authorize.py` en el OpenSSH y el Python de Debian 13, con [scripts/infra/authorize.sh](../scripts/infra/authorize.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| `00-<app>.conf` y `<app>-receiver.conf` que lee `sshd` | `sshd -t` en el OpenSSH de Debian 13, en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Solo llaves y sin `root`, aunque un archivo del proveedor permita contraseñas; las llaves en `/etc/ssh/authorized_keys/`; sin redirecciones salvo los túneles locales; el cierre a los 30 minutos, y la receptora con su llave, su comando, su túnel y sin cierre de su sesión | `sshd -T` con un `50-cloud-init.conf` que las permite, en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Los roles de «PostgreSQL», y que el dump del dueño se restaura en la base que crea `install.py` | Las cuentas de `sysusers.conf`, `create_database` de `database.py` y el `pg_dump` de la unidad, en el PostgreSQL y el PostGIS de Debian 13, en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que numpy importa con el filtro de llamadas de cada unidad que corre la app, y no sin su excepción de `mbind` | Python con el filtro de cada unidad, por `systemd-run`, con [scripts/infra/seccomp.sh](../scripts/infra/seccomp.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Exposición de cada unidad | `systemd-analyze security --offline=yes --threshold=20 <unidad>`, en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Los puertos que entran, que no entra un origen que nunca es válido ni una petición de TURN desde un túnel, y que lo que sale no se filtra, de «Firewall» | `nftables.conf` cargado en el nftables de Debian 13, con y sin `turn.nft`, con conexiones desde otro namespace de red, en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que coturn releva hacia internet, y no hacia una red privada o loopback, con otro secreto ni pasada la cuota, y que `denied-peer-ip` sigue los registros de IANA y niega 6to4 | `turnserver.conf` en el coturn de Debian 13, con `turnutils_uclient` desde otro namespace de red, y [scripts/infra/peers.py](../scripts/infra/peers.py), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que el journal llega al registro central por el túnel de la plantilla, en el archivo de la dirección de su llave, y que otra llave con la misma dirección no llega | `logs.conf` y `journal-upload.conf` con el `systemd-journal-upload` y el WireGuard de Debian 13, desde otro namespace de red, con [scripts/infra/logs.sh](../scripts/infra/logs.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que `install.py --logs` exige sus tres banderas juntas, envía el journal y el registro de PostgreSQL por el túnel, conserva la llave, falla sin `--logs` en una máquina que envía e instala aunque quien despliega tenga la umask 077; que el uploader reintenta sin quedar en `failed`; y que journald borra una entrada a más tardar un archivo después de su retención | `install.py` en un Debian 13 con systemd, arrancado con `systemd-nspawn` y con la umask 077, con un extremo en otro namespace de red y la retención reducida a 20 s con archivos de 5 s, con [scripts/infra/install-logs.sh](../scripts/infra/install-logs.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que detrás de un NAT dos clientes se alcanzan solo con el `external-ip` de `install.py --turn-ip` | `turnserver.conf` en el coturn de Debian 13, detrás de un NAT de nftables, con la dirección privada que da `private_ip` de `install.py`, en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
