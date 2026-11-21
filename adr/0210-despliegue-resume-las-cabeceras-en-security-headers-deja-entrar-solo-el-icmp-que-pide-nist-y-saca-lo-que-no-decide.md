# ADR-0210 · `despliegue.md` resume las cabeceras en *Security Headers*, deja entrar solo el ICMP que pide NIST, y saca lo que no decide nada

- **Estado:** Aceptada. El usuario pidió aplicar los veredictos de la revisión (2026-11-21). Los valores de la retención de los respaldos no los confirmó: quedan en [pendientes/retencion-de-respaldos.md](../pendientes/retencion-de-respaldos.md)
- **Fecha:** 2026-11-21
- **Alcance:** [plataformas/despliegue.md](../plataformas/despliegue.md), `plantilla/infra/Caddyfile`, `plantilla/infra/nftables.conf`, `scripts/infra/` y `scripts/verificar.py`

## Contexto

Se revisó `despliegue.md` con los cinco pasos de [plataformas/README.md](../plataformas/README.md#revisión). Cada script de `scripts/infra/` corrió en un Debian 13 como el de `infra.yml`, con systemd 257.13, Caddy 2.11.9, nftables 1.1.3, OpenSSH 10.0p1 y PostgreSQL 17, y se rompió a propósito la convención de cada fila de «Cumplimiento» para ver si su herramienta falla. Lo comprobado:

- No fallaban con su convención rota: `java.sh` sin el reinicio de la pieza en `deploy.py`, que solo buscaba la tupla `JAVA`; `install.sh` sin `passwd --lock root`, porque la imagen de debootstrap ya trae `root` bloqueado, y con la instancia de Valkey del paquete deshabilitada pero corriendo; `caddy.sh` sin `noindex` en `/api/*`, porque solo miraba `/api/*` del host de la web; `packages.sh` sin `restic` en la lista base; `uv.sh` con otra versión de uv en `qt/pyproject.toml`, porque solo leía la del servidor. `nftables.sh` prueba como origen inválido solo `169.254.0.0/16`.
- Caddy deja pasar el `X-Powered-By` que pone el servidor, y conserva el `Cache-Control` que el servidor puso.
- Con el `nftables.conf` anterior, la máquina respondía a un pedido de *timestamp* de ICMPv4, tipo 13. Con el nuevo no responde, y siguen respondiendo el ping por IPv4 y por IPv6 y el vecino IPv6.
- En la corrida 44874298451 de `infra.yml`, sin la excepción de `capset` Chromium quedó colgado una hora en vez de morir; en local murió. El timer `minutely` de la tarea arrancaba otra vuelta mientras la prueba miraba el resultado.
- OpenSSH 10.0 con el `sshd.conf` de la plantilla registra la huella de la llave con su `LogLevel` por defecto, y no abre un túnel a un socket con `AllowTcpForwarding no`.
- El *Security Headers* del cheat sheet de OWASP recomienda `Cross-Origin-Embedder-Policy: require-corp`; §4.1.4 de NIST SP 800-41 pide negar el ICMP que no se permite expresamente, y para ICMPv6 remite al RFC 4890; *Process Properties* de systemd.exec no toma posición sobre `LimitDATA=`, `LimitNOFILE=` ni `LimitAS=`; §5.1.1 de NIST IR 7966 pide cifrados aprobados, y OpenSSH 10.0 trae por defecto ChaCha20-Poly1305, que NIST no aprueba.

## Decisión

1. Las cabeceras que pone Caddy se escriben en una sola convención, que nombra *Security Headers* del *HTTP Security Response Headers Cheat Sheet* y dice lo que no sigue: `Cross-Origin-Embedder-Policy`, y la CSP, que lleva solo `frame-ancestors 'none'`. `Set-Cookie` y `Access-Control-Allow-Origin` siguen a `autenticacion.md`, y las cabeceras de una descarga, a `fastapi.md`. Caddy quita también `X-Powered-By`. `caddy.sh` comprueba la parte entera: la `Permissions-Policy` que escribe `install.py`, la ausencia de las cabeceras que la parte desaconseja, `X-Robots-Tag` en `/api/*` de los tres hosts, y el `Cache-Control` del servidor.
2. De ICMP entran el tipo 3 y el ping de ICMPv4, y de ICMPv6 lo que el RFC 4890 §4.4.1 y §4.4.2 no deja descartar (NIST SP 800-41 §4.1.4). Reemplaza el punto 5 del [ADR-0093](0093-lo-que-entra-se-niega-por-defecto-con-nftables-y-lo-que-sale-no-se-filtra.md) en lo que toca a ICMP.
3. Salen las convenciones que no deciden nada: el 308 de HTTP a HTTPS, que es el valor por defecto de Caddy; el paso del upgrade de WebSocket, que Caddy hace sin configurarse; los hosts que apuntan a la máquina antes de `install.py`, porque Caddy reintenta; Valkey en Linux; el loopback que coturn niega por defecto, y `LimitDATA=`, `LimitNOFILE=` y `LimitAS=`, que su origen no trata.
4. Pasan a convenciones propias, sin origen: que Caddy no corte por tiempo una conexión WebSocket, porque el cheat sheet pide un tiempo de lectura; los cifrados por defecto de OpenSSH 10.0, porque NIST no aprueba algunos, y la cuenta que nace con dos llaves. El nombre de un programa en `/usr/local/sbin` empieza por el de la app, como convención propia aparte de §3.16.1 de FHS.
5. Las convenciones no enlazan ADR. `<app>-browser@` permite `setpriority`, `pkey_alloc` y `capset` porque sin una de ellas Chromium no abre la página: puede morir o quedar colgado. El comando de Uvicorn no repite los flags de WebSocket, la exposición de las unidades no se repite en una convención de `<app>-browser@`, y la medición del bytecode compilado queda en el [ADR-0152](0152-el-entorno-del-servidor-se-instala-compilado-y-sin-modo-editable.md).
6. El árbol de «Proyecto» va después de sus convenciones y lleva `<pieza>.apk`, los `calendar.conf` de `--task` y `--browser`, y `/root/.cache/uv`.
7. Las pruebas comprueban lo que dice su fila: `java.sh` reinicia la pieza con `restart()` de `deploy.py`; `install.sh` le da a `root` una contraseña antes de instalar y mira que la instancia del paquete no corra; `packages.sh` compara la lista base con la de «Máquina»; `uv.sh` lee cada `pyproject.toml` de la plantilla; `browser.sh` detiene el timer antes de mirar los resultados, y una vuelta sin una excepción termina a los 2 minutos. La fila de `nftables.sh` nombra el único origen inválido que prueba, y la del respaldo deja «y se analiza», que hacía la propia prueba.
8. `scripts/apple.py` es canónico, como `play.py`, y `verificar.py` compara la copia de cada repositorio.

## Consecuencias

- La máquina ya no responde al ICMPv4 que no es el tipo 3 ni el ping, como el *timestamp* o el *redirect*. No se probó en una VPS real que reciba su ruta IPv6 por *router advertisement*, aunque el tipo 134 entra.
- Una cabecera nueva de *Security Headers* que no esté en la convención falla en `caddy.sh` si se pone distinta de la recomendación.
- `seccomp.sh` borra su venv al terminar.

## Descartado

- **Escribir cada cabecera en su convención:** repite la parte de OWASP que `caddy.sh` hace cumplir entera.
- **Dejar ICMP entero sin origen, como excepción:** la razón que daba, que IPv6 encuentra a sus vecinos con ICMPv6, justifica solo los tipos del RFC 4890.
- **Hacer que `browser.sh` exija que Chromium muera:** en CI se colgó una vez; lo que importa es que sin la excepción no abre la página.
