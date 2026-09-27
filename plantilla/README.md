# plantilla

Los archivos que se copian tal cual. No es un proyecto que corra, y **no es una lista de lo que un
repositorio debe tener**: se copia solo lo de las plataformas que el producto use.

| Archivo | Regla |
|---|---|
| `server/app/models/base.py` | Canónico. Se copia sin editar — [ADR-0002](../adr/0002-los-archivos-base-se-copian-y-se-verifican.md) |
| `server/app/schemas/base.py` | Canónico. Se copia sin editar |
| `server/app/core/tracing.py` | Canónico. Se copia sin editar |
| `server/app/models/ruff.toml` | Canónico. Se copia sin editar |
| `server/app/schemas/ruff.toml` | Canónico. Se copia sin editar |
| `server/app/services/ruff.toml` | Canónico. Se copia sin editar |
| `server/tests/test_conventions.py` | Canónico. Se copia sin editar |
| `server/app/core/database.py` | Punto de partida. `settings` es de cada repositorio |
| `server/app/core/exceptions.py` | Punto de partida. Los tipos de `PROBLEMS` son de cada repositorio |
| `server/app/routers/problems.py` | Punto de partida |
| `server/pyproject.toml` | Dependencias, ruff, mypy y pytest — [ADR-0006](../adr/0006-dependencias-con-pyproject-y-uv.md) |
| `server/tests/conftest.py` | Punto de partida. Los fixtures son de cada repositorio |
| `qt/ui/ruff.toml` | Canónico. Se copia sin editar a `desktop/ui/` |
| `qt/tests/test_theme.py` | Canónico. Se copia sin editar a `desktop/tests/` |
| `qt/tests/test_conventions.py` | Canónico. Se copia sin editar a `desktop/tests/` |
| `qt/tests/conftest.py` | Punto de partida. Los fixtures son de cada repositorio |
| `qt/ui/theme.py` | Punto de partida. Los colores son de cada producto |
| `python/pyproject.toml` | Base de toda pieza Python: ruff, mypy, pytest y uv — [ADR-0006](../adr/0006-dependencias-con-pyproject-y-uv.md) |
| `qt/pyproject.toml` | Dependencias, ruff, mypy y pytest de una pieza Qt |
| `.gitattributes` | Se copia sin editar |
| `.gitignore` | El del raíz |
| `python/.gitignore` | A cada pieza Python: `server/`, Flet, Qt |
| `sveltekit/.gitignore` | A cada superficie SvelteKit |
| `flutter/.gitignore` | A cada app Flutter |
| `.github/workflows/ci.yml` | Un job por pieza; se quitan los que el repositorio no tenga |

Todavía no hay plantilla de código de Flutter ni de Flet, solo su `.gitignore`. Cuando la haya,
sale de la documentación oficial, no de un repositorio — ver
[ADR-0018](../adr/0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md).

`canone/scripts/verificar.py` comprueba que las copias no se hayan separado.
