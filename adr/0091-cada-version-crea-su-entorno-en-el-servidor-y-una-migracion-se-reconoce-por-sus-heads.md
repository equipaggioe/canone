# ADR-0091 · Cada versión crea su entorno en el servidor, y una migración se reconoce por sus heads

- **Estado:** Aceptada
- **Fecha:** 2026-10-26
- **Alcance:** «Versiones» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/scripts/deploy.py`

## Contexto

`deploy.py` se escribió al implementar el
[ADR-0068](0068-una-version-se-despliega-desde-un-tag-con-un-artefacto-y-un-script.md), y tres de
sus elecciones no las decidió nadie ni las escribía la página: dónde se crea el entorno del
servidor, cuándo una versión trae migraciones y cuánto se espera la ruta de salud.

## Decisión

1. El artefacto no lleva el entorno del servidor: cada versión lo crea en la máquina con
   `uv sync --locked --no-dev`, con el Python 3.13 de Debian 13.
2. Una versión trae migraciones si sus heads de Alembic no son los de la activa, o si
   no hay una activa.
3. La versión nueva falla si `GET /api/health` no responde 204 en 30 intentos, uno
   por segundo.

## Consecuencias

- La máquina necesita uv, en la versión del
  [ADR-0090](0090-la-maquina-es-debian-13-sus-programas-salen-de-sus-paquetes-y-uv-tiene-una-sola-version-exacta.md),
  y acceso a PyPI al desplegar.
- Los heads se leen con el `alembic` de cada versión, sin conectarse a la base.

## Descartado

- **El entorno dentro del artefacto:** el CI lo crearía en Ubuntu, y un entorno virtual no se
  mueve: sus scripts llevan la ruta absoluta del intérprete con que se creó.
