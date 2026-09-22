# plantilla

Lo que un repositorio nuevo copia tal cual. No es un proyecto que corra: son los archivos que no se
escriben dos veces.

| Archivo | Regla |
|---|---|
| `server/app/models/base.py` | Canónico. Se copia sin editar — [ADR-0002](../adr/0002-los-archivos-base-se-copian-y-se-verifican.md) |
| `server/app/schemas/base.py` | Canónico. Se copia sin editar |
| `server/app/core/database.py` | Punto de partida. `settings` es de cada repositorio |
| `server/pyproject.toml` | Dependencias, ruff, mypy y pytest — [ADR-0006](../adr/0006-dependencias-con-pyproject-y-uv.md) |
| `.gitattributes` | Se copia sin editar |
| `.gitignore` | Punto de partida; lo propio del repositorio se agrega con un comentario que diga por qué |
| `.github/workflows/ci.yml` | Un job por superficie; se quitan los que el repositorio no tenga |

`canone/scripts/verificar.py` comprueba que las copias no se hayan separado.
