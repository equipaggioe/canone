# plantilla

Los archivos que se copian tal cual. No es un proyecto que corra, y **no es una lista de lo que un
repositorio debe tener**: se copia solo lo de las plataformas que el producto use.

| Archivo | Regla |
|---|---|
| `server/app/models/base.py` | Canónico. Se copia sin editar — [ADR-0002](../adr/0002-los-archivos-base-se-copian-y-se-verifican.md) |
| `server/app/schemas/base.py` | Canónico. Se copia sin editar |
| `server/app/core/database.py` | Punto de partida. `settings` es de cada repositorio |
| `server/pyproject.toml` | Dependencias, ruff, mypy y pytest — [ADR-0006](../adr/0006-dependencias-con-pyproject-y-uv.md) |
| `.gitattributes` | Se copia sin editar |
| `.gitignore` | El del raíz |
| `python/.gitignore` | A cada pieza Python: `server/`, Flet, Qt |
| `sveltekit/.gitignore` | A cada superficie SvelteKit |
| `flutter/.gitignore` | A cada app Flutter |
| `.github/workflows/ci.yml` | Un job por pieza; se quitan los que el repositorio no tenga |

Todavía no hay plantilla de código de Flutter ni de Flet, solo su `.gitignore`: cuando la haya,
sale de `vettore/app` y de `presenze/app`.

`canone/scripts/verificar.py` comprueba que las copias no se hayan separado.
