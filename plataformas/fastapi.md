# FastAPI

Un servidor en FastAPI. Se suma a [python.md](python.md).

## Proyecto

Estándares: la sección *An example file structure* de
[*Bigger Applications - Multiple Files*](../estandares/fastapi/bigger-applications.md) de FastAPI y
la sección *Creating an Environment* del [tutorial](../estandares/alembic/tutorial.rst) de Alembic.

```text
server/
  .gitignore
  pyproject.toml
  uv.lock
  alembic.ini
  alembic/
    env.py
    README
    script.py.mako
    versions/
  src/app/
    __init__.py
    main.py
    config.py
    database.py
    dependencies.py
    errors.py
    tracing.py
    enums.py
    models/
      __init__.py
      base.py
      ruff.toml
      <dominio>/
        __init__.py
        <modelo>.py
    schemas/
      __init__.py
      base.py
      page.py
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
    test_<recurso>.py
```

Plantilla: [`plantilla/server/`](../plantilla/server/) y el job `server` de
[`plantilla/.github/workflows/ci.yml`](../plantilla/.github/workflows/ci.yml). Se copian sin editar
`alembic.ini`, `alembic/`, `database.py`, `tracing.py`, `models/__init__.py`, `models/base.py`,
`models/ruff.toml`, `schemas/base.py`, `schemas/page.py`, los `health.py` de `routers/`, `schemas/`
y `services/`, y `tests/test_conventions.py`. Se copian y se completan `config.py`,
`dependencies.py`, `enums.py`, `errors.py`, `main.py` y `tests/conftest.py`.

## Configuración

Estándares: las secciones *Pydantic `Settings`* y *Settings in another module* de
[*Settings and Environment Variables*](../estandares/fastapi/settings.md) de FastAPI, y
[pydantic-settings](../estandares/pydantic-settings/index.md).

- Todo campo de `Settings` es obligatorio y sin valor por defecto.
- En desarrollo, las variables salen de `uv run --env-file .env`.

## Esquemas

Estándar: la [configuración de modelos](../estandares/pydantic/config.md) de Pydantic.

Contrato: [transversal.md](transversal.md#nombres-en-el-cable).

- `alias_generator=to_camel` y `serialize_by_alias=True` en el esquema base.
- `extra="forbid"` en los esquemas de entrada.
- Los parámetros de query se declaran en un esquema de entrada. Un parámetro desconocido responde
  422 en vez de ignorarse.

## Base de datos

Estándares: [*Session Basics*](../estandares/sqlalchemy/session_basics.rst), la
[extensión asyncio](../estandares/sqlalchemy/asyncio.rst) y el
[pool de conexiones](../estandares/sqlalchemy/pooling.rst) de SQLAlchemy.

- `AsyncSession` con asyncpg.
- `lazy="raise"` en toda relación.
- Una relación bidireccional declara `back_populates` en los dos lados. Con `backref`, el atributo
  del otro lado no aparece en su clase ni en sus tipos.
- Cada modelo va en su propio archivo, dentro de la carpeta de su dominio.
- Cada columna y cada relación se declaran en una sola línea. Contradice las 99 de
  [python.md](python.md): el modelo se lee de arriba abajo, una declaración por renglón.
- Un enum hereda de `StrEnum`. La `Base` guarda solo esos como `text` con `CHECK`; un `str, Enum`
  se vuelve un enum nativo de Postgres que guarda el nombre y no el valor.

## Migraciones

Estándares: el [tutorial](../estandares/alembic/tutorial.rst), salvo *Creating an Environment*, la
[autogeneración](../estandares/alembic/autogenerate.rst) y la
[plantilla async](../estandares/alembic/async/env.py) de Alembic, y
[*The Importance of Naming Constraints*](../estandares/alembic/naming.rst).

## Inyección de dependencias

Estándares: [*Dependencies*](../estandares/fastapi/dependencies.md) y
[*Dependencies with yield*](../estandares/fastapi/dependencies-with-yield.md) de FastAPI.

- La dependencia de la `AsyncSession` lleva `scope="function"`. El commit corre antes de enviar la
  respuesta: si falla, el cliente recibe el error y no un 200.

## Routers

Estándar: las secciones *`APIRouter`*, *Another module with `APIRouter`*, *The main `FastAPI`* e
*Include an `APIRouter` in another* de
[*Bigger Applications - Multiple Files*](../estandares/fastapi/bigger-applications.md) de FastAPI.

Contrato: [transversal.md](transversal.md#sesión).

- Los routers se incluyen en un `APIRouter(prefix="/api")` de `main.py`.
- Un recurso lleva el mismo nombre de archivo en `routers/`, `services/` y `schemas/`.

## Ciclo de vida

Estándar: [*Lifespan Events*](../estandares/fastapi/events.md) de FastAPI.

## Tareas en segundo plano

Estándares: [*Background Tasks*](../estandares/fastapi/background-tasks.md) y la sección
*Background Tasks and Dependencies with `yield`, Technical Details* de
[*Advanced Dependencies*](../estandares/fastapi/advanced-dependencies.md) de FastAPI.

## Archivos

Estándares: [*File Upload Cheat Sheet*](../estandares/owasp/File_Upload.md) de OWASP y
[*Request Files*](../estandares/fastapi/request-files.md) de FastAPI.

- El servidor recibe un archivo como `UploadFile`.
- Toda imagen se vuelve a codificar con Pillow antes de guardarse. Endurece OWASP, que lo da como
  técnica: también borra los metadatos de la foto.
- Cada archivo es una fila de una tabla hija de su recurso, `<recurso>_file`, con
  `ON DELETE CASCADE`. La fila guarda el tipo, el tamaño y el nombre original.
- El archivo en disco se llama con el ID de su fila.
- Un archivo tiene los permisos de su recurso.
- Un barrido borra los archivos con más de una hora en disco y sin fila en ninguna tabla `_file`.

## Autenticación

Estándares: [*Authentication Cheat Sheet*](../estandares/owasp/Authentication.md) de OWASP, salvo
*Implement Proper Password Strength Controls*, *Implement Secure Password Recovery Mechanism*,
*Store Passwords in a Secure Fashion*, *Compare Password Hashes Using Safe Functions*,
*Multi-Factor Authentication* y *Use of authentication protocols that require no password*, y
[*Forgot Password Cheat Sheet*](../estandares/owasp/Forgot_Password.md) de OWASP.

- Una pieza inicia sesión con passkeys. Usa contraseña solo si uno de sus clientes no puede usar
  passkeys, y entonces la contraseña es su único método.
- El registro verifica un correo o un teléfono, que es también a donde se envía el código para
  recuperar la cuenta.
- El token del enlace para restablecer la contraseña vence en 30 minutos, y la base guarda su
  SHA-256.

## Contraseñas

Estándares: la sección 3.1.1 *Passwords* de [NIST SP 800-63B-4](../estandares/nist/sp800-63b-4.txt),
salvo cómo se guarda la contraseña, y las secciones *Password hashing*, *Install `pwdlib`* y
*Hash and verify the passwords* de
[*OAuth2 with Password (and hashing), Bearer with JWT tokens*](../estandares/fastapi/oauth2-jwt.md)
de FastAPI.

- Toda contraseña tiene al menos 8 caracteres. Contradice NIST, que pide 15 cuando es el único
  factor: una contraseña de 15 caracteres aleja al usuario.
- La lista de bloqueo es un archivo del servidor.

## Correo

Estándares: [RFC 5322](../estandares/rfc/rfc5322.txt), [RFC 7208](../estandares/rfc/rfc7208.txt)
(SPF), [RFC 6376](../estandares/rfc/rfc6376.txt) (DKIM), [RFC 7489](../estandares/rfc/rfc7489.txt)
(DMARC), [RFC 8058](../estandares/rfc/rfc8058.txt) y, de Amazon SES,
[*Understanding email deliverability*](../estandares/aws-ses/send-email-concepts-deliverability.md),
[DKIM](../estandares/aws-ses/dkim.md), [*Using a custom MAIL FROM domain*](../estandares/aws-ses/mail-from.md),
[DMARC](../estandares/aws-ses/dmarc.md),
[la lista de supresión](../estandares/aws-ses/suppression-list.md) y
[*Monitor email sending using event publishing*](../estandares/aws-ses/monitor-using-event-publishing.md).

- El correo sale por SES con la API v2, desde `asyncio.to_thread`.
- Cada correo lleva una parte en texto y otra en HTML.
- Un correo que no responde a una acción del usuario lleva `List-Unsubscribe` y
  `List-Unsubscribe-Post`.
- Los rebotes y las quejas llegan por event publishing a un endpoint del servidor, que marca la
  dirección como inválida. La app sabe que el correo no llega y se lo dice al usuario.

## Direcciones

Estándar: la [política de uso de Nominatim](../estandares/osm/nominatim-usage-policy.md).

- Las respuestas de Nominatim se guardan en Redis.

## Envíos al exterior

- Primero la evidencia en la base, después el envío best-effort. Un fallo de entrega no tumba la
  operación.

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

## Fechas

Estándar: [RFC 3339](../estandares/rfc/rfc3339.txt).

- Un instante viaja en UTC, con `Z`.
- Los campos de fecha y hora de los esquemas son `AwareDatetime`. Un `datetime` acepta una hora sin
  zona, que RFC 3339 no admite.

## Límite de tasa

Estándar: la sección 4 de [RFC 6585](../estandares/rfc/rfc6585.txt), *429 Too Many Requests*.

- Los contadores viven en Redis, compartidos por todos los procesos.
- Todo 429 lleva `Retry-After`. Endurece RFC 6585, que lo deja opcional: el cliente sabe cuándo
  reintentar.

## Montos

Estándares: [I-JSON](../estandares/rfc/rfc7493.txt), RFC 7493, y la
[lista de monedas](../estandares/iso/iso-4217-list-one.xml) de ISO 4217.

- Un monto viaja como `{"amount": "10.50", "currency": "USD"}`: el monto en una cadena decimal y la
  moneda en su código ISO 4217. Un monto no se formatea sin su moneda.

## OpenAPI y clientes

Estándar: [*Generating SDKs*](../estandares/fastapi/generate-clients.md) de FastAPI.

- Cada router lleva un solo tag, y el operation ID es `<tag>-<función>`.

## Paginación

- Toda lista que puede crecer se pagina desde que se crea su ruta. Una lista sin límite crece hasta
  que la respuesta tarda o se corta.
- Una lista se pagina por cursor, salvo que muestre números de página. Un offset salta o repite
  filas si la lista cambia entre páginas.
- Una ruta tiene un solo modo.
- `limit` vale 50 por defecto y 100 como máximo en los dos modos. Fuera de rango responde 422.
- Toda lista paginada se ordena por una columna y el `id` como desempate. Dos filas con el mismo
  valor no se saltan ni se repiten.

Por cursor:

- La petición es `CursorParams`: `limit` y `cursor` en la query. Sin `cursor`, devuelve la primera
  página.
- La respuesta es `CursorPage[T]`: `{"items": [...], "nextCursor": "..."}`, y la última página
  lleva `"nextCursor": null`. El campo siempre está, y el cliente tipado no pregunta si existe.
- El cursor guarda en base64url la columna y el `id` del último elemento, y los filtros. El
  cliente no lo arma ni lo lee: el servidor puede cambiar su contenido sin tocar a ningún cliente.
- Un cursor ilegible o con filtros distintos de los de la petición responde 422 de tipo
  `validation`, con `parameter: "cursor"`.
- La respuesta no lleva el total. Contarlo recorre toda la tabla en cada petición.

Numerada:

- La petición es `NumberedParams`: `limit` y `page`, que empieza en 1. `?page=3` es la dirección
  que se comparte.
- La respuesta es `NumberedPage[T]`: `{"items": [...], "total": 123}`.
- Un `page` después de la última página devuelve `items` vacío con su `total`.

## Pagos

Estándares: [*Idempotent requests*](../estandares/stripe/idempotent-requests.md) y los
[webhooks](../estandares/stripe/webhooks.md) de Stripe.

- El ID de cada evento procesado se guarda con una restricción única. Un evento repetido choca con
  ella y no se procesa dos veces.

## Passkeys

Estándares: [*Web Authentication Level 3*](../estandares/w3c/webauthn-3.bs) de W3C, las secciones
3.1.7 *Multi-Factor Cryptographic Authentication*, 4.2 *Account Recovery* y el apéndice B
*Syncable Authenticators* de [NIST SP 800-63B-4](../estandares/nist/sp800-63b-4.txt), la sección
4.1 *Authorization Code Grant* de [RFC 6749](../estandares/rfc/rfc6749.txt),
[RFC 7636](../estandares/rfc/rfc7636.txt) y [RFC 8252](../estandares/rfc/rfc8252.txt).

- Las passkeys se validan con `webauthn`.
- Toda passkey es descubrible (`residentKey="required"`): el usuario entra sin escribir su correo.
- Una cuenta se recupera con un código guardado y un código enviado a su correo o a su teléfono.
- Una cuenta de administración rechaza la passkey que no verificó al usuario: sin esa verificación
  la passkey es un solo factor.
- Una cuenta de administración la recupera otro administrador, nunca un código: quien roba el
  correo y el código guardado no se lleva la administración.

## Permisos

Estándares: [*Authorization Cheat Sheet*](../estandares/owasp/Authorization.md) de OWASP y las
secciones 15.5.4 *403 Forbidden* y 15.5.5 *404 Not Found* de
[RFC 9110](../estandares/rfc/rfc9110.txt).

- Cada ruta declara con una dependencia de FastAPI el permiso que exige. El permiso queda a la
  vista en la ruta.
- Un recurso que no pertenece al usuario responde 404, como si no existiera; uno que el usuario ve
  pero sobre el que no puede hacer esa acción responde 403. Es la opción que RFC 9110 da para
  ocultar un recurso: una sola consulta, filtrada por el usuario, resuelve las dos cosas y no
  confirma que el recurso existe.

## Push

Estándares: [*Send a message using Firebase Admin SDK*](../estandares/firebase/admin-sdk.md),
[*FCM Error Codes*](../estandares/firebase/error-codes.md),
[RFC 8030](../estandares/rfc/rfc8030.txt) y [RFC 8291](../estandares/rfc/rfc8291.txt).

- El servidor envía a FCM con el Admin SDK de Python desde `asyncio.to_thread`. El SDK es síncrono.
- El servidor envía Web Push con pywebpush.

## Registro de eventos

Estándar: [*Logging Cheat Sheet*](../estandares/owasp/Logging.md) de OWASP.

## Reintentos

Estándar: las secciones 9.2.2 *Idempotent Methods* y 9.3.4 *PUT* de
[RFC 9110](../estandares/rfc/rfc9110.txt).

- Una creación que el cliente puede reintentar va por `PUT /<recurso>/{id}`, con un uuid v4 que
  genera el cliente. Si la respuesta se pierde, la petición repetida cae sobre la misma fila en vez
  de crear otra.

## Salud

- `GET /api/health` consulta la base con `SELECT 1` y responde 200 con `{"status": "ok"}`, o 503
  si la base no contesta. Un monitor que solo ve que el proceso responde da por vivo un servidor
  con la base caída.

## Tokens

Estándares: [RFC 7519](../estandares/rfc/rfc7519.txt), [RFC 8725](../estandares/rfc/rfc8725.txt)
y [*JSON Web Token Cheat Sheet*](../estandares/owasp/JSON_Web_Token.md) de OWASP.

- El token de acceso es un JWT firmado con HS256 que vence en 15 minutos.
- El token de refresco es un valor aleatorio de 256 bits, y la base guarda su SHA-256 en la fila de
  sesión. Rota en cada uso, y usar uno ya rotado borra la sesión entera: un token robado se
  descubre cuando el dueño vuelve a refrescar.
- Cada dispositivo tiene una fila de sesión, con su creación y su último uso. La sesión vence tras
  30 días sin uso, y cerrar sesión borra la fila.

## Trazas

Estándar: las secciones 3.2.2.3 *trace-id* y 8, *Considerations for trace-id field generation*,
de [Trace Context](../estandares/w3c/trace-context-1.md) de W3C.

- Cada petición y cada WebSocket empiezan una traza nueva, aunque lleguen con `traceparent`. El
  cliente no elige el id con el que se buscan sus registros.
- El trace-id va en cada línea de log y en la extensión `traceId` de cada problem+json. Con el id
  que ve el usuario se llega a la línea exacta del registro.

## Versión mínima de cliente

Estándar: las secciones 10.1.5 *User-Agent* y 15.5.1 *400 Bad Request* de
[RFC 9110](../estandares/rfc/rfc9110.txt).

- Cada cliente instalable manda `User-Agent: <pieza>/<versión>`, como `mobile/1.4.0`.
- La configuración guarda la versión mínima de cada pieza. Una versión menor recibe un 400 de tipo
  `https://<dominio>/problems/client-outdated`, y el cliente pide actualizar la app.
- La comprobación va desde la primera versión que se publica: a una app instalada sin ella nunca
  se le puede obligar a actualizar.

## WebSocket

Estándares: [*WebSockets*](../estandares/fastapi/websockets.md) de FastAPI y
[*Redis Pub/sub*](../estandares/redis/pubsub.md).

- Cerrar sesión cierra sus conexiones en todos los procesos.
- Cada proceso se suscribe a Redis y reenvía a sus conexiones, con un canal por usuario. Pub/sub
  entrega a lo sumo una vez; por eso el cliente pide el estado por REST al reconectar.

## Pruebas

Estándares: [*Async Tests*](../estandares/fastapi/async-tests.md) de FastAPI, las
[pruebas con AnyIO](../estandares/anyio/testing.rst) y
[*Joining a Session into an External Transaction*](../estandares/sqlalchemy/session_transaction.rst)
de SQLAlchemy.

- `anyio_backend` es `asyncio`. asyncpg y la app solo corren en asyncio.
- Las pruebas corren contra PostgreSQL. Ven los mismos tipos y restricciones que producción.

## Detrás de un proxy

Estándar: [*Behind a Proxy*](../estandares/fastapi/behind-a-proxy.md) de FastAPI.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| *Dependencies*: `Annotated` | ruff `FAST002` |
| Los nombres en camelCase: todo esquema hereda del esquema base | `test_schemas_inherit_schema` |
| `lazy="raise"` | `test_relationships_raise` |
| `AwareDatetime` en los esquemas | `test_schema_datetimes_are_aware` |
| Un enum hereda de `StrEnum` | `test_enums_are_checked_text` y ruff `UP042` |
| Una columna o relación por línea | `test_mapped_attributes_fit_one_line`, y `ruff format` con `line-length = 320`, el máximo de ruff, en `models/ruff.toml` |
| Toda respuesta de error en problem+json, con `traceId` | `test_unknown_route_is_a_problem` y `test_validation_error_points_to_the_field` |
| Un solo tag por router y el operation ID `<tag>-<función>` | `test_operation_ids` |
| La versión mínima de cliente | `test_outdated_client_is_rejected` |
| Un cursor ilegible o con otros filtros responde 422 | `test_invalid_cursor_points_to_the_parameter` |
| Las reglas de [postgres.md](postgres.md) | Las pruebas de `tests/test_conventions.py` que nombra esa página |
