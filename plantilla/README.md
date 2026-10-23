# plantilla

Los archivos que se copian a un repositorio. No es un proyecto que corra, y **no es una lista de lo
que un repositorio debe tener**: se copia solo lo de las plataformas que el producto use.

Cada archivo sale de una regla de [plataformas/](../plataformas/), y la página lo nombra. Un
archivo **canónico** se copia sin editar y `scripts/verificar.py` comprueba que la copia no se haya
separado ([ADR-0002](../adr/0002-los-archivos-base-se-copian-y-se-verifican.md)). Un **punto de
partida** se copia y después es del repositorio.

| Archivo | Destino | Tipo | Página |
|---|---|---|---|
| `.gitattributes` | Raíz | Canónico | [repositorio.md](../repositorio.md) |
| `.gitignore` | Raíz | Punto de partida | [repositorio.md](../repositorio.md) |
| `.github/workflows/ci.yml` | Raíz | Punto de partida: se quitan los jobs de las piezas que no hay y `PIEZA` toma el nombre de la carpeta | [repositorio.md](../repositorio.md), [python.md](../plataformas/python.md) |
| `.github/workflows/release.yml` | Raíz | Punto de partida: se quitan los jobs de las piezas que no hay y `PIEZA` toma el nombre de la carpeta | [despliegue.md](../plataformas/despliegue.md) |
| `scripts/deploy.py` | `scripts/` | Punto de partida: `PRODUCTO` y `OWNER` toman los nombres del repositorio, y se ajustan `TOKEN`, `UNITS`, `PORT` y `DESKTOP` | [despliegue.md](../plataformas/despliegue.md#versiones) |
| `infra/` | El servidor | Se instala desde canone, sin copiarse al repositorio: `PRODUCTO` y `PUERTO` toman los datos de la app, y salen las unidades de las piezas que no hay | [despliegue.md](../plataformas/despliegue.md) |
| `scripts/tokens.py` | `scripts/` | Canónico | [transversal.md](../plataformas/transversal.md) |
| `brand/tokens/` | `brand/tokens/` | Punto de partida | [transversal.md](../plataformas/transversal.md) |
| `python/.gitignore` | Cada pieza Python | Punto de partida | [python.md](../plataformas/python.md) |
| `server/pyproject.toml` | `server/` | Punto de partida | [python.md](../plataformas/python.md), [fastapi.md](../plataformas/fastapi.md) |
| `server/alembic.ini`, `alembic/README`, `alembic/env.py`, `alembic/script.py.mako` | `server/` | Canónico | [fastapi.md](../plataformas/fastapi.md) |
| `server/src/app/database.py`, `tracing.py`, `models/__init__.py`, `models/base.py`, `models/ruff.toml`, `routers/problems.py`, `schemas/base.py`, `schemas/page.py` | `server/src/app/` | Canónico | [fastapi.md](../plataformas/fastapi.md), [postgres.md](../plataformas/postgres.md) |
| `server/src/app/` (el resto) | `server/src/app/` | Punto de partida | [fastapi.md](../plataformas/fastapi.md) |
| `server/tests/test_conventions.py` | `server/tests/` | Canónico | [fastapi.md](../plataformas/fastapi.md), [postgres.md](../plataformas/postgres.md) |
| `server/tests/conftest.py`, `__init__.py` | `server/tests/` | Punto de partida | [fastapi.md](../plataformas/fastapi.md) |
| `qt/pyproject.toml` | `desktop/` | Punto de partida | [python.md](../plataformas/python.md), [qt.md](../plataformas/qt.md) |
| `qt/theme.py` | `desktop/src/app/` | Punto de partida | [qt.md](../plataformas/qt.md) |
| `qt/tests/test_theme.py` | `desktop/tests/` | Canónico | [qt.md](../plataformas/qt.md) |
| `flet/pyproject.toml` | La pieza Flet | Punto de partida | [python.md](../plataformas/python.md), [flet.md](../plataformas/flet.md) |
| `flet/theme.py` | `src/` de la pieza | Punto de partida | [flet.md](../plataformas/flet.md) |
| `flet/tests/test_theme.py` | `tests/` de la pieza | Canónico | [flet.md](../plataformas/flet.md) |
| `sveltekit/.prettierrc` | Cada superficie SvelteKit | Canónico | [sveltekit.md](../plataformas/sveltekit.md) |
| `sveltekit/.gitignore`, `svelte.config.js`, `uno.config.ts` | Cada superficie SvelteKit | Punto de partida | [sveltekit.md](../plataformas/sveltekit.md) |
| `flutter/analysis_options.yaml` | Cada app Flutter | Canónico | [flutter.md](../plataformas/flutter.md) |
| `flutter/.gitignore` | Cada app Flutter | Punto de partida | [repositorio.md](../repositorio.md) |
| `android/.editorconfig` | `mobile/` | Canónico | [android.md](../plataformas/android.md) |
| `android/.gitignore` | `mobile/` | Punto de partida | [repositorio.md](../repositorio.md) |
