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
    tasks.py
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
`alembic.ini`, `alembic/README`, `alembic/env.py`, `alembic/script.py.mako`, `database.py`,
`tracing.py`, `models/__init__.py`, `models/base.py`, `models/ruff.toml`, `routers/problems.py`,
`schemas/base.py`, `schemas/page.py` y `tests/test_conventions.py`. Se copian y se completan
`config.py`, `dependencies.py`, `enums.py`, `errors.py`, `main.py`, los `health.py` de `routers/`,
`schemas/` y `services/`, y `tests/conftest.py`.

<br>

---
---

<br>

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
- Una relación bidireccional declara `back_populates` en los dos lados.
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

- Los routers se incluyen en un `APIRouter(prefix="/api")` de `main.py`.
- Un recurso lleva el mismo nombre de archivo en `routers/`, `services/` y `schemas/`.

## Ciclo de vida

Estándar: [*Lifespan Events*](../estandares/fastapi/events.md) de FastAPI.

## Tareas en segundo plano

Estándares: [*Background Tasks*](../estandares/fastapi/background-tasks.md) y la sección
*Background Tasks and Dependencies with `yield`, Technical Details* de
[*Advanced Dependencies*](../estandares/fastapi/advanced-dependencies.md) de FastAPI.

## Tareas periódicas

- Una tarea periódica es una función en `services/`.
- La tarea trabaja sobre lo que encuentra en la base, no sobre lo que pasó desde la vuelta
  anterior: una vuelta perdida la recupera la siguiente.
- La dispara un timer de systemd con `python -m app.tasks <tarea>`: systemd no arranca una vuelta
  si la anterior sigue corriendo.

<br>

---
---

<br>

## Archivos

Estándares: [*File Upload Cheat Sheet*](../estandares/owasp/File_Upload.md) de OWASP y
[*Request Files*](../estandares/fastapi/request-files.md) de FastAPI.

Contrato: [transversal.md](transversal.md#archivos).

- El servidor recibe un archivo como `UploadFile`.
- Toda imagen se vuelve a codificar con Pillow antes de guardarse. Endurece OWASP, que lo da como
  técnica: también borra los metadatos de la foto.
- Cada archivo es una fila de una tabla hija de su recurso, `<recurso>_file`, con
  `ON DELETE CASCADE`.
- La fila de un archivo guarda su tipo, su tamaño y su nombre original.
- El archivo en disco se llama con el ID de su fila.
- Un archivo tiene los permisos de su recurso.
- Un barrido borra los archivos con más de una hora en disco y sin fila en ninguna tabla `_file`.
  El margen deja terminar la subida que todavía no confirmó su fila.

## Autenticación

Estándar: las secciones V6.1 *Authentication Documentation* y V6.3 *General Authentication
Security*, en el nivel 1, de [ASVS 5.0](../estandares/owasp/ASVS_V6_Authentication.md) de OWASP.

- El registro verifica un correo o un teléfono, y el que falte se agrega desde una sesión abierta,
  verificado con un código.
- Una cuenta no tiene nombre de usuario: es un dato más que recordar.
- El registro responde 409 si la cuenta ya existe.
- Una IP que recibe 10 respuestas 409 del registro en 15 minutos queda bloqueada 30 minutos: quien
  prueba correos o teléfonos en serie busca cuentas existentes.
- Una cuenta de administración inicia sesión solo con passkeys.
- Cambiar el correo, el teléfono o una passkey pide volver a autenticarse en ese momento: una
  sesión robada no se queda con la cuenta.
- El correo se cambia desde una sesión abierta, con un código enviado al correo nuevo, y el correo
  viejo recibe un aviso.
- El conteo de intentos fallidos vive en Valkey.
- Una cuenta con 10 intentos fallidos en 15 minutos queda bloqueada 30 minutos, y con el segundo
  bloqueo queda bloqueada hasta que el titular lo levanta.
- El segundo bloqueo es un estado de la cuenta en la base: si Valkey pierde sus datos, el bloqueo
  sigue.
- El titular ve en la app cada intento fallido y cada bloqueo de su cuenta.
- El bloqueo cierra solo el login: las sesiones abiertas siguen, y el titular lo levanta desde una
  de ellas.
- El login con contraseña responde el mismo error exista o no la cuenta.

## Código por SMS

Estándar: la sección 3.1.3.2 *Out-of-Band Verifiers* de
[NIST SP 800-63B-4](../estandares/nist/sp800-63b-4.txt).

Contrato: [transversal.md](transversal.md#código-por-sms).

- El servidor valida el número con `phonenumbers`.
- Verificar el primer código de un número sin cuenta crea la cuenta.
- El código vive en Valkey, con un TTL de 10 minutos.
- Un código nuevo reemplaza al anterior: solo vale el último.
- Cada número recibe un SMS por minuto, hasta 5 por hora y hasta 10 por día, y cada IP pide hasta
  10 por hora.
- Un código se invalida al tercer intento fallido, y un código mal escrito no bloquea la cuenta.
  Contradice NIST, que pide no reiniciar el conteo de fallos con un código nuevo: el límite diario
  ya acota los intentos.
- El número se cambia desde una sesión abierta, con un código enviado al número nuevo, y el número
  viejo recibe un aviso.
- Quien perdió su número recupera la cuenta con un administrador.

## Contraseñas

Estándares: las secciones V6.2 *Password Security* y V6.4 *Authentication Factor Lifecycle and
Recovery*, en el nivel 1, de [ASVS 5.0](../estandares/owasp/ASVS_V6_Authentication.md) de OWASP;
las secciones *Password hashing*, *Install `pwdlib`* y *Hash and verify the passwords* de
[*OAuth2 with Password (and hashing), Bearer with JWT tokens*](../estandares/fastapi/oauth2-jwt.md)
de FastAPI, y [*Forgot Password Cheat Sheet*](../estandares/owasp/Forgot_Password.md) de OWASP,
salvo *Security Questions*.

- Toda contraseña tiene al menos 8 caracteres: una de 15 aleja al usuario.
- La lista de bloqueo es un archivo del servidor.
- Una cuenta restablece su contraseña con un código que recibe, a su elección, en el correo o en el
  teléfono que registró.
- La solicitud para restablecer responde 404 si la cuenta no existe, y una IP que recibe 10 en 15
  minutos queda bloqueada 30 minutos. Contradice OWASP, que pide la misma respuesta exista o no la
  cuenta: el registro ya lo revela.
- El código para restablecer tiene 6 dígitos, vive en Valkey con un TTL de 10 minutos, y uno nuevo
  reemplaza al anterior.
- Un código para restablecer se invalida al tercer intento fallido.
- Cada correo y cada número reciben un código para restablecer por minuto, y hasta 5 por hora.
- Cambiar la contraseña cierra las demás sesiones y renueva los tokens de la sesión que hizo el
  cambio; restablecerla cierra todas: quien lo hace puede sospechar de un acceso ajeno.

## Correo y SMS

Estándar: [Standard Webhooks](../estandares/standard-webhooks/standard-webhooks.md).

- El correo sale por la API de correo de Equipaggio, `PUT /email/{id}`, y el SMS, por su pasarela,
  `PUT /sms/{id}`.
- Cada correo lleva una parte en texto y otra en HTML.
- Un correo rebotado llega por el webhook de Equipaggio. El servidor marca la dirección como
  inválida, y la app le dice al usuario que su correo no llega.

## Envíos al exterior

- Primero la evidencia en la base, después el envío best-effort. Un fallo de entrega no tumba la
  operación.

## Errores

Estándar: [*Handling Errors*](../estandares/fastapi/handling-errors.md) de FastAPI.

Contrato: [transversal.md](transversal.md#errores).

- Un error con tipo propio se lanza con `AppError`; uno que su código de estado ya explica, con
  `HTTPException`, y sale como `about:blank`.

## Fechas

Estándar: [RFC 3339](../estandares/rfc/rfc3339.txt).

- Un instante viaja en UTC, con `Z`.
- Los campos de fecha y hora de los esquemas son `AwareDatetime`. Un `datetime` acepta una hora sin
  zona, que RFC 3339 no admite.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

## Límite de tasa

Estándar: la sección 4 de [RFC 6585](../estandares/rfc/rfc6585.txt), *429 Too Many Requests*.

- Los contadores viven en Valkey, compartidos por todos los procesos.
- Todo 429 lleva `Retry-After`. Endurece RFC 6585, que lo deja opcional: el cliente sabe cuándo
  reintentar.

## Llamadas de voz y video

Contrato: [transversal.md](transversal.md#llamadas-de-voz-y-video).

## Mapas

Estándar: la [política de uso de Nominatim](../estandares/osm/nominatim-usage-policy.md).

Contrato: [transversal.md](transversal.md#mapas).

- Las respuestas de Nominatim se guardan en Valkey.

## Montos

Estándares: [I-JSON](../estandares/rfc/rfc7493.txt), RFC 7493, y la
[lista de monedas](../estandares/iso/iso-4217-list-one.xml) de ISO 4217.

Contrato: [transversal.md](transversal.md#montos).

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

Contrato: [transversal.md](transversal.md#pagos).

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
- Una cuenta con passkey se recupera con un código guardado y un código enviado a su correo o a su
  teléfono.
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

Contrato: [transversal.md](transversal.md#push).

- El servidor envía a FCM con el Admin SDK de Python desde `asyncio.to_thread`. El SDK es síncrono.
- El servidor envía Web Push con pywebpush.

## Registro de eventos

Estándar: [*Logging Cheat Sheet*](../estandares/owasp/Logging.md) de OWASP.

- Los eventos van en una sola tabla, `event_log`, con su categoría (`auth`, `security`, `admin` o
  `business`) y su acción, un enum de cada repositorio: lo que pasó alrededor de una hora se lee en
  una consulta.
- Las demás columnas de `event_log`:

  | Columna | Regla |
  |---|---|
  | `occurred_at`, `created_at` | Cuándo pasó y cuándo se escribió |
  | `actor_id` | Nulo si no hay cuenta detrás |
  | `actor_label` | El identificador tal como llegó |
  | `target_type`, `target_id` | Nulos si el evento no es sobre un recurso |
  | `outcome` | `success` o `failure` |
  | `severity` | `low`, `medium`, `high` o `critical` |
  | `ip_address`, `user_agent` | De dónde vino |
  | `trace_id` | El trace-id de la petición, el mismo del log y del `traceId` del error |
  | `details` | `jsonb` |
  | `tenant_id` | En todo evento, si el repositorio es multi-tenant |

- Los cambios de fila van en `audit_log`, con `table_name`, `record_id`, `old_values` y
  `new_values`. Un hecho que no cambia una fila va en `event_log`: no tiene valores anteriores.
- Un valor entra al registro solo si su tabla y su campo están en una lista blanca: una columna
  nueva no se registra sola. Un campo fuera de la lista se registra como cambiado, sin su valor.
- `event_log` y `audit_log` tienen cada uno su retención en días en `Settings`, y `0` la deja
  indefinida.
- Renovar un token no escribe en el registro: sería una fila por cada renovación.

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

## Sesión

Estándares: [RFC 7519](../estandares/rfc/rfc7519.txt), [RFC 8725](../estandares/rfc/rfc8725.txt)
y [*JSON Web Token Cheat Sheet*](../estandares/owasp/JSON_Web_Token.md) de OWASP.

Contrato: [transversal.md](transversal.md#sesión).

- El token de acceso es un JWT firmado con HS256 que vence en 15 minutos.
- El token de refresco es un valor aleatorio de 256 bits que rota en cada uso.
- La fila de sesión guarda el SHA-256 del token de refresco vigente y el del anterior: si un ladrón
  rota, el token que presenta después el dueño es el anterior.
- Presentar el anterior borra la sesión de ese dispositivo, avisa al titular por los medios que
  registró y cuenta como un intento fallido de la cuenta: un token robado se descubre cuando el
  dueño vuelve a refrescar.
- Un token de refresco que no es el vigente ni el anterior responde 401, sin aviso.
- Cada dispositivo tiene una fila de sesión, con su creación y su último uso. La sesión vence tras
  30 días sin uso, y cerrar sesión borra la fila.
- Una tarea periódica borra las sesiones vencidas.

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

Contrato: [transversal.md](transversal.md#versión-mínima-de-cliente).

- Cada cliente instalable manda `User-Agent: <pieza>/<versión>`, como `mobile/1.4.0`.
- La configuración guarda la versión mínima de cada pieza. Una versión menor recibe un 400 de tipo
  `https://<dominio>/api/problems/client-outdated`, y el cliente pide actualizar la app.
- La comprobación va desde la primera versión que se publica: a una app instalada sin ella nunca
  se le puede obligar a actualizar.

## WebSocket

Estándares: [*WebSockets*](../estandares/fastapi/websockets.md) de FastAPI y
[*Pub/Sub*](../estandares/valkey/pubsub.md) de Valkey.

Contrato: [transversal.md](transversal.md#websocket).

- Cerrar sesión cierra sus conexiones en todos los procesos.
- Cada proceso se suscribe a Valkey y reenvía a sus conexiones, con un canal por usuario. Pub/sub
  entrega a lo sumo una vez; por eso el cliente pide el estado por REST al reconectar.

<br>

---
---

<br>

## Pruebas

Estándares: [*Async Tests*](../estandares/fastapi/async-tests.md) de FastAPI, las
[pruebas con AnyIO](../estandares/anyio/testing.rst) y
[*Joining a Session into an External Transaction*](../estandares/sqlalchemy/session_transaction.rst)
de SQLAlchemy.

- `anyio_backend` es `asyncio`. asyncpg y la app solo corren en asyncio.
- Las pruebas corren contra PostgreSQL. Ven los mismos tipos y restricciones que producción.

<br>

---
---

<br>

## Detrás de un proxy

Estándar: [*Behind a Proxy*](../estandares/fastapi/behind-a-proxy.md) de FastAPI.

<br>

---
---

<br>

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Todo campo de `Settings` es obligatorio | `test_settings_are_required` |
| *Dependencies*: `Annotated` | ruff `FAST002` |
| El commit corre antes de enviar la respuesta | `test_failed_commit_is_a_server_error` |
| Los nombres en camelCase: todo esquema hereda del esquema base | `test_schemas_inherit_schema` |
| `lazy="raise"` | `test_relationships_raise` |
| `AwareDatetime` en los esquemas | `test_schema_datetimes_are_aware` |
| Un enum hereda de `StrEnum` | `test_enums_are_checked_text` y ruff `UP042` |
| Una columna o relación por línea | `test_mapped_attributes_fit_one_line`, y `ruff format` con `line-length = 320`, el máximo de ruff, en `models/ruff.toml` |
| El `traceId` en cada problem+json | `test_unknown_route_is_a_problem` |
| Un solo tag por router y el operation ID `<tag>-<función>` | `test_operation_ids` |
| La versión mínima de cliente | `test_outdated_client_is_rejected` |
| Un cursor ilegible o con otros filtros responde 422 | `test_invalid_cursor_points_to_the_parameter` |
| Las reglas de [postgres.md](postgres.md) | Las pruebas de `tests/test_conventions.py` que nombra esa página |
