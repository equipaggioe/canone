# Convención: `server/`

## Layout

```
server/
  pyproject.toml        dependencias, ruff, mypy, pytest
  uv.lock
  alembic.ini
  alembic/versions/
  app/
    main.py             crea la app, monta routers y handlers de error
    core/
      settings.py       pydantic-settings; única lectura del entorno
      database.py       engine, sessionmaker, get_db()
      deps.py           dependencias de FastAPI compartidas
      enums.py          enums del dominio + ErrorCode
      exceptions.py     excepciones de la aplicación
      security.py       hash, tokens
    models/             SQLAlchemy. base.py + un archivo o carpeta por dominio
    schemas/            Pydantic. base.py + un archivo o carpeta por dominio
    routers/            un archivo por recurso
    services/           la lógica; no sabe de FastAPI
  tests/
  scripts/
```

Los routers van en `routers/`, no en `api/routers/`. Las dependencias van en `core/deps.py`, no en
`api/dependencies.py`.

## Quién puede llamar a quién

| Capa | Puede importar | No puede |
|---|---|---|
| `routers/` | `schemas`, `services`, `core.deps` | `models` directamente para escribir |
| `services/` | `models`, `schemas`, `core` | Nada de `fastapi` salvo las excepciones de la aplicación |
| `models/` | `core.enums` | `schemas`, `services` |
| `schemas/` | `core.enums` | `models` |

Un router valida, delega y responde. La lógica vive en `services/`.

## `main.py`

Monta todo en un solo lugar:

```python
API_PREFIX = "/api"
app.include_router(auth.router, prefix=API_PREFIX)
```

El prefijo se aplica en `include_router`, no dentro de cada `APIRouter`. Sin `v1`: ningún
repositorio está en producción y no hay cliente viejo que sostener.

## `core/settings.py`

- Una sola clase `Settings(BaseSettings)` y una sola instancia `settings`.
- **Nada lee `os.environ` fuera de este archivo.**
- Sin valores por defecto para secretos: una variable que falta tiene que reventar al arranque.

## `core/database.py`

El archivo canónico está en [`plantilla/server/app/core/database.py`](../plantilla/). Los cuatro
puntos que no son negociables, y que hoy solo concordia tiene todos:

| Regla | Qué pasa si falta |
|---|---|
| `expire_on_commit=False` | Una `AsyncSession` no hace lazy-load: leer el modelo después del commit revienta |
| `pool_pre_ping=True` | Una conexión muerta en el pool (túnel caído) falla el primer request que la tome |
| `rollback` explícito en el `except` de `get_db` | La conexión vuelve al pool con la transacción abierta |
| Tipo de retorno explícito en `get_db` | Sin él, mypy no revisa el cuerpo de la función |

## Errores

Un servicio levanta una excepción de `core/exceptions.py`. Un handler en `main.py` la traduce a
`ErrorResponse` — ver [api.md](api.md). Un router no arma respuestas de error a mano.

## Tests

- `pytest` con `asyncio_mode = "auto"`, configurado en `pyproject.toml`.
- Contra Postgres real, en un schema dedicado. No SQLite: el `models/base.py` es de PostgreSQL puro
  (JSONB, `gen_random_uuid()`, `Geography`) y nada de eso existe en SQLite.
- Un test por regla que se pueda romper en silencio. El de concordia
  `test_camel_and_snake_case_are_both_accepted_on_input` es el modelo: verifica una convención, no
  una funcionalidad.

## Lint y tipos

`pyproject.toml`, igual en todos los repositorios:

```toml
[tool.ruff]
line-length = 120
target-version = "py313"
extend-exclude = ["alembic/env.py", "alembic/versions/", "scripts/"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
ignore = ["UP042"]   # los enums son `class X(str, Enum)`, no StrEnum

[tool.mypy]
python_version = "3.13"
plugins = ["pydantic.mypy"]
ignore_missing_imports = true
exclude = ["alembic/"]
```

`app/models/base.py` y `app/schemas/base.py` quedan fuera de ruff: son archivos canónicos de
`canone` y reformatearlos los separa de su fuente.
