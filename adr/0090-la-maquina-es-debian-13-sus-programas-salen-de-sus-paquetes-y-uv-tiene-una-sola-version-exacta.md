# ADR-0090 · La máquina es Debian 13, sus programas salen de sus paquetes, y uv tiene una sola versión exacta

- **Estado:** Aceptada
- **Fecha:** 2026-10-26
- **Alcance:** «Máquina» de [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Proyecto»
  de [`plataformas/python.md`](../plataformas/python.md), los `pyproject.toml` y los workflows de
  `plantilla/`, y `scripts/verificar.py`

## Contexto

`despliegue.md` tomaba las versiones de Caddy, PostgreSQL, Valkey, OpenSSH y systemd de Debian 13,
pero no decía de dónde salía cada programa, y quien instala no sabía qué poner en la máquina antes
de `install.py`. Cada versión crea su entorno en el servidor con `uv sync`
([ADR-0091](0091-cada-version-crea-su-entorno-en-el-servidor-y-una-migracion-se-reconoce-por-sus-heads.md)),
y uv no está en Debian 13: packages.debian.org lo tiene solo en forky y sid, en la 0.9.17. El CI
instalaba la última versión de uv, y quien desarrolla, la que tuviera: el servidor no habría creado
el entorno con la versión que probó el CI.

## Decisión

1. La máquina es Debian 13, y cada programa sale de sus paquetes: `caddy`, `postgresql`,
   `postgresql-17-postgis-3` si la app usa PostGIS, `valkey-server`, `restic`, `sudo` y `python3`,
   y `coturn` si usa TURN.
2. uv tiene una sola versión exacta, la misma en el CI, en la máquina de quien desarrolla y en el
   servidor. En el servidor sale del release de GitHub de esa versión, con su SHA-256 comprobado.
3. La versión es la 0.13.5, la más nueva, y va en «Proyecto» de `python.md`.
4. Cada `pyproject.toml` la declara con `required-version = "==0.13.5"` en
   `[tool.uv]`, y `setup-uv` la lee con `version-file`.
5. `verificar.py` comprueba que cada `pyproject.toml` del repositorio la declare.

## Consecuencias

- Otra versión de uv falla antes de hacer nada. Comprobado sobre una copia de
  `plantilla/server/`: uv 0.8.17 responde «Required uv version `==0.13.5` does not match the
  running version `0.8.17`», y uv 0.13.5 corre `uv sync --locked --no-dev` con el `uv.lock` de la
  plantilla sin cambiarlo.
- Sin `version-file`, `setup-uv` v6 busca `required-version` solo en la raíz del repositorio, y el
  `pyproject.toml` de cada pieza está en su carpeta: instalaría la última versión, y uv fallaría.
- Quien desarrolla con otra versión de uv la cambia con `uv self update 0.13.5`.
- Subir de versión cambia `python.md`, `UV` de `verificar.py` y cada `pyproject.toml` en la misma
  pasada.
- Comprobado en packages.debian.org: trixie trae `caddy` 2.6.2, `postgresql` 17,
  `postgresql-17-postgis-3` 3.5.2, `valkey-server` 8.1.1, `restic` 0.18.0, `sudo` 1.9.16,
  `python3` 3.13.5 y `coturn` 4.6.1.

## Descartado

- **El uv de forky o sid:** no es de Debian 13, la versión de la máquina.
- **uv con `pip install`:** el Python de Debian 13 está marcado como *externally managed*, y
  `pip` no instala fuera de un entorno virtual.
- **La versión en el `version:` de `setup-uv`:** la misma versión en dos lugares, que se separan, y
  quien desarrolla no la ve.
