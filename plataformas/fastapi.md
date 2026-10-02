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
    env.py            el de la plantilla async, con target_metadata = Base.metadata
    README
    script.py.mako
    versions/
  src/app/
    __init__.py
    main.py           crea la app, monta los routers y registra los handlers de errores
    config.py         Settings
    database.py       el engine y la fábrica de sesiones
    dependencies.py   las dependencias compartidas, como la sesión y el usuario actual
    errors.py         la excepción de la app y los handlers que responden problem+json
    problems.py       la URI de cada tipo de problema
    tracing.py        el trace-id de cada petición, en el log y en los errores
    enums.py          los enums de la app
    models/
      __init__.py     importa todos los modelos
      base.py         la base declarativa, los tipos de PostgreSQL y los nombres
      ruff.toml       el largo de línea que deja cada columna en un renglón
      <dominio>/
        __init__.py
        <modelo>.py   una tabla
    schemas/
      __init__.py
      base.py         el modelo base en camelCase, la página y el problema
      <recurso>.py
    routers/
      __init__.py
      <recurso>.py
    services/
      __init__.py
      <recurso>.py
  tests/
    __init__.py
    conftest.py
    test_conventions.py
```

- `database.py`, `errors.py`, `problems.py`, `tracing.py` y `enums.py` le dan un lugar fijo a lo
  que el estándar no ubica. `config.py` es el módulo que propone la guía de configuración. Todos van directo en
  `app/`, junto a `main.py` y `dependencies.py`: son módulos únicos de toda la app, como los que
  ubica el estándar.
- Cada modelo va en su propio archivo, dentro de la carpeta de su dominio. Cada tabla tiene un
  solo lugar posible.
- `models/__init__.py` importa todos los modelos. Importar cualquiera los registra todos en
  `Base.metadata`, y así la app, Alembic y las pruebas ven las mismas tablas.
- Los routers se montan bajo `/api` en un `APIRouter` de `main.py`, y cada uno declara solo su
  recurso. Las rutas de las pruebas, los logs y el OpenAPI son las que ve el cliente.
- Un router recibe la petición, llama a su servicio y responde. El servicio hace las consultas y
  aplica las reglas del negocio: la misma operación se llama desde una ruta, un WebSocket o una
  tarea sin repetirla.

Plantilla: [`plantilla/server/`](../plantilla/server/). Son canónicos, y se copian sin editar,
`database.py`, `errors.py`, `tracing.py`, `models/__init__.py`, `models/base.py`,
`models/ruff.toml`, `schemas/base.py` y `tests/test_conventions.py`.

## Dependencias

Estándares: [*Dependencies*](../estandares/fastapi/dependencies.md) y
[*Dependencies with yield*](../estandares/fastapi/dependencies-with-yield.md) de FastAPI.

## Configuración

Estándares: [*Settings and Environment Variables*](../estandares/fastapi/settings.md) de FastAPI y
[pydantic-settings](../estandares/pydantic-settings/index.md).

- La configuración se lee solo de variables de entorno: `Settings` no declara `env_file`, y todo
  campo es obligatorio y sin valor por defecto. En desarrollo, las variables salen de
  `uv run --env-file .env`. Así cada valor tiene un solo origen, y si falta uno el servidor no
  arranca.

## Modelos

Estándar: la [configuración de modelos](../estandares/pydantic/config.md) de Pydantic.

- `alias_generator=to_camel` y `serialize_by_alias=True` en el modelo base: los nombres viajan en
  camelCase.
- Un `Query()` de dos palabras declara su `alias` en camelCase.
- `extra="forbid"` en los esquemas de entrada. Un campo mal escrito da 422 en vez de perderse en
  silencio.

## Base de datos

Estándares: [*SQL (Relational) Databases*](../estandares/fastapi/sql-databases.md) de FastAPI, y
[*Session Basics*](../estandares/sqlalchemy/session_basics.rst), la
[extensión asyncio](../estandares/sqlalchemy/asyncio.rst) y el
[pool de conexiones](../estandares/sqlalchemy/pooling.rst) de SQLAlchemy.

- SQLAlchemy 2.0 como ORM, con las tablas separadas de los esquemas de Pydantic. La tabla y el
  contrato de la API cambian por separado.
- `AsyncSession` con asyncpg, y rutas y dependencias con `async def`. Una ruta, un WebSocket y una
  tarea llaman al mismo servicio.
- `lazy="raise"` en toda relación. Una carga implícita falla con un error claro en vez de
  `MissingGreenlet`.
- La sesión es una dependencia con `scope="function"`. El commit corre antes de enviar la
  respuesta: si falla, el cliente recibe el error y no un 200.
- Cada columna se declara en una sola línea.

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

- `type` es una URI `https://<dominio>/problems/<nombre>`. Contradice RFC 9457, que pide servir en
  ella la documentación del tipo: la URI queda fija desde el primer error, y la página puede llegar
  después sin cambiarla.
- Los errores propios se lanzan con `AppError`, que lleva `type`, `title` y `status`.
- Toda respuesta de error es problem+json, también la de un `HTTPException`, la de un error de
  validación y la de una excepción sin atrapar. El cliente lee un solo sobre.
- Un error de validación es un 422 de tipo `https://<dominio>/problems/validation`, con la
  extensión `errors`: una lista de `{detail, pointer}`, o de `{detail, parameter}` en query, path y
  header.

## Trazas

Estándar: [Trace Context](../estandares/w3c/trace-context-1.md) de W3C.

- Cada petición y cada WebSocket empiezan una traza nueva, aunque lleguen con `traceparent`. El
  cliente no elige el id con el que se buscan sus registros.
- El trace-id va en cada línea de log y en la extensión `traceId` de cada problem+json. Con el id
  que ve el usuario se llega a la línea exacta del registro.

## Fechas

Estándar: [RFC 3339](../estandares/rfc/rfc3339.txt).

- Un instante viaja en UTC, con `Z`.
- Los campos de fecha y hora de los esquemas son `AwareDatetime`. Un `datetime` acepta una hora sin
  zona, que RFC 3339 no admite.

## Montos

Estándares: [I-JSON](../estandares/rfc/rfc7493.txt), RFC 7493, y la
[lista de monedas](../estandares/iso/iso-4217-list-one.xml) de ISO 4217.

- Un monto viaja como `{"amount": "10.50", "currency": "USD"}`: el monto en una cadena decimal y la
  moneda en su código ISO 4217. Un monto no se formatea sin su moneda.

## Paginación

- Las listas se paginan por cursor: la petición lleva `limit` y `cursor`, y la respuesta `items` y
  `nextCursor`. Un offset salta o repite filas si la lista cambia entre páginas.
- El cursor es una cadena opaca. El servidor puede cambiar cómo la arma sin romper a ningún
  cliente.

## Salud

- `GET /api/health` consulta la base con `SELECT 1` y responde 200 con `{"status": "ok"}`, o 503
  si la base no contesta. Un monitor que solo ve que el proceso responde da por vivo un servidor
  con la base caída.

## Reintentos

Estándar: [RFC 9110](../estandares/rfc/rfc9110.txt).

- Una creación que el cliente puede reintentar va por `PUT /<recurso>/{id}`, con un uuid v4 que
  genera el cliente. Si la respuesta se pierde, la petición repetida cae sobre la misma fila en vez
  de crear otra.

## Versión mínima de cliente

Estándar: [RFC 9110](../estandares/rfc/rfc9110.txt).

- Cada cliente instalable manda `User-Agent: <pieza>/<versión>`, como `mobile/1.4.0`.
- La configuración guarda la versión mínima de cada pieza. Una versión menor recibe un 400 de tipo
  `https://<dominio>/problems/client-outdated`, y el cliente pide actualizar la app.
- La comprobación va desde la primera versión que se publica: a una app instalada sin ella nunca
  se le puede obligar a actualizar.

## Ciclo de vida

Estándar: [*Lifespan Events*](../estandares/fastapi/events.md) de FastAPI.

## Tareas en segundo plano

Estándares: [*Background Tasks*](../estandares/fastapi/background-tasks.md) y
[*Advanced Dependencies*](../estandares/fastapi/advanced-dependencies.md) de FastAPI.

## Detrás de un proxy

Estándar: [*Behind a Proxy*](../estandares/fastapi/behind-a-proxy.md) de FastAPI.

## OpenAPI y clientes

Estándar: [*Generating SDKs*](../estandares/fastapi/generate-clients.md) de FastAPI.

- Cada router lleva un solo tag, y el operation ID es `<tag>-<función>`. Los métodos de los
  clientes generados quedan legibles.

## Pruebas

Estándares: [*Testing*](../estandares/fastapi/testing.md) y
[*Async Tests*](../estandares/fastapi/async-tests.md) de FastAPI, las
[pruebas con AnyIO](../estandares/anyio/testing.rst) y
[*Joining a Session into an External Transaction*](../estandares/sqlalchemy/session_transaction.rst)
de SQLAlchemy.

- Las pruebas son `async def` y llaman a la app con `httpx.AsyncClient` y `ASGITransport`. El
  `TestClient` corre la app en otro loop, y una conexión del engine async no sirve fuera del loop
  que la abrió.
- `anyio_backend` es `asyncio`. asyncpg y la app solo corren en asyncio.
- Las pruebas corren contra PostgreSQL. Ven los mismos tipos y restricciones que producción.
- Cada prueba abre una transacción que se revierte al terminar, y `SessionFactory` se une a ella con
  `join_transaction_mode="create_savepoint"`. La app, sus tareas y la prueba comparten la
  transacción: un commit que falla en producción también falla en la prueba, y nada queda en la
  base.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| *Dependencies*: `Annotated` | ruff `FAST002` |
| Los nombres en camelCase: todo esquema hereda del modelo base | `test_schemas_inherit_schema` |
| `lazy="raise"` | `test_relationships_raise` |
| `AwareDatetime` en los esquemas | `test_schema_datetimes_are_aware` |
| Una columna por línea | `ruff format` con `line-length = 320`, el máximo de ruff, en `models/ruff.toml` |
| Toda respuesta de error en problem+json, con `traceId` | `test_unknown_route_is_a_problem` y `test_validation_error_points_to_the_field` |
| Un solo tag por router y el operation ID `<tag>-<función>` | `test_operation_ids` |
| La versión mínima de cliente | `test_outdated_client_is_rejected` |
| Las reglas de [postgres.md](postgres.md) | Las pruebas de `tests/test_conventions.py` que nombra esa página |
