# FastAPI

Un servidor en FastAPI. Se suma a [python.md](python.md).

## Estructura

Estándares: [*Bigger Applications - Multiple Files*](../estandares/fastapi/bigger-applications.md)
de FastAPI y el [tutorial](../estandares/alembic/tutorial.rst) de Alembic.

```text
server/
  pyproject.toml
  uv.lock
  alembic.ini
  alembic/
    env.py            el de la plantilla async
    script.py.mako
    versions/
  src/app/
    __init__.py
    main.py           crea la app, monta los routers y registra los handlers de errores
    config.py         Settings
    database.py       el engine y la fábrica de sesiones
    dependencies.py   las dependencias compartidas, como la sesión y el usuario actual
    errors.py         la excepción de la app y los handlers que responden problem+json
    tracing.py        el trace-id de cada petición, en el log y en los errores
    enums.py          los enums de la app
    models/
      base.py         la base declarativa, los tipos de PostgreSQL y los nombres
      ruff.toml       el largo de línea que deja cada columna en un renglón
      <dominio>/
        __init__.py
        <modelo>.py   una tabla
    schemas/
      base.py         el modelo base en camelCase, la página y el problema
      <recurso>.py
    routers/
      <recurso>.py
    services/
      <recurso>.py
  tests/
    conftest.py
    test_conventions.py
```

- El paquete se llama `app` en todo servidor. Los archivos canónicos lo importan por nombre y se
  copian sin editar.
- `database.py`, `errors.py`, `tracing.py` y `enums.py` le dan un lugar fijo a lo que el estándar
  no ubica. `config.py` es el módulo que propone la guía de configuración. Todos van directo en
  `app/`, junto a `main.py` y `dependencies.py`: son módulos únicos de toda la app, como los que
  ubica el estándar.
- Cada modelo va en su propio archivo, dentro de la carpeta de su dominio. Cada tabla tiene un
  solo lugar posible.
- Un router recibe la petición, llama a su servicio y responde. El servicio hace las consultas y
  aplica las reglas del negocio: la misma operación se llama desde una ruta, un WebSocket o una
  tarea sin repetirla.

Plantilla: [`plantilla/server/`](../plantilla/server/). Son canónicos, y se copian sin editar,
`database.py`, `errors.py`, `tracing.py`, `models/base.py`, `models/ruff.toml`,
`schemas/base.py` y `tests/test_conventions.py`.

## Dependencias

Estándar: [*Dependencies*](../estandares/fastapi/dependencies.md) de FastAPI.

## Configuración

Estándares: [*Settings and Environment Variables*](../estandares/fastapi/settings.md) de FastAPI y
[pydantic-settings](../estandares/pydantic-settings/index.md).

- La configuración se lee solo de variables de entorno, y todo campo es obligatorio y sin valor
  por defecto. En desarrollo, las variables salen de `uv run --env-file .env`. Contradice la guía
  de FastAPI, que lee `.env` desde la app: así cada valor tiene un solo origen, y si falta uno el
  servidor no arranca.

## Modelos

Estándar: la [configuración de modelos](../estandares/pydantic/config.md) de Pydantic.

- Los nombres viajan en camelCase. Los esquemas heredan de un modelo base con
  `alias_generator=to_camel`, la entrada se acepta solo con el alias, y los query params de dos
  palabras declaran su `alias`. TypeScript y Dart, dos de los tres lenguajes de cliente, usan
  camelCase.
- Los esquemas de entrada llevan `extra="forbid"`. Un campo mal escrito da 422 en vez de perderse
  en silencio.

## Base de datos

Estándares: [*SQL (Relational) Databases*](../estandares/fastapi/sql-databases.md) de FastAPI, la
[extensión asyncio](../estandares/sqlalchemy/asyncio.rst) y el
[pool de conexiones](../estandares/sqlalchemy/pooling.rst) de SQLAlchemy.

- El ORM es SQLAlchemy 2.0. Contradice el tutorial de FastAPI, que usa SQLModel: la tabla y el
  contrato de la API cambian por separado, y los tipos de PostGIS y el async son de primera clase
  en SQLAlchemy.
- Todo es async: rutas y dependencias con `async def`, `AsyncSession` y el driver asyncpg.
  WebSocket y Redis ya son async, y con un solo modelo no se bloquea el loop por error.
- Toda relación lleva `lazy="raise"`. Endurece la carga anticipada que pide SQLAlchemy: una carga
  implícita falla con un error claro en vez de `MissingGreenlet`.
- Cada columna se declara en una sola línea. Contradice las 99 de [python.md](python.md): la tabla
  se lee de arriba abajo, una columna por renglón.

## Migraciones

Estándares: el [tutorial](../estandares/alembic/tutorial.rst), la
[autogeneración](../estandares/alembic/autogenerate.rst) y la
[plantilla async](../estandares/alembic/async/env.py) de Alembic, y
[*The Importance of Naming Constraints*](../estandares/alembic/naming.rst).

- La `MetaData` lleva la convención de nombres que da la documentación de Alembic. Una migración
  borra o cambia una restricción por su nombre, y así el nombre no lo elige la base.

## Errores

Estándares: [*Handling Errors*](../estandares/fastapi/handling-errors.md) de FastAPI,
[RFC 9457](../estandares/rfc/rfc9457.txt) y [RFC 6901](../estandares/rfc/rfc6901.txt).

- `type` es una URI `tag:<dominio>,<año>:<nombre>`, o `about:blank` cuando basta el status.
  Cumple la URI absoluta que recomienda RFC 9457 sin obligar a servir una página por cada tipo.
- Los errores propios se lanzan con una excepción de la app que lleva `type`, `title` y `status`.
  Los handlers de `errors.py` la convierten en problem+json, igual que a los `HTTPException` de
  Starlette, a los errores de validación y a toda excepción sin atrapar. Toda respuesta de error
  sale por un solo punto.
- Un error de validación es un 422 en problem+json con la extensión `errors`, una lista de
  `{detail, pointer}` como en el ejemplo de RFC 9457. En query, path y header, `parameter` toma el
  lugar de `pointer`. Contradice el `{"detail": [...]}` de FastAPI: el sobre es uno solo, y el
  cliente marca el campo exacto.

## Trazas

Estándar: [Trace Context](../estandares/w3c/trace-context-1.md) de W3C.

- Cada petición y cada WebSocket empiezan una traza nueva, aunque lleguen con `traceparent`. Es el
  reinicio que el estándar prevé para la puerta de entrada de un sistema: el cliente no elige el
  id con el que se buscan sus registros.
- Cada línea de log lleva el trace-id de su petición, y cada problem+json lo devuelve en la
  extensión `traceId`. Con el id que ve el usuario se llega a la línea exacta del registro.

## Fechas

Estándar: [RFC 3339](../estandares/rfc/rfc3339.txt).

- Las fechas viajan en UTC, con `Z`.

## Paginación

- Las listas se paginan por cursor: la petición lleva `limit` y `cursor`, y la respuesta `items` y
  `nextCursor`. Un offset salta o repite filas si la lista cambia entre páginas.

## Salud

- `GET /api/health` consulta la base con `SELECT 1` y responde 200 con `{"status": "ok"}`, o 503
  si la base no contesta. Un monitor que solo ve que el proceso responde da por vivo un servidor
  con la base caída.

## Reintentos

Estándar: [RFC 9110](../estandares/rfc/rfc9110.txt).

- Una creación que el cliente puede reintentar va por `PUT /<recurso>/{id}`, con un uuid v4 que
  genera el cliente, y no por `POST`. El estándar admite los dos para crear, pero solo `PUT` es
  idempotente: si la respuesta se pierde, la petición repetida cae sobre la misma fila en vez de
  crear otra.

## Versión mínima de cliente

- Cada cliente instalable manda su versión en toda petición, en la cabecera `Client-Version` con
  la forma `<pieza>/<versión>`, como `mobile/1.4.0`. La configuración guarda la versión mínima de
  cada pieza, y una versión menor recibe un 400 en problem+json de nombre `client-outdated`, que
  el cliente muestra como «actualiza la app».
- La comprobación va desde la primera versión que se publica: a una app instalada sin ella nunca
  se le puede obligar a actualizar.

## Ciclo de vida

Estándar: [*Lifespan Events*](../estandares/fastapi/events.md) de FastAPI.

## Tareas en segundo plano

Estándar: [*Background Tasks*](../estandares/fastapi/background-tasks.md) de FastAPI.

## Detrás de un proxy

Estándar: [*Behind a Proxy*](../estandares/fastapi/behind-a-proxy.md) de FastAPI.

## OpenAPI y clientes

Estándar: [*Generating SDKs*](../estandares/fastapi/generate-clients.md) de FastAPI.

- Cada router lleva un tag, y el operation ID es `<tag>-<función>`. Los métodos de los clientes
  generados quedan legibles.

## Pruebas

Estándares: [*Testing*](../estandares/fastapi/testing.md) y
[*Async Tests*](../estandares/fastapi/async-tests.md) de FastAPI, y las
[pruebas con AnyIO](../estandares/anyio/testing.rst).

- Las pruebas usan `httpx.AsyncClient` con `ASGITransport`. Contradice el `TestClient` de la guía:
  corre la app en otro loop, y el engine async falla con «attached to a different loop».
- `anyio_backend` es `asyncio`. asyncpg y la app solo corren en asyncio.
- Las pruebas corren contra PostgreSQL, cada una dentro de una transacción que se revierte al
  terminar. SQLite no tiene los tipos de PostGIS, y revertir aísla cada prueba sin recrear las
  tablas.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| *Dependencies*: `Annotated` | ruff `FAST002` |
| mypy strict, de [python.md](python.md), sobre los modelos de Pydantic | plugin `pydantic.mypy` |
| Los esquemas heredan del modelo base | `test_schemas_inherit_schema` |
| `lazy="raise"` | `test_relationships_raise` |
| Una columna por línea | `ruff format` con `line-length = 320`, el máximo de ruff, en `models/ruff.toml` |
| Toda respuesta de error en problem+json, con `traceId` | `test_unknown_route_is_a_problem` y `test_validation_error_points_to_the_field` |
| El operation ID `<tag>-<función>` | `test_operation_ids` |
| Las reglas de [postgres.md](postgres.md) | Las pruebas de `tests/test_conventions.py` que nombra esa página |
