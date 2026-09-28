# FastAPI

Un servidor en FastAPI. Se suma a [python.md](python.md).

## Estructura

Estándar: [*Bigger Applications - Multiple Files*](../estandares/fastapi/bigger-applications.md) de FastAPI.

- El layout del estándar va en `src/<paquete>/`. Al lado de `routers/` van `models/`, con las
  tablas de SQLAlchemy, y `schemas/`, con los esquemas de Pydantic, con un archivo por recurso en
  cada una.

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

## Migraciones

Estándares: el [tutorial](../estandares/alembic/tutorial.rst), la
[autogeneración](../estandares/alembic/autogenerate.rst) y la
[plantilla async](../estandares/alembic/async/env.py) de Alembic.

## Errores

Estándares: [*Handling Errors*](../estandares/fastapi/handling-errors.md) de FastAPI,
[RFC 9457](../estandares/rfc/rfc9457.txt) y [RFC 6901](../estandares/rfc/rfc6901.txt).

- `type` es una URI `tag:<dominio>,<año>:<nombre>`, o `about:blank` cuando basta el status.
  Cumple la URI absoluta que recomienda RFC 9457 sin obligar a servir una página por cada tipo.
- Los errores propios se lanzan con una excepción de la app que lleva `type`, `title` y `status`.
  Un solo handler la convierte en problem+json, y convierte también los `HTTPException` de
  Starlette. Toda respuesta de error sale por un solo punto.
- Un error de validación es un 422 en problem+json con la extensión `errors`, una lista de
  `{detail, pointer}` como en el ejemplo de RFC 9457. En query, path y header, `parameter` toma el
  lugar de `pointer`. Contradice el `{"detail": [...]}` de FastAPI: el sobre es uno solo, y el
  cliente marca el campo exacto.

## Fechas

Estándar: [RFC 3339](../estandares/rfc/rfc3339.txt).

- Las fechas viajan en UTC, con `Z`.

## Paginación

- Las listas se paginan por cursor: la petición lleva `limit` y `cursor`, y la respuesta `items` y
  `nextCursor`. Un offset salta o repite filas si la lista cambia entre páginas.

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
