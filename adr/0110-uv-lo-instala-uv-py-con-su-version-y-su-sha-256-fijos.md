# ADR-0110 · uv lo instala `uv.py`, con su versión y su SHA-256 fijos

- **Estado:** Aceptada
- **Fecha:** 2026-10-31
- **Alcance:** «Máquina» de [`plataformas/despliegue.md`](../plataformas/despliegue.md),
  `plantilla/infra/` y `scripts/infra/`

## Contexto

El [ADR-0090](0090-la-maquina-es-debian-13-sus-programas-salen-de-sus-paquetes-y-uv-tiene-una-sola-version-exacta.md)
fija una sola versión de uv, que en el servidor sale del release de GitHub con su SHA-256
comprobado, pero ningún programa de canone la instalaba. Los paquetes y el swap los pone quien
prepara la máquina, con lo que trae Debian 13; uv no está en Debian 13, y su versión y su SHA-256
son reglas de canone. `deploy.py` corre `uv sync` en cada versión, y sin uv no despliega.

## Decisión

1. `plantilla/infra/uv.py` instala uv en `/usr/local/bin/uv`, con `sudo python3 uv.py`. Lo corre
   quien prepara la máquina, antes del primer `deploy.py`, y otra vez cuando cambia la versión.
2. `uv.py` fija la versión y el SHA-256 del archivo de cada procesador, `x86_64` y `aarch64`.
   Descarga el archivo de esa versión del release de GitHub, y falla sin instalar nada si no tiene
   ese SHA-256 o si el procesador es otro.
3. Escribe el binario junto a `/usr/local/bin/uv` y lo renombra encima: el uv que había sigue
   entero hasta que el nuevo lo reemplaza.
4. `scripts/infra/uv.sh` comprueba en `infra.yml` que el uv instalado es la versión que pide el
   `pyproject.toml` de `plantilla/server/`, y que un archivo con otro SHA-256 no instala nada.

## Consecuencias

- Subir la versión de uv cambia también `VERSION` y `CHECKSUMS` de `uv.py`, además de lo que
  nombra el ADR-0090. Si `uv.py` queda con otra versión, `uv.sh` falla.
- `uv.sh` descarga de GitHub: el job `uv` de `infra.yml` necesita internet, a diferencia de los
  de `install`.
- `install.py` no comprueba uv. Si falta o es otra versión, `deploy.py` falla en `uv sync`, antes
  de publicar nada.
- Probado en Debian 13.7 con `systemd-nspawn`: `uv.sh` pasa, y falla con otro SHA-256 en
  `uv.py` y con otra versión.

## Descartado

- **Que lo instale `install.py`:** `install.py` comprueba lo que trae la máquina y no instala
  programas de afuera, y cada prueba de `install.py` corre sin internet.
- **Comprobar contra el `.sha256` del mismo release:** sale del mismo lugar que el archivo, y quien
  cambie uno puede cambiar el otro.
- **El instalador de astral.sh:** corre un script que se descarga en el momento, sin un SHA-256
  fijo en canone.
