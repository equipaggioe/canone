# FastAPI + SQLAlchemy async

Servidor HTTP con FastAPI y SQLAlchemy async. Se suma a [python.md](python.md). Archivos base en
[`plantilla/server/`](../plantilla/server/).

## Layout

Estándar: [*Bigger Applications*](../estandares/fastapi/bigger-applications.md) de FastAPI.

```
server/
  pyproject.toml
  uv.lock
  alembic.ini
  alembic/versions/
  app/
    main.py             crea la app, monta los routers y registra los handlers de error
    core/
      settings.py       la clase Settings y su instancia
      database.py       engine, sessionmaker, get_db()
      deps.py           las dependencias compartidas y sus alias Annotated
      enums.py          los enums del dominio y ProblemType
      exceptions.py     AppError y PROBLEMS
      security.py       hash y tokens
      tracing.py        el trace-id de cada request
    models/             base.py y una carpeta por dominio, con un archivo por tabla
      ruff.toml
    schemas/            base.py y una carpeta por dominio, con un archivo por modelo
      ruff.toml
    routers/            un archivo por recurso
      problems.py       la documentación de cada ProblemType
    services/           la lógica
      ruff.toml
  tests/
    conftest.py
    test_conventions.py
  scripts/
```

- En `models/` y `schemas/`, cada dominio tiene su carpeta, también el que tiene un solo archivo.
- Una tabla de asociación (`Table(...)` de un muchos a muchos) tiene su propio archivo.
- `models/__init__.py` importa cada tabla: así Alembic las ve todas al generar una migración.
- Una relación entre archivos nombra la clase como texto: `relationship("User")`.
- El archivo de `schemas/` de un modelo reúne sus variantes (`UserCreate`, `UserUpdate`,
  `UserRead`). Un schema sin tabla (`LoginRequest`, `TokenResponse`) va en un archivo por recurso,
  en la carpeta de su dominio.

## Capas

| Capa | Importa |
|---|---|
| `routers/` | `schemas`, `services`, `core.deps`, y `models` solo para leer |
| `services/` | `models`, `schemas`, `core` |
| `models/` | `core.enums` |
| `schemas/` | `core.enums` |

- Un router valida, delega en un servicio y responde.

## FastAPI

Estándares: [*Dependencies*](../estandares/fastapi/dependencies.md),
[*Bigger Applications*](../estandares/fastapi/bigger-applications.md),
[*Lifespan Events*](../estandares/fastapi/events.md) y
[*Behind a Proxy*](../estandares/fastapi/behind-a-proxy.md) de FastAPI.

- El prefijo `/api/v1` se aplica al montar cada router, en `main.py`. El `APIRouter` declara solo
  su recurso: `prefix="/vehicles"` ([ADR-0012](../adr/0012-el-prefijo-api-v1-se-aplica-al-montar.md)).
- Las rutas de operación interna van bajo `/api/v1/backoffice/`.
- `--forwarded-allow-ips` lleva la IP del proxy inverso ([despliegue.md](despliegue.md)): con `*`,
  cualquiera falsea su IP con un `X-Forwarded-For`.
- El endpoint de salud responde bien cuando la base contesta.

## Settings

Estándares: [*Settings and Environment Variables*](../estandares/fastapi/settings.md) de FastAPI y
[pydantic-settings](../estandares/pydantic-settings/index.md).

- Una instancia `settings` de `Settings(BaseSettings)`, en `core/settings.py`: el engine y el
  logging la leen al importarse, antes de que exista un request.
- El entorno se lee solo en `core/settings.py`.
- Un secreto es un campo obligatorio.

## Base de datos

Estándares: [*Asynchronous I/O (asyncio)*](../estandares/sqlalchemy/asyncio.rst) y
[*Dealing with Disconnects*](../estandares/sqlalchemy/pooling.rst) de SQLAlchemy, y la
[plantilla async](../estandares/alembic/async/env.py) de Alembic.

- Los modelos son de SQLAlchemy 2 y los schemas de Pydantic, cada uno en su capa.
- `asyncpg` es el único driver, para la app, Alembic y los scripts, con una sola URL
  `postgresql+asyncpg://...`: `psycopg` en modo async no corre sobre el event loop por defecto de
  Windows.
- La sesión de un request sale de `get_db()`, en `core/database.py`.
- El pool revisa cada conexión antes de entregarla (`pool_pre_ping=True`): una conexión muerta hace
  fallar el request que la toma.
- Alembic con la plantilla `async`.
- Los scripts de `scripts/` son async y arrancan con `asyncio.run`.

## Forma de los datos

Estándares: la [configuración de modelos](../estandares/pydantic/config.md) de Pydantic y el
[RFC 3339](../estandares/rfc/rfc3339.txt).

`app/schemas/base.py` es un archivo canónico: se copia de `plantilla/` sin editar.

- En el cable, camelCase: es la convención de TypeScript y Dart. Al entrar se acepta también
  `snake_case`.
- `bytes` en base64. Fechas en RFC 3339.
- La entrada lleva `extra="forbid"`: un campo mal escrito falla en el momento.

| Clase | Para qué | Config |
|---|---|---|
| `SchemaBase` | Salida | `from_attributes=True` |
| `SchemaInputBase` | Entrada | `extra="forbid"` |
| `QueryParamsBase` | Parámetros de query | |

## Respuestas

| Caso | Cuerpo |
|---|---|
| Un recurso | El schema del recurso |
| Una lista paginada | `PageResponse[T]`: `items` y `meta` |
| Un error | `ProblemDetails` |

- Paginación con `page` (desde 1), `perPage` (de 1 a 200, 50 por defecto), `sort` y `order`
  (`asc` o `desc`, `desc` por defecto).
- `meta` trae `page`, `perPage` y `total`, y calcula `totalPages`, `hasNext` y `hasPrev`.

## El sobre de error

Estándares: [RFC 9457](../estandares/rfc/rfc9457.txt), [RFC 6901](../estandares/rfc/rfc6901.txt)
y [*Handling Errors*](../estandares/fastapi/handling-errors.md) de FastAPI.

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
| `type` | Un valor de `ProblemType`, en `core/enums.py`. Es lo único sobre lo que ramifica un cliente |
| `title` | Fijo por tipo |
| `detail` | Un texto que el cliente muestra tal cual |
| `errors` | Un elemento por campo, con el JSON Pointer al campo de la petición |
| `traceId` | El trace-id del request |

- `type` es relativo, bajo `/problems/`: el dominio cambia entre entornos, y el `type` de un error
  es el mismo en todos.
- `PROBLEMS`, en `core/exceptions.py`, tiene el `title`, el `status` y la descripción de cada
  `ProblemType`. De ahí leen `AppError` y `GET /problems/{slug}`.
- `GET /problems/{slug}` sirve la descripción en HTML desde `routers/problems.py`, que se monta sin
  prefijo y fuera de OpenAPI.
- La validación de Pydantic sale con `type` `/problems/validation-error` y un elemento de `errors`
  por fallo.
- Un servicio levanta `AppError` con el `type` y el `detail`, y el handler de `main.py` la responde.
  Todo error de un router sale por `AppError`.

## Trazas

Estándar: [W3C Trace Context](../estandares/w3c/trace-context-1.md).

`app/core/tracing.py` es un archivo canónico.

- `main.py` agrega `TraceContextMiddleware`.
- Cada línea del log lleva el trace-id: el handler usa `TraceIdFilter` y su formato,
  `%(trace_id)s`.
- El error lleva el mismo trace-id en `traceId`.

## Enums hacia el cliente

- Un catálogo para un select viaja como lista de `EnumOption` (`value` y `label`). El `label` en
  español lo arma el servidor: es la misma lista que valida.

## OpenAPI

Estándar: [*Generating SDKs*](../estandares/fastapi/generate-clients.md) de FastAPI.

- Un script exporta `openapi.json`, y cada cliente que genera tipos los genera desde él.
- Se commitea el archivo de tipos generado; el `openapi.json` se regenera cada vez.
- Todo router se monta con `responses=PROBLEM_RESPONSES`, de `app/schemas/base.py`, que documenta
  los 4XX, el 422 y los 5XX como `ProblemDetails`: FastAPI documenta el 422 con su propio formato.

## Trabajo fuera del request

Estándar: [*Background Tasks*](../estandares/fastapi/background-tasks.md) de FastAPI.

- El trabajo de fondo corre en el mismo proceso: `BackgroundTasks` o el lazo periódico.
- La entrega al exterior que dispara un request va en `BackgroundTasks`, y la agenda el router.

## Trabajo periódico

Estándar: [*Lifespan Events*](../estandares/fastapi/events.md) de FastAPI
([ADR-0011](../adr/0011-la-pasada-es-una-funcion-y-el-disparador-va-aparte.md)).

- La pasada es una función idempotente de `services/` que devuelve cuántas filas tocó.
- La disparan un script de `scripts/ops/` para cron o systemd, el lazo del `lifespan`, o los dos.
- Cada worker corre su propio lazo, así que el lazo toma un candado: `pg_try_advisory_lock` para
  una operación global, y `FOR UPDATE SKIP LOCKED` cuando reparte filas.
- Una sola tarea de fondo por proceso.
- El lazo registra la excepción y sigue con la próxima vuelta.
- Cada tarea tiene un interruptor y un intervalo, y arranca apagada: los tests y los scripts
  importan `app.main`.
- Al cerrar, el `lifespan` espera a que la tarea termine.

## Tests

Estándares: [*Async Tests*](../estandares/fastapi/async-tests.md) de FastAPI y
[*Testing with AnyIO*](../estandares/anyio/testing.rst).

- pytest se configura en `pyproject.toml`.
- El plugin de AnyIO con `anyio_mode = "auto"`.
- `anyio_backend` devuelve `"asyncio"`, con alcance `session`, en `tests/conftest.py`: `asyncpg`
  solo corre sobre asyncio.
- Los tests corren contra Postgres, en un schema de prueba: `models/base.py` usa JSONB,
  `gen_random_uuid()` y `Geography`.
- Una regla que se puede romper en silencio tiene su test, como que la entrada acepte camelCase y
  `snake_case`, o que la base rechace un enum inválido.

## Cómo se hace cumplir

| Convención | Con qué |
|---|---|
| [*Dependencies*, `Annotated`](../estandares/fastapi/dependencies.md) | `FAST002` |
| FastAPI, `response_model` y parámetros de ruta | `FAST001`, `FAST003` |
| Modelos de Pydantic tipados | plugin `pydantic.mypy` |
| Routers en `routers/` | `scripts/verificar.py` |
| Capas | `TID251` en el `ruff.toml` de `services/`, `models/` y `schemas/` |
| El entorno solo en `settings.py` | `TID251` en `pyproject.toml` |
| `asyncpg`, [PyJWT](../estandares/fastapi/oauth2-jwt.md) y AnyIO | `scripts/verificar.py` rechaza `python-jose`, `passlib`, `psycopg` y `pytest-asyncio` |
| pytest en `pyproject.toml` | `scripts/verificar.py` |
| camelCase, `extra="forbid"` y base64 | `app/schemas/base.py` canónico |
| Campos del sobre de error | `ProblemDetails` en `app/schemas/base.py` canónico |
| Cada `ProblemType` responde en `/problems/{slug}` | `tests/test_conventions.py` |
| Toda operación declara sus errores como `ProblemDetails` | `tests/test_conventions.py` |
| [RFC 9457, `application/problem+json`](../estandares/rfc/rfc9457.txt) y `traceId` | `tests/test_conventions.py` |
| Archivos canónicos iguales a los de canone: `app/models/base.py`, `app/schemas/base.py`, `app/core/tracing.py`, los tres `ruff.toml` y `tests/test_conventions.py` | `scripts/verificar.py` |
| La entrada acepta camelCase y `snake_case` | Tests del repositorio |

### Configuración

La base está en [`plantilla/server/pyproject.toml`](../plantilla/server/pyproject.toml). Sobre la de
[python.md](python.md) suma:

- `FAST` en ruff y el plugin `pydantic.mypy`.
- `os.environ` y `os.getenv` en `banned-api`, con `app/core/settings.py` como excepción.
- `pythonpath = ["."]` en pytest, para que los tests importen `app`.
- `extend-exclude` con los archivos canónicos, `alembic/env.py`, `alembic/versions/` y `scripts/`:
  reformatear un canónico lo separa de su fuente.

### CI

Los pasos están en el job `server` de
[`plantilla/.github/workflows/ci.yml`](../plantilla/.github/workflows/ci.yml). pytest corre contra
el schema de prueba.
