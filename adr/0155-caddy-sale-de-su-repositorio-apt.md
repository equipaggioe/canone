# ADR-0155 · Caddy sale de su repositorio APT, y no de los paquetes de Debian 13

- **Estado:** Aceptada
- **Fecha:** 2026-11-15
- **Alcance:** [`stack.md`](../stack.md), «Despliegue»; [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Caddy» y «Máquina»; `packages.py`, `install.py` y el `Caddyfile` de `plantilla/infra/`; `scripts/infra/packages.sh` e `install.sh`; `.github/workflows/infra.yml`

## Contexto

El [ADR-0090](0090-la-maquina-es-debian-13-sus-programas-salen-de-sus-paquetes-y-uv-tiene-una-sola-version-exacta.md)
sacó cada programa de la máquina de los paquetes de Debian 13, Caddy incluido. El
[ADR-0071](0071-cada-app-tiene-su-instancia-de-valkey-y-cada-superficie-su-host-en-caddy.md),
punto 4, respondió con su propio 413 a un `Content-Length` que pasa el límite, porque Caddy 2.6.2
responde 502 cuando `request_body` corta ese cuerpo. Descartó el repositorio oficial porque el
servidor instalaría la versión de ese día, no la que valida el CI.

Comprobado el 2026-11-15 en sources.debian.org: trixie tiene `2.6.2-12+deb13u1`, de una versión de
octubre de 2022; trixie-backports, `2.11.2-1~bpo13+1`, y upstream va en la 2.11.9. Las notas de
Debian 13 (§5.2.3.2, *Go- and Rust-based packages*) dicen que los paquetes en Go tienen *«limited
security support»*, y que sus arreglos suelen llegar solo en las actualizaciones menores. Caddy
está en Go y es el que recibe cada petición de internet.

En el código de Caddy 2.11.9, `request_body` responde 413 a un `Content-Length` que pasa
`max_size`, antes de pasar la petición (`modules/caddyhttp/requestbody/requestbody.go`).

## Decisión

1. Caddy sale del repositorio APT de Caddy, `https://dl.cloudsmith.io/public/caddy/stable/deb/debian`,
   firmado con su llave, que la plantilla versiona en `caddy.asc`.
2. `packages.py` escribe en apt el repositorio, la llave y lo demás de esta decisión antes de
   instalar los paquetes.
3. `unattended-upgrades` instala también las versiones de Caddy, por el origen
   `cloudsmith/caddy/stable` en `51caddy-upgrades`.
4. `caddy.pref` fija la serie de `stack.md`, `2.11.*`: `unattended-upgrades` instala cada versión
   de la serie, y una serie nueva espera a que `stack.md` la fije. Cualquier otra versión, de otra
   serie o de Debian, lleva prioridad -1: si la serie no está, apt falla en vez de instalar otra.
5. `install.py` falla si el Caddy instalado no es de la serie de `caddy.pref`.
6. El `Caddyfile` no responde su propio 413: lo responde `request_body`.
7. El CI prueba el `Caddyfile` en el Caddy que instala `packages.py`, y `packages.sh` comprueba que
   el instalado es de la serie de `caddy.pref` y que su origen está en `unattended-upgrades`.

## Consecuencias

- Caddy recibe los arreglos el día que los publica upstream, sin esperar a Debian.
- La objeción del ADR-0071 queda a medias: el CI valida la serie, pero `unattended-upgrades`
  instala cada versión nueva de la serie sin que el CI la haya probado antes.
- Cada límite de cuerpo queda escrito una sola vez en el `Caddyfile`, en `request_body`.
- `packages.py` necesita llegar a `dl.cloudsmith.io`, además de a Debian.
- Pasar a otra serie es cambiar `stack.md` y `caddy.pref` a la vez.
- El job `caddy` del CI instala los paquetes base de `packages.py`, no solo Caddy.

## Descartado

- **El Caddy de Debian 13:** cuatro años de atraso, con soporte de seguridad limitado, en la pieza
  expuesta a internet.
- **trixie-backports:** sigue siendo Debian, pero backports no garantiza las actualizaciones de
  seguridad y va detrás de upstream.
- **Una versión exacta de Caddy, en el repositorio o en el release de GitHub, como rest-server:**
  el CI validaría la misma versión, pero cada arreglo esperaría a que alguien cambie `stack.md` y
  vuelva a instalar.
- **La serie con prioridad 990 sola:** sin la serie, apt instalaría en silencio otra versión con
  prioridad 500.
