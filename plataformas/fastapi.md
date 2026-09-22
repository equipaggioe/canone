# FastAPI + SQLAlchemy async

Aplica a un repositorio con `server/`. Hoy: los seis.

Leído de `navetta`, `presenze`, `vettore`, `banditore`, `concordia` y `cadenza`. Donde había varias
formas, la página dice cuál se adopta y por qué.

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

Los routers van en `routers/`, no en `api/routers/` (banditore). Las dependencias van en
`core/deps.py`, no en `api/dependencies.py`. Un dominio grande usa una carpeta dentro de `models/`
y `schemas/`, como ya hacen concordia y vettore.

## Quién puede llamar a quién

| Capa | Puede importar | No puede |
|---|---|---|
| `routers/` | `schemas`, `services`, `core.deps` | `models` para escribir |
| `services/` | `models`, `schemas`, `core` | `fastapi`, salvo las excepciones de la aplicación |
| `models/` | `core.enums` | `schemas`, `services` |
| `schemas/` | `core.enums` | `models` |

Un router valida, delega y responde. La lógica vive en `services/`.

## `main.py`

```python
API_PREFIX = "/api"
app.include_router(auth.router, prefix=API_PREFIX)
```

El prefijo se aplica al montar, no dentro de cada `APIRouter`, y **no lleva versión** — ver
[ADR-0005](../adr/0005-prefijo-api-al-montar.md). Las rutas de operación interna van bajo
`/api/backoffice/...`.

## `core/settings.py`

- Una clase `Settings(BaseSettings)` y una instancia `settings`.
- **Nada lee `os.environ` fuera de este archivo.**
- Sin valores por defecto para secretos: una variable que falta revienta al arranque.

## `core/database.py`

Punto de partida en [`plantilla/server/app/core/database.py`](../plantilla/server/app/core/database.py).
Los cuatro puntos que no son negociables, y que hoy solo concordia tiene casi todos:

| Regla | Qué pasa si falta | Dónde falta hoy |
|---|---|---|
| `expire_on_commit=False` | Una `AsyncSession` no hace lazy-load: leer el modelo después del commit revienta | navetta |
| `pool_pre_ping=True` | Una conexión muerta en el pool (túnel caído) hace fallar el primer request que la tome | presenze, concordia |
| `rollback` explícito en el `except` de `get_db` | La conexión vuelve al pool con la transacción abierta | todos menos concordia |
| Tipo de retorno explícito en `get_db` | Sin él, mypy no revisa el cuerpo de la función | todos menos concordia |

## Forma de los datos

`app/schemas/base.py` es un **archivo canónico**: hoy es idéntico byte a byte en los seis
repositorios y se copia sin editar — ver [ADR-0002](../adr/0002-los-archivos-base-se-copian-y-se-verifican.md).

- **Entrada y salida en camelCase.** `alias_generator=to_camel` con `validate_by_name` y
  `validate_by_alias`: el servidor acepta las dos formas al entrar y siempre responde en camelCase,
  así los clientes TypeScript y Dart no traducen nombres.
- `bytes` en base64. Fechas en ISO 8601 con zona.

| Clase | Para qué | Config |
|---|---|---|
| `SchemaBase` | Salida | `from_attributes=True` |
| `SchemaInputBase` | Entrada | `extra="forbid"` — un campo de más es un error, no algo que se ignora |
| `QueryParamsBase` | Parámetros de query | |

`extra="forbid"` es la aplicación directa de «sin fallbacks»: un cliente que manda un campo mal
escrito se entera en el momento.

## Respuestas

| Caso | Cuerpo |
|---|---|
| Un recurso | El schema del recurso, sin envoltorio |
| Una lista paginada | `PageResponse[T]`: `items` + `meta` |
| Un error | `ErrorResponse` |

`PageMeta` calcula `totalPages`, `hasNext` y `hasPrev` como campos computados: el cliente no los
recalcula. Paginación: `page` (>= 1), `perPage` (1 a 200, por defecto 50), `sort`, `order`.

## El sobre de error

Es lo único de esta página que cruza a las otras plataformas: todo cliente lo consume igual.

```json
{
  "status": 422,
  "detail": "El correo ya está registrado",
  "errorCode": "EMAIL_TAKEN",
  "errors": { "email": ["Ya está registrado"] },
  "requestId": "..."
}
```

| Campo | Para quién |
|---|---|
| `status` | El HTTP |
| `detail` | La persona: se puede mostrar tal cual |
| `errorCode` | El cliente: es lo único sobre lo que ramifica. Enum `ErrorCode` en `core/enums.py` |
| `errors` | El formulario: errores por campo |
| `requestId` | El log |

**Un cliente nunca ramifica sobre `detail`.** El texto cambia; el `errorCode` es el contrato.

Los handlers se registran en `main.py`, uno por familia de excepción. Un router no arma un error a
mano. Un servicio levanta una excepción de `core/exceptions.py`.

## Enums hacia el cliente

`EnumOption` (`value` + `label`) es la forma de mandar un catálogo a un select. El `label` en
español lo produce el servidor: es la misma lista que valida, y así no hay dos traducciones que se
desincronicen.

## OpenAPI

El servidor exporta `openapi.json` con un script. Los clientes que puedan generar tipos a partir de
él lo hacen; se commitea el archivo de tipos generado y **no** el `openapi.json` intermedio
(concordia ya lo tiene resuelto así).

## WebSocket

- Bajo `/ws`, autenticado igual que el resto.
- Cada mensaje lleva un campo de tipo, y el payload es un schema de Pydantic serializado igual que
  una respuesta HTTP: camelCase, mismo formato de fecha.
- Un registro de conexiones en memoria solo sirve con un proceso. Con varios workers hace falta
  pub/sub en Redis, y entonces **Redis es obligatorio**: arrancar con varios workers sin Redis tiene
  que fallar al arranque, no partir las conexiones en silencio. Hoy concordia lo deja opcional, que
  es el degradado silencioso que `principios.md` prohíbe.

## Dependencias

`pyproject.toml` + `uv.lock`, sin `requirements.txt` en paralelo — ver
[ADR-0006](../adr/0006-dependencias-con-pyproject-y-uv.md). Base en
[`plantilla/server/pyproject.toml`](../plantilla/server/pyproject.toml).

Bibliotecas que no se usan más, con lo que las reemplaza:

| No | Sí | Por qué | Dónde está todavía |
|---|---|---|---|
| `python-jose` | `PyJWT[crypto]` | Sin mantenimiento desde 2021, con vulnerabilidades publicadas | presenze |
| `passlib` | `argon2-cffi` directo | Sin mantenimiento desde 2020, roto contra las versiones nuevas de bcrypt | navetta |
| `psycopg2-binary` | `psycopg[binary]` (v3) | psycopg2 está en mantenimiento pasivo | navetta |

## Tests

- `pytest` con `asyncio_mode = "auto"`, configurado en `pyproject.toml`. Nada de `pytest.ini`
  suelto (vettore).
- Contra Postgres real, en un schema dedicado. **No SQLite**: `models/base.py` es de PostgreSQL puro
  (JSONB, `gen_random_uuid()`, `Geography`) y nada de eso existe en SQLite.
- Un test por regla que se pueda romper en silencio. El
  `test_camel_and_snake_case_are_both_accepted_on_input` de concordia es el modelo: verifica una
  convención, no una funcionalidad.

## Lint y tipos

En `pyproject.toml`, igual en todos los repositorios que tengan servidor:

```toml
[tool.ruff]
line-length = 120
target-version = "py313"
extend-exclude = ["alembic/env.py", "alembic/versions/", "app/models/base.py", "app/schemas/base.py", "scripts/"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
ignore = ["UP042"]   # los enums son `class X(str, Enum)`, no StrEnum

[tool.mypy]
python_version = "3.13"
plugins = ["pydantic.mypy"]
ignore_missing_imports = true
exclude = ["alembic/"]
```

Los archivos canónicos quedan fuera de ruff: reformatearlos los separa de su fuente.

## CI

```yaml
- run: uv sync --frozen
- run: uv run ruff check .
- run: uv run mypy app
- run: uv run pytest     # DATABASE_URL apunta al schema de prueba, nunca al real
```

Hoy solo concordia lo tiene.
