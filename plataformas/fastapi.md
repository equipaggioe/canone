# FastAPI + SQLAlchemy async

Cómo se construye un `server/`.

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

Los routers van en `routers/`; las dependencias, en `core/deps.py`. Un dominio con muchos archivos
usa una carpeta dentro de `models/` y `schemas/`, no un módulo de mil líneas.

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

El prefijo se aplica al montar, no dentro de cada `APIRouter`, y **no lleva versión**: todas las
piezas se despliegan juntas y no hay cliente viejo que sostener. Las rutas de operación interna van
bajo `/api/backoffice/...`.

## Detrás del proxy

El servidor corre detrás de un proxy inverso — ver [despliegue.md](despliegue.md).

- **Los encabezados reenviados se aceptan solo del proxy**: `--proxy-headers` con
  `--forwarded-allow-ips` apuntando a él, nunca a `*`. Si se confía en cualquier origen, el límite
  de tasa por IP se saltea mandando un `X-Forwarded-For` falso, y los logs registran la dirección
  que el cliente quiera.
- **Un endpoint de salud que comprueba sus dependencias**, no que el proceso vive: responde bien
  solo si la base contesta. Es lo que mira el despliegue para decidir si el servicio quedó arriba, y
  uno que devuelve `200` siempre convierte esa comprobación en un adorno.

## `core/settings.py`

- Una clase `Settings(BaseSettings)` y una instancia `settings`.
- **Nada lee `os.environ` fuera de este archivo.**
- Sin valores por defecto para secretos: una variable que falta revienta al arranque, no a la
  primera petición que la necesita.

## `core/database.py`

```python
engine = create_async_engine(
    settings.database_url_async,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine,
    class_=AsyncSession, expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession]:
    db: AsyncSession = SessionLocal()
    try:
        yield db
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()
```

Los cuatro puntos, y qué pasa si falta cada uno:

| Regla | Si falta |
|---|---|
| `expire_on_commit=False` | Una `AsyncSession` no hace lazy-load: leer el modelo después del commit revienta |
| `pool_pre_ping=True` | Una conexión muerta en el pool hace fallar el primer request que la tome, mucho después de que la red se cayera |
| `rollback` en el `except` | La conexión vuelve al pool con la transacción abierta |
| Tipo de retorno explícito | mypy no revisa el cuerpo de la función sin él |

## Forma de los datos

`app/schemas/base.py` es un **archivo canónico**: se copia de `plantilla/` sin editar.

- **Entrada y salida en camelCase.** `alias_generator=to_camel` con `validate_by_name` y
  `validate_by_alias`: el servidor acepta las dos formas al entrar y siempre responde en camelCase,
  para que los clientes TypeScript y Dart no traduzcan nombres.
- `bytes` en base64. Fechas en ISO 8601 con zona.

| Clase | Para qué | Config |
|---|---|---|
| `SchemaBase` | Salida | `from_attributes=True` |
| `SchemaInputBase` | Entrada | `extra="forbid"` |
| `QueryParamsBase` | Parámetros de query | |

`extra="forbid"` es la aplicación directa de «sin fallbacks»: un cliente que manda un campo mal
escrito se entera en el momento, no cuando alguien nota que ese dato nunca llegó.

## Respuestas

| Caso | Cuerpo |
|---|---|
| Un recurso | El schema del recurso, sin envoltorio |
| Una lista paginada | `PageResponse[T]`: `items` + `meta` |
| Un error | `ErrorResponse` |

`PageMeta` calcula `totalPages`, `hasNext` y `hasPrev` como campos computados: el cliente no los
recalcula. Paginación: `page` (>= 1), `perPage` (1 a 200, por defecto 50), `sort`, `order`.

## El sobre de error

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

**Un cliente nunca ramifica sobre `detail`.** El texto cambia; el `errorCode` es el contrato. Todo
cliente —web, Flutter, Flet, Qt— traduce este sobre a un error tipado con estos mismos campos.

Un servicio levanta una excepción de `core/exceptions.py`; un handler registrado en `main.py` la
traduce. Un router no arma un error a mano.

## Enums hacia el cliente

`EnumOption` (`value` + `label`) es la forma de mandar un catálogo a un select. El `label` en
español lo produce el servidor: es la misma lista que valida, así no hay dos traducciones que se
desincronicen.

## OpenAPI

El servidor exporta `openapi.json` con un script y los clientes que puedan generan sus tipos desde
él. Se commitea el archivo de tipos generado; el `openapi.json` intermedio, no.

## Trabajo que no cabe en el request

No hay cola de tareas. Lo que no cabe en la respuesta se resuelve así:

- **Un SDK bloqueante va en `asyncio.to_thread`.** Llamarlo directo desde una corrutina congela el
  event loop entero, y con eso los WebSocket del mismo proceso.
- **Primero la evidencia, después la entrega.** Lo que hay que conservar se escribe en la
  transacción de quien llama; el envío al mundo exterior ocurre después y es best-effort.
- **Un fallo de entrega no tumba la operación que lo originó.** Se registra y se sigue.

Si algún día hace falta una cola de verdad, es un ADR del repositorio que la necesite, y empieza por
nombrar el síntoma que elimina.

## Dependencias

`pyproject.toml` + `uv.lock`, sin `requirements.txt` en paralelo. Base en
[`plantilla/server/pyproject.toml`](../plantilla/server/pyproject.toml).

| No se usa | Se usa | Por qué |
|---|---|---|
| `python-jose` | `PyJWT[crypto]` | Sin mantenimiento desde 2021, con vulnerabilidades publicadas |
| `passlib` | `argon2-cffi` directo | Sin mantenimiento desde 2020, roto contra las versiones nuevas de bcrypt |
| `psycopg2-binary` | `psycopg[binary]` (v3) | psycopg2 está en mantenimiento pasivo |
| Un ORM sync | SQLAlchemy async | El servidor entero es async |

Una dependencia que ningún archivo importa se borra del `pyproject.toml`.

## Tests

- `pytest` con `asyncio_mode = "auto"`, configurado en `pyproject.toml`. Nada de `pytest.ini`.
- Contra Postgres real, en un schema dedicado. **No SQLite**: `models/base.py` es de PostgreSQL puro
  (JSONB, `gen_random_uuid()`, `Geography`) y nada de eso existe en SQLite.
- Un test por regla que se pueda romper en silencio: que la entrada acepte camelCase y snake_case,
  que un enum inválido sea rechazado por la base, que el contraste de los tokens se mantenga. Son
  tests de convención, y son los que avisan cuando alguien deshace una decisión sin saberlo.

## Lint y tipos

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
