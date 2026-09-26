# FastAPI + SQLAlchemy async

Servidor HTTP con FastAPI y SQLAlchemy async. Se suma a [python.md](python.md). Archivos base en
[`plantilla/server/`](../plantilla/server/).

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
      enums.py          enums del dominio + ProblemType
      exceptions.py     AppError y PROBLEMS: title, status y descripción de cada ProblemType
      security.py       hash, tokens
      tracing.py        el trace-id de cada request (W3C Trace Context)
    models/             SQLAlchemy. base.py + una carpeta por dominio, con un archivo por tabla
      ruff.toml
    schemas/            Pydantic. base.py + una carpeta por dominio, con un archivo por modelo (o por recurso sin tabla)
      ruff.toml
    routers/            un archivo por recurso
      problems.py       la documentación de cada ProblemType
    services/           la lógica; no sabe de FastAPI
      ruff.toml
  tests/
    conftest.py
    test_conventions.py
  scripts/
```

- Los routers van en `routers/`; las dependencias compartidas, en `core/deps.py`.
- En `models/` y `schemas/` la carpeta del dominio existe aunque tenga un solo archivo.
- Una tabla por archivo, también las de asociación (`Table(...)` de un muchos a muchos), que no van
  dentro del modelo de ninguno de los dos lados.
- `models/__init__.py` importa cada tabla.
- Una relación entre archivos se declara con el nombre como texto (`relationship("User")`) y el
  import del tipo bajo `TYPE_CHECKING`.
- Un archivo de `schemas/` por modelo agrupa sus variantes (`UserCreate`, `UserUpdate`,
  `UserRead`). Lo que no corresponde a una tabla (`LoginRequest`, `TokenResponse`) va en un archivo
  por recurso dentro de la carpeta de su dominio.

## Capas

| Capa | Puede importar | No puede |
|---|---|---|
| `routers/` | `schemas`, `services`, `core.deps` | `models` para escribir |
| `services/` | `models`, `schemas`, `core` | `fastapi`, `routers` |
| `models/` | `core.enums` | `schemas`, `services`, `routers` |
| `schemas/` | `core.enums` | `models`, `services`, `routers` |

- Un router valida, delega y responde. La lógica vive en `services/`.

## FastAPI

Estándares: *Dependencies*, *Bigger Applications*, *Lifespan Events* y *Behind a Proxy* de la
documentación de FastAPI.

- Las dependencias se declaran con `Annotated`, nunca como valor por defecto. El alias se escribe
  una vez en `core/deps.py`:

  ```python
  DbSession = Annotated[AsyncSession, Depends(get_db)]

  async def get_vehicle(vehicle_id: UUID, db: DbSession) -> VehicleOut: ...
  ```

- El prefijo se aplica al montar, no dentro de cada `APIRouter`, y lleva versión (ADR-0012):

  ```python
  API_PREFIX = "/api/v1"
  app.include_router(auth.router, prefix=API_PREFIX, responses=PROBLEM_RESPONSES)
  app.include_router(problems.router)
  ```

- Las rutas de operación interna van bajo `/api/v1/backoffice/...`.
- Arranque y cierre en `lifespan`, nunca en `@app.on_event`.
- Detrás del proxy inverso ([despliegue.md](despliegue.md)), `--proxy-headers` con
  `--forwarded-allow-ips` apuntando al proxy, nunca a `*`: con `*`, cualquiera falsea su IP con un
  `X-Forwarded-For`.
- El endpoint de salud responde bien solo si la base contesta.

## Settings

Estándar: *Settings and Environment Variables* de FastAPI, con `pydantic-settings`.

- Una clase `Settings(BaseSettings)` en `core/settings.py` y una instancia `settings`.
- Nada lee `os.environ` fuera de ese archivo.
- Un secreto no lleva valor por defecto.

## Base de datos

Estándares: *Asynchronous I/O (asyncio)* y *Dealing with Disconnects* de SQLAlchemy, y la plantilla
async de Alembic.

```python
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as db:
        yield db
```

- Una sesión por request, abierta con `async with`. Nada de `rollback` a mano.
- `settings.database_url` es una sola URL `postgresql+asyncpg://...`, la misma para la app, Alembic
  y los scripts.
- Alembic con la plantilla `async`.
- Los scripts de `scripts/` también son async y arrancan con `asyncio.run`.

## Forma de los datos

Estándar: la configuración de modelos de Pydantic.

`app/schemas/base.py` es un **archivo canónico**: se copia de `plantilla/` sin editar.

- Entrada y salida en camelCase: `alias_generator=to_camel` con `validate_by_name` y
  `validate_by_alias`. El servidor acepta las dos formas al entrar y siempre responde en camelCase,
  para que los clientes TypeScript y Dart no traduzcan nombres.
- `bytes` en base64. Fechas en ISO 8601 con zona.
- La entrada lleva `extra="forbid"`: un campo mal escrito falla en el momento.

| Clase | Para qué | Config |
|---|---|---|
| `SchemaBase` | Salida | `from_attributes=True` |
| `SchemaInputBase` | Entrada | `extra="forbid"` |
| `QueryParamsBase` | Parámetros de query | |

## Respuestas

| Caso | Cuerpo |
|---|---|
| Un recurso | El schema del recurso, sin envoltorio |
| Una lista paginada | `PageResponse[T]`: `items` + `meta` |
| Un error | `ProblemDetails` |

- `PageMeta` calcula `totalPages`, `hasNext` y `hasPrev` como campos computados.
- Paginación: `page` (>= 1), `perPage` (1 a 200, por defecto 50), `sort`, `order`.

## El sobre de error

Estándar: RFC 9457, *Problem Details for HTTP APIs*.

```json
{
  "type": "/problems/email-taken",
  "title": "Correo ya registrado",
  "status": 422,
  "detail": "El correo ya está registrado",
  "errors": [{ "detail": "Ya está registrado", "pointer": "#/email" }],
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

| Campo | Contenido |
|---|---|
| `type` | Un valor del enum `ProblemType`, en `core/enums.py` |
| `title` | Fijo por tipo |
| `status` | El código de la respuesta |
| `detail` | Un texto que se puede mostrar tal cual |
| `errors` | Un elemento por campo, con un JSON Pointer al campo de la petición |
| `traceId` | El trace-id del request |

- Se responde con `Content-Type: application/problem+json`.
- `type` es una ruta completa bajo `/problems/`, estable entre versiones de la API.
- Relativo y no absoluto: el dominio cambia entre entornos, y el `type` de un error tiene que ser el
  mismo en todos.
- `GET /problems/{slug}` responde una página HTML con el `title`, el `status` y la descripción del
  tipo. Vive en `routers/problems.py`, se monta sin prefijo y queda fuera de
  OpenAPI.
- La validación de Pydantic sale con `type` `/problems/validation-error` y un elemento de `errors`
  por fallo.
- Un error sin semántica propia, como el 404 de una ruta que no existe o un 500 no controlado, va
  con `type` `about:blank` y la frase de su código HTTP como `title`.
- **Un cliente nunca ramifica sobre `detail`.** Todo cliente —web, Flutter, Flet, Qt— traduce
  este sobre a un error tipado con estos mismos campos.
- Cada `ProblemType` tiene en `PROBLEMS`, en `core/exceptions.py`, su `title`, su `status` y su
  descripción. Es la única fuente: `AppError` y `/problems/{slug}` leen de ahí.
- Un servicio levanta `AppError` con el `type` y el `detail`, y un handler registrado en `main.py`
  la traduce. Un router no arma un error a mano.

## Trazas

Estándar: W3C Trace Context.

`app/core/tracing.py` es un **archivo canónico**.

- `main.py` agrega `TraceContextMiddleware`. Toma el trace-id del header `traceparent`, o empieza
  una traza nueva si falta o es inválido.
- El handler del log lleva `TraceIdFilter`, y su formato, `%(trace_id)s`.
- El error lleva el mismo valor en `traceId`.

## Enums hacia el cliente

- Un catálogo para un select se manda con `EnumOption` (`value` + `label`).
- El `label` en español lo produce el servidor: es la misma lista que valida, así no hay dos
  traducciones que se desincronicen.

## OpenAPI

Estándar: *Generating SDKs* de FastAPI.

- El servidor exporta `openapi.json` con un script, y los clientes que puedan generan sus tipos
  desde él.
- Se commitea el archivo de tipos generado; el `openapi.json` intermedio, no.
- Todo router se monta con `responses=PROBLEM_RESPONSES`, de `app/schemas/base.py`, que documenta
  los 4XX, 5XX y el 422 como `ProblemDetails`: sin él, FastAPI documenta el 422 con su propio
  formato.

## Trabajo que no cabe en el request

Estándar: *Background Tasks* de FastAPI.

No hay cola de tareas.

- Un SDK bloqueante va en `asyncio.to_thread`.
- La entrega al exterior sigue la regla de [notificaciones.md](notificaciones.md): primero la
  evidencia, después la entrega.
- La entrega que dispara un request va en `BackgroundTasks`, y la agenda el router.

## Trabajo periódico

Lo fija el ADR-0011.

- La pasada es una función de `services/`, idempotente, que devuelve cuántas filas tocó y no sabe
  quién la llamó.
- El disparador va aparte y pueden convivir dos: un script en `scripts/ops/` para cron o systemd, y
  el lazo del `lifespan`.
- Si hay lazo, hay candado: `pg_try_advisory_lock` para una operación global, `FOR UPDATE SKIP
  LOCKED` cuando reparte filas.
- Al cerrar, el `lifespan` espera a que la tarea termine.
- Una excepción nunca mata el lazo, y cada tarea tiene un interruptor, apagado por defecto.

## Dependencias

| No se usa | Se usa | Por qué |
|---|---|---|
| `python-jose` | `PyJWT[crypto]` | Lo que usa FastAPI |
| `passlib` | `argon2-cffi` directo | Sin mantenimiento desde 2020, roto contra las versiones nuevas de bcrypt |
| `psycopg2-binary`, `psycopg` | `asyncpg`, también para Alembic | Un solo driver y una sola URL. `psycopg` en modo async no corre sobre el event loop por defecto de Windows |

## Tests

Estándares: *Async Tests* de FastAPI y *Testing with AnyIO*.

- `pytest` con el plugin de AnyIO en `anyio_mode = "auto"`, configurado en `pyproject.toml`. Nada
  de `pytest.ini` ni de `pytest-asyncio`.
- `anyio_backend` devuelve `"asyncio"`, con alcance `session`, en `tests/conftest.py`.
- Los endpoints se prueban con `httpx.AsyncClient` sobre `ASGITransport`.
- Contra Postgres real, en un schema dedicado. Nada de SQLite: `models/base.py` usa JSONB,
  `gen_random_uuid()` y `Geography`.
- Un test por regla que se pueda romper en silencio, como que la entrada acepte camelCase y
  `snake_case`, o que la base rechace un enum inválido.

## Cómo se hace cumplir

| Convención | Con qué |
|---|---|
| Dependencias con `Annotated` | `FAST002` |
| Sin `response_model` redundante ni parámetros de ruta sin usar | `FAST001`, `FAST003` |
| Constructores y validadores de Pydantic tipados | plugin `pydantic.mypy` |
| camelCase, `extra="forbid"` y base64 | `app/schemas/base.py` canónico |
| Campos del sobre de error | `ProblemDetails` en `app/schemas/base.py` canónico |
| Cada `ProblemType` responde en `/problems/{slug}` | `tests/test_conventions.py` |
| Toda operación declara sus errores como `ProblemDetails` | `tests/test_conventions.py` |
| El error sale como `application/problem+json` con el `traceId` del `traceparent` | `tests/test_conventions.py` |
| Capas de `services/`, `models/` y `schemas/` | `TID251` en el `ruff.toml` de cada carpeta |
| `os.environ` solo en `settings.py` | `TID251` en `pyproject.toml` |
| Sin las dependencias descartadas | `scripts/verificar.py` |
| `app/models/base.py`, `app/schemas/base.py`, `app/core/tracing.py`, los tres `ruff.toml` y `tests/test_conventions.py` iguales a los de canone | `scripts/verificar.py` |
| `pyproject.toml`, sin `requirements.txt` ni `pytest.ini` | `scripts/verificar.py` |
| Sin `app/api/` y `app/routers/` a la vez | `scripts/verificar.py` |
| La entrada acepta camelCase y `snake_case` | Tests del repositorio |

### Configuración

La base está en [`plantilla/server/pyproject.toml`](../plantilla/server/pyproject.toml). Sobre la de
[python.md](python.md) suma:

- `FAST` en ruff y el plugin `pydantic.mypy`.
- `os.environ` y `os.getenv` prohibidos con `TID251`, salvo en `app/core/settings.py`.
- `pythonpath = ["."]` en pytest, para que los tests importen `app`.
- Los archivos canónicos, `alembic/env.py`, `alembic/versions/` y `scripts/` quedan fuera de ruff:
  reformatear un canónico lo separa de su fuente.

### CI

Los pasos están en el job `server` de
[`plantilla/.github/workflows/ci.yml`](../plantilla/.github/workflows/ci.yml). `pytest` corre contra
el schema de prueba, nunca contra la base real.
