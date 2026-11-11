# FastAPI

Un servidor en FastAPI. Se suma a [python.md](python.md).

## Proyecto

- FastAPI 0.162.0, Starlette 1.10.0, pydantic-settings 2.16.2, SQLAlchemy 2.1.8, Alembic 1.20.1, asyncpg 0.32.0, cryptography 50.0.2, OpenTelemetry 1.45.2, AnyIO 4.16.0, Babel 2.18.0, valkey-py 6.2.0, Uvicorn 0.54.0, Pillow 13.0.0, pywebpush 2.5.0, aiohttp 3.14.5, firebase-admin 7.7.0 y httpx-ws 0.9.0.

```text
server/
  .gitignore
  pyproject.toml
  uv.lock
  openapi.json
  alembic.ini
  alembic/
    env.py
    README
    script.py.mako
    versions/
      <revisión>_event_log.py
      <revisión>_<cambio>.py
  src/app/
    __init__.py
    main.py
    openapi.py
    config.py
    database.py
    store.py
    dependencies.py
    errors.py
    tracing.py
    enums.py
    tasks.py
    seeders/
      __init__.py
      <datos>.py
    mock_data/
      __init__.py
      <datos>.py
    models/
      __init__.py
      base.py
      ruff.toml
      event/
        __init__.py
        event_log.py
      <dominio>/
        __init__.py
        <modelo>.py
    schemas/
      __init__.py
      base.py
      page.py
      health.py
      <recurso>.py
    routers/
      __init__.py
      health.py
      problems.py
      <recurso>.py
    services/
      __init__.py
      events.py
      files.py
      health.py
      <recurso>.py
    locale/
      <idioma>/
        LC_MESSAGES/
          messages.po
  tests/
    __init__.py
    conftest.py
    test_conventions.py
    test_events.py
    test_files.py
    test_health.py
    test_tasks.py
    test_<recurso>.py
```

Plantilla: [plantilla/server/](../plantilla/server/) y el job `server` de [plantilla/.github/workflows/ci.yml](../plantilla/.github/workflows/ci.yml). Se copian sin editar `alembic.ini`, `alembic/README`, `alembic/env.py`, `alembic/script.py.mako`, cada `__init__.py`, `database.py`, `openapi.py`, `store.py`, `tracing.py`, `models/base.py`, `models/ruff.toml`, `routers/problems.py`, `schemas/base.py`, `schemas/page.py`, `services/files.py`, `tests/test_conventions.py`, `tests/test_events.py`, `tests/test_files.py` y `tests/test_tasks.py`. Los demás se copian y se completan.

## Estilo

- Cada columna y cada relación de un modelo se declaran en una sola línea, sin el límite de 99 caracteres de [python.md](python.md#estilo): el modelo se lee de arriba abajo, una declaración por renglón.

## Paquetes

- Cada modelo va en su propio archivo, dentro de la carpeta de su dominio.
- Un recurso lleva el mismo nombre de archivo en `routers/`, `services/` y `schemas/`.

## Configuración

- La configuración es una instancia de `Settings`, que hereda de `BaseSettings` de pydantic-settings.
- `Settings` lleva solo lo que cambia entre despliegues. Lo que no cambia es una constante del módulo que lo usa: se versiona y se prueba con el código.
- Todo campo de `Settings` es obligatorio y sin valor por defecto.
- `Settings(_secrets_dir=os.environ["CREDENTIALS_DIRECTORY"])` lee solo los archivos de esa carpeta, sin variables de entorno: cada valor sale de un solo lugar. Cada archivo se llama como su campo con el prefijo `app_`, el que pone systemd al cargar la carpeta ([despliegue.md](despliegue.md#configuración)), y `env_prefix="app_"` lo quita. Una carpeta que no existe solo da un aviso, y cada campo falla igual por faltar. [pydantic-settings 2.16.2](https://raw.githubusercontent.com/pydantic/pydantic-settings/v2.16.2/pydantic_settings/sources/providers/secrets.py)
- En desarrollo, `uv run --env-file .env` apunta `CREDENTIALS_DIRECTORY` a `credentials/`, que git ignora.

## Base de datos

Estándares: [*Session Basics*](../fuentes/sqlalchemy/session_basics.rst) y la [extensión asyncio](../fuentes/sqlalchemy/asyncio.rst) de SQLAlchemy.

- La sesión es una `AsyncSession` con asyncpg.
- Una relación bidireccional declara `back_populates` en los dos lados.
- Un enum hereda de `StrEnum`. La `Base` guarda solo esos como `text` con `CHECK`; un `str, Enum` se vuelve un enum nativo de Postgres que guarda el nombre y no el valor.
- Una columna `created_at` es `CreatedAt`, y una `updated_at` es `UpdatedAt`, de la `Base`. Las dos toman `now()`; `updated_at` lo toma en cada `UPDATE` que emite SQLAlchemy.
- Una relación de uno a muchos deja el borrado al `ON DELETE` de la clave foránea del hijo. Si es `CASCADE`, lleva las cascadas `save-update`, `merge`, `delete` y `delete-orphan`, con `passive_deletes=True`; si es `RESTRICT`, lleva `passive_deletes="all"`. Sin eso, el ORM carga los hijos para ponerles `NULL`: un `CASCADE` falla por el `NOT NULL`, y un `RESTRICT` cambia en silencio una fila que no le pertenece al padre. [SQLAlchemy 2.1.8](https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_1_8/doc/build/orm/cascades.rst)
- Toda relación lleva `lazy="raise"`: lo que se lee de ella se carga antes con una opción de carga, como `selectinload` ([asyncio, *Preventing Implicit IO when Using AsyncSession*](../fuentes/sqlalchemy/asyncio.rst)).
- SQLAlchemy se instala con el extra `asyncio` ([asyncio, *Asyncio Platform Installation Notes*](../fuentes/sqlalchemy/asyncio.rst)).
- El engine y `SessionFactory`, su `async_sessionmaker`, se crean una sola vez, en `database.py` ([Session Basics, *Using a sessionmaker*](../fuentes/sqlalchemy/session_basics.rst)).
- La sesión la abre quien empieza la operación, como la dependencia de una petición o una tarea, y la recibe como argumento cada función que lee o cambia datos. La excepción es el evento que se escribe en su propia transacción, de [Registro de eventos](#registro-de-eventos) ([Session Basics, *Session Frequently Asked Questions*](../fuentes/sqlalchemy/session_basics.rst)).
- Una petición usa una sola sesión y una sola transacción, abiertas con `SessionFactory.begin()`, además de las de sus eventos que se escriben aparte: hacen commit si la ruta termina, rollback si lanza, y se cierran al terminar ([Session Basics, *Framing out a begin / commit / rollback block*](../fuentes/sqlalchemy/session_basics.rst) y [*Session Frequently Asked Questions*](../fuentes/sqlalchemy/session_basics.rst)).
- Una `AsyncSession` se usa en una sola tarea a la vez: cada tarea concurrente abre la suya ([asyncio, *Using AsyncSession with Concurrent Tasks*](../fuentes/sqlalchemy/asyncio.rst)).
- No se usa `async_scoped_session` ([asyncio, *Using asyncio scoped session*](../fuentes/sqlalchemy/asyncio.rst)).
- `SessionFactory` lleva `expire_on_commit=False`, y un atributo se vuelve a leer con `refresh()`, no con `expire()` ([asyncio, *Preventing Implicit IO when Using AsyncSession*](../fuentes/sqlalchemy/asyncio.rst)).
- Un objeto nuevo recibe sus colecciones vacías al crearse ([asyncio, *Preventing Implicit IO when Using AsyncSession*](../fuentes/sqlalchemy/asyncio.rst)).
- Una relación nombra cada cascada que usa, nunca `all` ([asyncio, *Preventing Implicit IO when Using AsyncSession*](../fuentes/sqlalchemy/asyncio.rst)).
- Una columna diferida se lee después de cargarla con su opción de carga ([asyncio, *Preventing Implicit IO when Using AsyncSession*](../fuentes/sqlalchemy/asyncio.rst)).
- Una colección que no se lee entera es `write_only`, nunca `dynamic` ([asyncio, *Preventing Implicit IO when Using AsyncSession*](../fuentes/sqlalchemy/asyncio.rst)).
- Un hijo que pertenece a su padre, en una colección cargada, se borra quitándolo de ella, con la cascada `delete-orphan`, y no con `session.delete()` ([Session Basics, *Deleting*](../fuentes/sqlalchemy/session_basics.rst)).
- Un `AsyncEngine` no se comparte entre bucles de eventos: el que pasa a otro bucle se cierra antes con `dispose()` ([asyncio, *Using multiple asyncio event loops*](../fuentes/sqlalchemy/asyncio.rst)).

## Migraciones

Estándar: la [autogeneración](../fuentes/alembic/autogenerate.rst) de Alembic.

- `alembic/` sale de la plantilla `async` de Alembic: las migraciones corren con asyncpg, como la app.
- Las migraciones corren con `python -m app.tasks migrate`, que aplica las de Alembic y después los seeders, en una sola transacción: un seeder que falla deshace las migraciones, y `deploy.py` vuelve a la versión anterior.
- El job `server` del CI corre `alembic check` después de las migraciones: un modelo sin su migración falla.
- `env.py` le pasa a Alembic como `target_metadata` la `MetaData` de la `Base`, con todos los modelos importados ([Autogenerate, *Auto Generating Migrations*](../fuentes/alembic/autogenerate.rst)).
- Cada migración autogenerada se revisa y se corrige a mano antes de commitearla ([Autogenerate, *Auto Generating Migrations*](../fuentes/alembic/autogenerate.rst)).
- La `MetaData` de la `Base` lleva una `naming_convention`, y toda restricción tiene nombre ([Autogenerate, *What does Autogenerate Detect*](../fuentes/alembic/autogenerate.rst)).
- Un cambio de nombre de una tabla o de una columna se escribe a mano como un cambio de nombre: la autogeneración lo propone como borrar y crear ([Autogenerate, *What does Autogenerate Detect*](../fuentes/alembic/autogenerate.rst)).
- Un cambio en los valores de un `StrEnum` se escribe a mano en la migración, en su `CHECK`: la autogeneración no lo ve ([Autogenerate, *What does Autogenerate Detect*](../fuentes/alembic/autogenerate.rst)).

## Seeders

- `seeders/` lleva los datos que tiene que haber en todo entorno, producción incluida: catálogos, roles, listas. `mock_data/` lleva los datos de ejemplo, solo para una máquina en desarrollo.
- Cada módulo trae funciones `async def seed_<nombre>(session: AsyncSession) -> None`. Corren en el orden de los nombres del módulo y de la función.
- Un seeder es idempotente: escribe lo que falta y nunca duplica una fila, porque corre en cada despliegue, después de las migraciones.
- Los datos no van en una migración: juntar el historial en una inicial los borraría.
- `mock_data/` corre con `python -m app.tasks mock`, que `database.py seed --mock` lanza solo en una máquina en desarrollo ([despliegue.md](despliegue.md#postgresql)).

## Valkey

- El servidor habla con Valkey con el cliente asíncrono de valkey-py, uno para toda la app, en `store.py`. Su URL es `valkey_url`: en el servidor, el socket de su instancia, que escribe `install.py` ([despliegue.md](despliegue.md#valkey)).

## Esquemas

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- `alias_generator=to_camel` y `serialize_by_alias=True` en el esquema base.
- `validate_by_name=True` en el esquema base: el código y las filas usan los nombres de Python, en snake_case. Sin él, `from_attributes` busca en una fila el alias, `createdAt`, y no encuentra `created_at`.
- `extra="forbid"` y `validate_by_name=False` en los esquemas de entrada: el cliente escribe solo en camelCase, y un campo en snake_case responde 422 en vez de aceptarse con dos nombres.
- Los parámetros de query se declaran en un esquema de entrada. Un parámetro desconocido responde 422 en vez de ignorarse.

## Inyección de dependencias

- Las dependencias y los parámetros de una ruta se declaran con `Annotated`.
- La dependencia de la `AsyncSession` lleva `scope="function"`. El commit corre antes de enviar la respuesta: si falla, el cliente recibe el error y no un 200.

## Routers

- Los routers se incluyen en un `APIRouter(prefix="/api")` de `main.py`.
- Un `DELETE` borra la fila de verdad. Una columna `deleted_at` se escribe con un `PATCH`, como cualquier otro campo, y nunca reemplaza al borrado: un `DELETE` que solo marca la fila obliga a filtrar cada consulta y cada índice único.

## Ciclo de vida

- El arranque y el cierre van en el `lifespan` de la app: `on_event` está obsoleto. [FastAPI 0.162.0](https://raw.githubusercontent.com/fastapi/fastapi/0.162.0/fastapi/applications.py)

## Tareas en segundo plano

- El trabajo que sigue a la respuesta va en `BackgroundTasks`.

## Tareas periódicas

- Una tarea periódica es una función en `services/`.
- La tarea trabaja sobre lo que encuentra en la base, no sobre lo que pasó desde la vuelta anterior: una vuelta perdida la recupera la siguiente.
- La dispara un timer de systemd con `python -m app.tasks <tarea>`: systemd no arranca una vuelta si la anterior sigue corriendo.

## Archivos

Estándares: de OWASP, el [*File Upload Cheat Sheet*](../fuentes/owasp/File_Upload.md) y el [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md).

Contrato: [transversal.md](transversal.md#archivos).

- El servidor recibe un archivo como `UploadFile`.
- Cada archivo es una fila de una tabla hija de su recurso, `<recurso>_file`.
- La fila de un archivo guarda su tipo, su tamaño y su nombre original.
- Un barrido borra los archivos con más de una hora en disco y sin fila en ninguna tabla `_file`. El margen deja terminar la subida que todavía no confirmó su fila.
- Antes de volver a codificar una imagen se aplica su orientación EXIF: sin eso queda girada.
- Toda imagen se vuelve a codificar con Pillow antes de guardarse, sin sus metadatos ([File Upload, *File Content Validation*](../fuentes/owasp/File_Upload.md)).
- Cada recurso acepta solo los tipos de archivo que necesita, de una lista, y ninguno acepta ZIP ([File Upload, *List Allowed Extensions*](../fuentes/owasp/File_Upload.md) y [*File Content Validation*](../fuentes/owasp/File_Upload.md)).
- El servidor comprueba el tipo de un archivo por su contenido: el `Content-Type` y la extensión que manda el cliente no lo deciden ([File Upload, *Content-Type Validation*](../fuentes/owasp/File_Upload.md) y [*File Signature Validation*](../fuentes/owasp/File_Upload.md)).
- Pillow decodifica una imagen solo en los formatos de la lista del recurso y con su límite de píxeles, `Image.MAX_IMAGE_PIXELS` ([File Upload, *File Content Validation*](../fuentes/owasp/File_Upload.md) y [*Upload and Download Limits*](../fuentes/owasp/File_Upload.md)).
- El archivo en disco se llama con el ID de su fila ([File Upload, *Filename Safety*](../fuentes/owasp/File_Upload.md)).
- El nombre original tiene a lo sumo 255 caracteres y nunca forma una ruta en disco ([File Upload, *Filename Safety*](../fuentes/owasp/File_Upload.md)).
- Subir un archivo exige una sesión y el permiso de su recurso, y bajarlo, el permiso de su recurso ([File Upload, *User Permissions*](../fuentes/owasp/File_Upload.md)).
- Un usuario descarga a lo sumo 300 archivos por minuto: una pantalla llena de imágenes pide unas 50 ([File Upload, *Upload and Download Limits*](../fuentes/owasp/File_Upload.md)).
- Un archivo se responde con `Content-Disposition: attachment`, y con `application/octet-stream` si su tipo es desconocido o binario ([HTTP Security Response Headers Cheat Sheet, *Secure File Download Headers*](../fuentes/owasp/HTTP_Headers.md)).

## Autenticación

Rige [autenticacion.md](autenticacion.md).

## Correo y SMS

Estándar: [Standard Webhooks](../fuentes/standard-webhooks/standard-webhooks.md).

- El correo sale por la API de correo de Equipaggio, `PUT /email/{id}`, y el SMS, por su pasarela, `PUT /sms/{id}`.
- Cada correo lleva una parte en texto y otra en HTML.
- Un correo rebotado llega por el webhook de Equipaggio. El servidor marca la dirección como inválida, y la app le dice al usuario que su correo no llega.
- El servidor verifica las firmas de `webhook-signature` sobre `webhook-id`, `webhook-timestamp` y el cuerpo tal como llegó, sin volver a serializarlo, y rechaza el webhook si ninguna vale ([Standard Webhooks, *Signature scheme*](../fuentes/standard-webhooks/standard-webhooks.md) y [*Webhook headers*](../fuentes/standard-webhooks/standard-webhooks.md)).
- Una firma simétrica se compara en tiempo constante ([Standard Webhooks, *Verifying signatures*](../fuentes/standard-webhooks/standard-webhooks.md)).
- La clave pública de una firma asimétrica sale de `Settings`, nunca de la petición ([Standard Webhooks, *Additional considerations*](../fuentes/standard-webhooks/standard-webhooks.md)).
- Un webhook con un `webhook-timestamp` a más de 5 minutos de la hora del servidor se rechaza ([Standard Webhooks, *Verifying signatures*](../fuentes/standard-webhooks/standard-webhooks.md)).
- `webhook-id` es la clave de idempotencia: un webhook ya procesado no se procesa otra vez ([Standard Webhooks, *Verifying signatures*](../fuentes/standard-webhooks/standard-webhooks.md)).

## Envíos al exterior

- Primero la evidencia en la base, después el envío best-effort. Un fallo de entrega no tumba la operación.

## Errores

Contrato: [transversal.md](transversal.md#errores).

- Un error con tipo propio se lanza con `AppError`; uno que su código de estado ya explica, con `HTTPException`, y sale como `about:blank`.

## Fechas

Contrato: [transversal.md](transversal.md#fechas).

- Los campos de fecha y hora de los esquemas son `Timestamp`, del esquema base: entra solo como cadena RFC 3339 y queda en UTC. `AwareDatetime` acepta también un número como epoch y una hora sin segundos, y conserva el desfase que recibe; un `datetime`, además, una hora sin zona.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- El servidor traduce con Babel.
- El `.mo` no se versiona: `release.yml` lo compila del `.po` con `pybabel compile -d src/app/locale` y viaja en el artefacto. Un `.mo` versionado puede quedar desfasado de su `.po`, y el código de una versión no cambia en el servidor.
- El servidor guarda el idioma de `Accept-Language` con el FID de cada instalación de la app, y en el usuario el último elegido, para el correo.

## Límite de tasa

Estándar: [RFC 6585](../fuentes/rfc/rfc6585.txt).

- Los contadores viven en Valkey, compartidos por todos los procesos.
- Todo 429 lleva `Retry-After`: el cliente sabe cuándo reintentar ([RFC 6585 §4](../fuentes/rfc/rfc6585.txt)).
- Una petición que pasa su límite responde 429 ([RFC 6585 §4](../fuentes/rfc/rfc6585.txt)).
- El `detail` de un 429 dice qué límite se pasó ([RFC 6585 §4](../fuentes/rfc/rfc6585.txt)).

## Llamadas de voz y video

Estándar: [RFC 8656](../fuentes/rfc/rfc8656.txt).

Contrato: [transversal.md](transversal.md#llamadas-de-voz-y-video).

- Una credencial de TURN dura 1 hora. coturn la revisa solo al abrir el relay, así que vencer no corta una llamada en curso.
- La llamada que suena vive en Valkey, con su oferta y un TTL de 60 segundos. Una llamada sin respuesta en ese plazo queda perdida.
- El usuario de una credencial de TURN es solo su vencimiento, sin la cuenta: coturn lo recibe sin cifrar ([RFC 8656 §21.1.6](../fuentes/rfc/rfc8656.txt)).

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

- Las respuestas de Nominatim se guardan en Valkey.

## Montos

Contrato: [transversal.md](transversal.md#montos).

- Un monto es `Decimal` en los esquemas y entra solo como cadena. Pydantic acepta también un número JSON, lo declara así en el OpenAPI de las peticiones y lo recorta si excede un `double`.
- Un monto se serializa sin exponente. Pydantic lo escribe con `str`, que puede dar `1E-7`.

## OpenAPI y clientes

Estándar: la [especificación OpenAPI 3.1](../fuentes/openapi/openapi-3.1.2.md).

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- Cada router lleva un solo tag.
- El OpenAPI se exporta a `server/openapi.json`, versionado, y una prueba falla si no coincide con la app. Un cambio de contrato se ve en el diff.
- En producción no se sirven el OpenAPI ni su documentación. El contrato está en el repositorio, y nadie de afuera necesita el mapa de la API.
- El `operationId` es el tag seguido del nombre de la función, en camelCase: el tag lo hace único en toda la API ([OpenAPI, *Operation Object*](../fuentes/openapi/openapi-3.1.2.md)).
- Cada operación declara sus errores como `application/problem+json` con el esquema del problema, y el 422 con el del problema `validation`: un cliente generado tipa el error que de verdad recibe ([OpenAPI, *Responses Object*](../fuentes/openapi/openapi-3.1.2.md)).
- Un `GET`, un `HEAD` o un `DELETE` no lleva cuerpo ([OpenAPI, *Operation Object*](../fuentes/openapi/openapi-3.1.2.md)).

## Paginación

Contrato: [transversal.md](transversal.md#paginación).

- La petición es `PageParams`, o `SkipParams` si acepta `skip`. La respuesta es `Page[T]`, o `CountedPage[T]` si devuelve `totalSize`.
- El token guarda la columna y el `id` del último elemento, y los filtros, cifrados con Fernet y la clave `PAGE_TOKEN_KEY`.

## Pagos

Estándar: el [*Secure Integration of Third-Party Payment Gateways Cheat Sheet*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md) de OWASP.

Contrato: [transversal.md](transversal.md#pagos).

- El servidor valida cada producto, precio y descuento del pedido y calcula el total con sus propios datos antes de crear la orden en la pasarela ([Payment Gateways, *1. Sending Order data*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- Solo una notificación de servidor a servidor confirma un pago: los parámetros de la redirección del usuario no ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- El servidor verifica la autenticidad de cada notificación de la pasarela, con su firma ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- Un pedido se cumple solo después de consultar el estado del pago en la API de la pasarela, y si el monto, la moneda y el id de la orden son los esperados ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- El ID de cada evento procesado se guarda con una restricción única: un evento se procesa una sola vez, aunque llegue repetido o dos entregas lleguen a la vez ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- Una notificación que llega tarde o fuera de orden se verifica y se concilia con el estado actual del pago, aunque el pago haya vencido ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- Cada inicio de pago, redirección y notificación va al registro de eventos con su hora y su IP, el id de la notificación, el resultado de su validación y la orden, sin cabeceras ni cuerpos crudos, credenciales ni datos de pago ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md) y [*Logging and Monitoring*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).

## Permisos

Estándares: el [*Authorization Cheat Sheet*](../fuentes/owasp/Authorization.md) de OWASP y [RFC 9110](../fuentes/rfc/rfc9110.txt).

- Cada ruta declara con una dependencia de FastAPI el permiso que exige. El permiso queda a la vista en la ruta.
- Una sola consulta, filtrada por el usuario, decide entre el 404 y el 403 de un recurso, y no confirma que exista uno ajeno.
- Un recurso que no pertenece al usuario responde 404, como si no existiera; uno que el usuario ve pero sobre el que no puede hacer esa acción responde 403 ([RFC 9110 §15.5.4](../fuentes/rfc/rfc9110.txt) y [§15.5.5](../fuentes/rfc/rfc9110.txt)).
- Un permiso combina el rol y la relación: el rol de la cuenta da las acciones que puede hacer, y su relación con el recurso, como ser su dueño o miembro de su organización, los recursos sobre los que las hace ([Authorization Cheat Sheet, *Prefer Attribute and Relationship Based Access Control over RBAC*](../fuentes/owasp/Authorization.md)).
- El servidor comprueba el permiso en cada petición, sobre el objeto concreto que pide: lo que oculta un cliente no cuenta como control ([Authorization Cheat Sheet, *Validate the Permissions on Every Request*](../fuentes/owasp/Authorization.md) y [*Verify that Authorization Checks are Performed in the Right Location*](../fuentes/owasp/Authorization.md)).
- Ninguna ruta queda abierta por omisión, ni por la configuración por defecto de una biblioteca: el acceso que da cada una está escrito en ella ([Authorization Cheat Sheet, *Deny by Default*](../fuentes/owasp/Authorization.md)).
- Una cuenta tiene solo los permisos que necesita ([Authorization Cheat Sheet, *Enforce Least Privileges*](../fuentes/owasp/Authorization.md)).
- Un permiso que falla lanza una excepción que responde el manejador de errores de la app, sin datos internos ([Authorization Cheat Sheet, *Exit Safely when Authorization Checks Fail*](../fuentes/owasp/Authorization.md)).
- Cada permiso tiene una prueba de que quien no lo tiene recibe 403 o 404 ([Authorization Cheat Sheet, *Enforce Least Privileges*](../fuentes/owasp/Authorization.md) y [*Create Unit and Integration Test Cases for Authorization Logic*](../fuentes/owasp/Authorization.md)).

## Push

Estándar: [RFC 8030](../fuentes/rfc/rfc8030.txt).

Contrato: [transversal.md](transversal.md#push).

- El servidor envía a FCM con `messaging.send_each_async` del Admin SDK, con el FID en `fid`.
- El servidor envía Web Push con `webpush_async` de pywebpush y una sola `aiohttp.ClientSession` para toda la app: sin ella, cada envío abre una sesión nueva.
- El endpoint de una suscripción web lo elige el cliente, y el servidor le hace un `POST`. Por eso la suscripción se rechaza con 422 si el host de su endpoint es una dirección IP, y la `ClientSession` de Web Push resuelve cada nombre con un resolver que descarta las direcciones que `ipaddress` no marca como globales y se conecta a la que resolvió: un endpoint no lleva al servidor a su propia red, a la máquina ni a los metadatos del proveedor. aiohttp no pasa por el resolver una dirección IP escrita en la URL. [aiohttp 3.14.5](https://raw.githubusercontent.com/aio-libs/aiohttp/v3.14.5/aiohttp/connector.py)
- Una suscripción web se rechaza con 422 si su endpoint no es una URL `https` ([RFC 8030 §8](../fuentes/rfc/rfc8030.txt)).
- Un Web Push de un aviso que no caduca lleva un TTL de 28 días, el de FCM por defecto: con el TTL 0 de pywebpush, se pierde si el navegador no está en línea ([RFC 8030 §5.2](../fuentes/rfc/rfc8030.txt)). [FCM](https://firebase.google.com/docs/reference/fcm/rest/v1/projects.messages), [pywebpush 2.5.0](https://raw.githubusercontent.com/web-push-libs/pywebpush/4a2b66dae1408a19eb2c3f724ef0792f5258e72b/pywebpush/__init__.py)
- Una suscripción web que responde 404 o 410 se borra: el 404 dice que venció, y el servicio de push de Firefox responde 410 a una suscripción que ya no vale ([RFC 8030 §7.3](../fuentes/rfc/rfc8030.txt)). [autopush](https://raw.githubusercontent.com/mozilla-services/autopush-rs/60841760e34878715780bdc57309a31d1d33fd95/docs/src/errors.md)

## Registro de eventos

Estándares: el [*Logging Cheat Sheet*](../fuentes/owasp/Logging.md) y el [*Application Logging Vocabulary Cheat Sheet*](../fuentes/owasp/Logging_Vocabulary.md) de OWASP.

- Los eventos van en una sola tabla, `event_log`, y un cambio de fila también es un evento, con los campos cambiados en `details`: lo que pasó alrededor de una hora se lee en una consulta.
- `actor_label` guarda el identificador tal como llegó: así queda el intento sobre una cuenta que no existe.
- Un valor de una fila entra en `details` solo si su tabla y su campo están en una lista blanca: una columna nueva no se registra sola. Un campo fuera de la lista se registra como cambiado, sin su valor.
- Un evento se escribe en su propia transacción, salvo el de un cambio de fila, que va en la del cambio: un fallo queda aunque la petición se deshaga, y un cambio deshecho no queda.
- El rol de la app se llama como la app, y solo tiene `INSERT` y `SELECT` sobre `event_log`: un error o una inyección en la app no cambian ni borran el rastro. El rol no es el dueño de la tabla.
- Los permisos de una tabla los da la migración que la crea: quedan versionados y el CI los prueba.
- `actor_id` es un `uuid` sin clave foránea, y `ip_address`, un `inet`: el rastro sobrevive a la cuenta, e `inet` rechaza una dirección malformada.
- La purga es una tarea periódica que borra lo que pasó la retención con la credencial del dueño del esquema, la de las migraciones: el servidor no la recibe.
- Un evento que no se puede escribir hace fallar la operación que lo registra: un rastro incompleto no pasa en silencio.
- La retención de `event_log` es una constante en días en `services/events.py`, y la plantilla guarda 365.
- `action` es el nombre del vocabulario sin sus parámetros, como `authn_login_fail`. Los parámetros van en sus columnas: así se consultan ([Logging Vocabulary, *The Vocabulary*](../fuentes/owasp/Logging_Vocabulary.md)).
- `level` es `info`, `warn` o `critical`, el nivel que el vocabulario da al evento ([Logging Vocabulary, *The Vocabulary*](../fuentes/owasp/Logging_Vocabulary.md)).
- `event_log` se retiene un plazo fijo, mayor que cero: la IP y el user agent son datos personales ([Logging Cheat Sheet, *Disposal of logs*](../fuentes/owasp/Logging.md)).
- Solo el rol de la app y el dueño leen `event_log`, y ningún rol es miembro de ellos. La migración de `event_log` se lo quita a `<app>_read`, que lee el resto de la base ([despliegue.md](despliegue.md#postgresql)), y cada CI revisa quién lo lee ([Logging Cheat Sheet, *Protection*](../fuentes/owasp/Logging.md)).
- La copia en solo lectura de `event_log` es el respaldo de [despliegue.md](despliegue.md#respaldos), en cada corrida ([Logging Cheat Sheet, *Protection*](../fuentes/owasp/Logging.md)).
- Detectar que una fila de `event_log` se cambió o se borró le toca a quien la copia fuera de la máquina por la ruta de [Salud](#salud): en la máquina, solo el dueño y `root` pueden cambiarla, y `root` también cambia lo que lo detectaría ([Logging Cheat Sheet, *Protection*](../fuentes/owasp/Logging.md)).
- Cada evento guarda cuándo, desde dónde, quién y qué: `occurred_at`, `ip_address`, `user_agent`, `actor_id`, `actor_label`, `action`, `level`, `target_type`, `target_id` y `details` en `jsonb` y, si el repositorio es multi-tenant, `tenant_id` ([Logging Cheat Sheet, *Event attributes*](../fuentes/owasp/Logging.md)).
- `trace_id` es el trace-id del span actual, el mismo del log y del `traceId` del error ([Logging Cheat Sheet, *Event attributes*](../fuentes/owasp/Logging.md)).
- Se registran los inicios de sesión, buenos y fallidos, como `authn_login_success`, `authn_login_successafterfail`, `authn_login_fail` y `authn_login_fail_max`; el bloqueo de un autenticador, como `authn_login_lock`; el cambio de contraseña, como `authn_password_change` o `authn_password_change_fail`, y cada token que se crea, se revoca, se vuelve a presentar o se borra, como `authn_token_created`, `authn_token_revoked`, `authn_token_reuse` y `authn_token_delete` ([Logging Vocabulary, *Authentication*](../fuentes/owasp/Logging_Vocabulary.md)).
- Se registran el acceso denegado, como `authz_fail`; el cambio de los permisos de una cuenta, como `authz_change`, y cada acción de un administrador, como `authz_admin` ([Logging Vocabulary, *Authorization*](../fuentes/owasp/Logging_Vocabulary.md)).
- Se registran la sesión que se crea, se renueva, vence, se cierra o se usa vencida, como `session_created`, `session_renewed`, `session_expired`, `session_logout` y `session_use_after_expire`, y la cuenta que pasa su máximo de sesiones, como `excess_sessions_exceeded` ([Logging Vocabulary, *Session Management*](../fuentes/owasp/Logging_Vocabulary.md) y [*Excessive Use*](../fuentes/owasp/Logging_Vocabulary.md)).
- Se registran el fallo de validación de la entrada, como `input_validation_fail`, el de un valor que no está en su lista, como `input_validation_discrete_fail`, y el campo que el servidor no espera, como `malicious_extraneous` ([Logging Vocabulary, *Input Validation*](../fuentes/owasp/Logging_Vocabulary.md) y [*Malicious Behavior*](../fuentes/owasp/Logging_Vocabulary.md)).
- Se registran el límite de tasa que se pasa, como `excess_rate_limit_exceeded`, y la petición sin un `Origin` válido, como `malicious_csrf` ([Logging Vocabulary, *Excessive Use*](../fuentes/owasp/Logging_Vocabulary.md) y [*Malicious Behavior*](../fuentes/owasp/Logging_Vocabulary.md)).
- Se registran cada archivo que se sube, se valida, se guarda o se borra, como `upload_complete`, `upload_validation`, `upload_stored` y `upload_delete` ([Logging Vocabulary, *File Upload*](../fuentes/owasp/Logging_Vocabulary.md)).
- Se registran la cuenta que se crea, se cambia, se archiva o se borra, como `user_created`, `user_updated`, `user_archived` y `user_deleted`, y el permiso de un objeto que cambia, como `privilege_permissions_changed` ([Logging Vocabulary, *User Management*](../fuentes/owasp/Logging_Vocabulary.md) y [*Privilege Changes*](../fuentes/owasp/Logging_Vocabulary.md)).
- Se registran el fallo de un cifrado o un descifrado, como `crypt_encrypt_fail` y `crypt_decrypt_fail`, y el paso que llega fuera de su orden, como `sequence_fail` ([Logging Vocabulary, *Encryption/Decryption*](../fuentes/owasp/Logging_Vocabulary.md) y [*Sequence Errors*](../fuentes/owasp/Logging_Vocabulary.md)).
- Se registran la creación, la lectura, el cambio y el borrado de un dato sensible, como `sensitive_create`, `sensitive_read`, `sensitive_update` y `sensitive_delete`, sin copiar el dato ([Logging Vocabulary, *Sensitive Data Changes*](../fuentes/owasp/Logging_Vocabulary.md)).
- Se registran el arranque y la parada del servidor, como `sys_startup` y `sys_shutdown` ([Logging Vocabulary, *System Events*](../fuentes/owasp/Logging_Vocabulary.md)).
- Un error de la app, como una excepción sin manejar o el fallo de un tercero, va al log con su traceback ([Logging Cheat Sheet, *Which events to log*](../fuentes/owasp/Logging.md)).
- Ningún usuario queda fuera del registro, tampoco un administrador ni quien vigila el servidor ([Logging Cheat Sheet, *Data to exclude*](../fuentes/owasp/Logging.md)).
- Ni el log ni `event_log` guardan código, un id de sesión, una contraseña, una cadena de conexión, una clave, datos de pago ni datos personales sensibles, además de los tokens de [autenticacion.md](autenticacion.md#sesión) ([Logging Cheat Sheet, *Data to exclude*](../fuentes/owasp/Logging.md)).
- Un valor que llega de afuera entra al log sin retornos de carro ni saltos de línea: una línea no se hace pasar por otra ([Logging Cheat Sheet, *Event collection*](../fuentes/owasp/Logging.md)).
- Un dato de un evento que llega de afuera se valida antes de registrarlo: un campo malformado se omite, y el evento se registra igual, con el fallo de validación ([Logging Cheat Sheet, *Event collection*](../fuentes/owasp/Logging.md)).

## Reintentos

Contrato: [transversal.md](transversal.md#reintentos).

## Salud

- `GET /api/health` responde 204, o 503 si la base o Valkey no contestan: un servidor con una dependencia caída no está vivo aunque el proceso responda.
- `GET /api/health/events` responde `lastCriticalAt`, la hora del último evento `critical` de `event_log`, y `lastBackupAt`, la fecha de `last-backup` de [despliegue.md](despliegue.md#respaldos), o `null` si no hay. Quien lo consulta decide cuándo avisar: el servidor no fija umbrales.
- La misma ruta responde `lastEventAt`, la hora del último evento de `event_log` de cualquier nivel, o `null`: si `event_log` deja de recibir eventos, `lastCriticalAt` sigue en `null`, como cuando no pasó nada grave.
- La misma ruta responde `diskFreeBytes` y `diskTotalBytes`, del disco de su `StateDirectory=`: con el disco lleno PostgreSQL deja de escribir, y `SELECT 1` sigue respondiendo. El libre es el que puede escribir un usuario sin privilegios, como PostgreSQL.
- La ruta exige el token de `health_token` en `Authorization: Bearer`, comparado en tiempo constante, y sin él responde 401.
- Un token equivocado deja un evento `authn_login_fail`, de nivel `warn`: un escaneo no mueve `lastCriticalAt`.
- El servidor lee `last-backup` en la carpeta padre de su `StateDirectory=`, sin otra configuración.
- `GET /api/health/event-log`, con el mismo token, responde las filas de `event_log` en un `Page` de [Paginación](#paginación), en orden de transacción: quien vigila las copia fuera de la máquina y nota si una se cambió o se borró.
- `event_log` tiene la columna `xid`, un `xid8` con `pg_current_xact_id()` por defecto, y la ruta solo responde las filas con un `xid` menor que `pg_snapshot_xmin(pg_current_snapshot())`: una transacción que confirma tarde deja filas con un `xid` menor que el de las ya leídas, y un cursor por `id` o por hora se las saltaría.

## Trazas

- La app configura un `TracerProvider` del SDK de OpenTelemetry: sin él, FastAPI no crea spans y no hay trace-id.
- La telemetría no sale del proceso: el `TracerProvider` no tiene exportador, y la app crea FastAPI con `telemetry={"auto_configure": False}`, porque `OTEL_EXPORTER_OTLP_ENDPOINT` le agregaría uno sin cambiar el código. Una traza no ve la base ni sigue a otro servicio, y su trace-id ya está en cada log y en cada error.
- El propagador global de OpenTelemetry ignora `traceparent`: cada petición y cada WebSocket empiezan una traza nueva. El cliente no elige el id con el que se buscan sus registros. Es un propagador propio: con `OTEL_PROPAGATORS=none`, FastAPI falla en cada petición.
- Cada vuelta de una tarea periódica empieza su propia traza.
- Cada línea de log lleva el trace-id del span actual.

## Versión mínima de cliente

Contrato: [transversal.md](transversal.md#versión-mínima-de-cliente).

- La configuración guarda la versión mínima de cada pieza.
- La comprobación es una dependencia del router de `/api`: corre antes que las dependencias de cada ruta y que la validación, y un cliente viejo recibe `client-outdated` antes que un 401 o un 422.

## WebSocket

Estándar: el [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

Contrato: [transversal.md](transversal.md#websocket) y [autenticacion.md](autenticacion.md#websocket).

- Cada proceso se suscribe a Valkey y reenvía a sus conexiones, con un canal por usuario.
- Un handshake con la cookie exige un `Origin` igual al de la web, y uno con `Authorization` no lo revisa: una app nativa no manda `Origin`, y el secuestro entre sitios solo existe con la credencial que el navegador agrega por su cuenta.
- Una conexión sin mensajes no se cierra: la conexión existe para esperar eventos del servidor, y el ping de Uvicorn ya cierra la que se cayó.
- Los mensajes no llevan nonce: WSS ya impide que alguien fuera de la conexión repita un mensaje.
- Los contadores de los límites del WebSocket viven en Valkey, compartidos por todos los procesos.
- Un usuario tiene a lo sumo 10 conexiones abiertas, y la siguiente se rechaza en el handshake: alcanza para varias pestañas y dispositivos ([WebSocket Security, *Denial-of-Service Protection*](../fuentes/owasp/WebSocket_Security.md)).
- Un usuario manda a lo sumo 100 mensajes por minuto, y la conexión que se pasa se cierra con 1008 ([WebSocket Security, *Denial-of-Service Protection*](../fuentes/owasp/WebSocket_Security.md) y [*Input Validation*](../fuentes/owasp/WebSocket_Security.md)).
- Cada mensaje que pide una acción comprueba su permiso, como la ruta que haría lo mismo ([WebSocket Security, *Message-Level Authorization*](../fuentes/owasp/WebSocket_Security.md)).
- Cada mensaje que llega se valida con su esquema ([WebSocket Security, *Input Validation*](../fuentes/owasp/WebSocket_Security.md)).
- La lectura de cada mensaje atrapa su excepción: un mensaje malformado no tumba la app ([WebSocket Security, *Framework-Specific Best Practices*](../fuentes/owasp/WebSocket_Security.md)).
- Un envío a una conexión lenta no acumula mensajes en memoria sin límite ([WebSocket Security, *Denial-of-Service Protection*](../fuentes/owasp/WebSocket_Security.md)).
- El WebSocket no hace de túnel hacia otro servicio ([WebSocket Security, *Service Tunneling Risks*](../fuentes/owasp/WebSocket_Security.md)).

## Pruebas

- Las pruebas asíncronas corren con el plugin de pytest de AnyIO, con `anyio_mode = "auto"`, y `anyio_backend` es `asyncio`: asyncpg y la app solo corren en asyncio.
- Las pruebas corren contra PostgreSQL. Ven los mismos tipos y restricciones que producción.
- La base de prueba se arma con `python -m app.tasks migrate` antes de pytest: las pruebas ven el esquema de las migraciones, no el de los modelos, y los datos de los seeders.
- Las migraciones de prueba entran como el rol dueño del esquema, y cada conexión de las pruebas toma el rol del servidor con `SET ROLE`: una prueba tiene los permisos del servidor en producción, y una tabla sin su `GRANT` falla en el CI. Lo que corre el dueño, como la purga, se prueba con el fixture `owner`.
- Las pruebas corren contra Valkey, que se vacía en cada prueba: un conteo de intentos no pasa de una prueba a la siguiente.
- Cada prueba corre en una transacción que se deshace al terminar, y las sesiones de la app se unen a ella con `join_transaction_mode="create_savepoint"`: un commit de la app no sale de la prueba.
- Una prueba llama a la app con `AsyncClient` y `ASGITransport` de httpx, y a un WebSocket con `ASGIWebSocketTransport` de httpx-ws, nunca con `TestClient`: corren en el loop de la prueba y ven su transacción, y `TestClient` corre la app en otro loop.
- Una dependencia se reemplaza en una prueba con `app.dependency_overrides`.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Las versiones de «Proyecto» | [scripts/verificar.py](../scripts/verificar.py) |
| Todo campo de `Settings` es obligatorio | `test_settings_are_required` |
| Las dependencias y los parámetros con `Depends`, `Query`, `Path`, `Header`, `Cookie`, `Body`, `Form` o `File` se declaran con `Annotated` | ruff `FAST002` |
| El commit corre antes de enviar la respuesta | `test_failed_commit_is_a_server_error` |
| Los nombres en camelCase: todo esquema hereda del esquema base | `test_schemas_inherit_schema` |
| El esquema base lee por nombre, y el de entrada solo por alias | `test_schemas_read_rows_by_name` |
| `lazy="raise"` | `test_relationships_raise` |
| Una relación de uno a muchos deja el borrado al `ON DELETE` | `test_one_to_many_leaves_deletes_to_the_database` |
| `Timestamp` en los esquemas | `test_schema_datetimes_are_timestamps` |
| Un enum hereda de `StrEnum` | `test_enums_are_checked_text` y ruff `UP042` |
| Una columna o relación por línea | `test_mapped_attributes_fit_one_line`, y `ruff format` con `line-length = 320`, el máximo de ruff, en `models/ruff.toml` |
| `traceparent` no continúa la traza | `test_traceparent_starts_a_new_trace` |
| Las variables OTLP no agregan un exportador | `test_otlp_variables_export_nothing` |
| Un solo tag por router y el `operationId` en camelCase | `test_operation_ids` |
| Cada operación declara sus errores, y solo como problem+json | `test_errors_are_problems` |
| `server/openapi.json` coincide con la app | `test_openapi_file_is_current` |
| La versión mínima de cliente, en tres enteros | `test_outdated_client_is_rejected` |
| Un modelo sin su migración | `uv run alembic check` después de las migraciones, en el job `server` de CI |
| La base de prueba con las migraciones y los seeders | `uv run python -m app.tasks migrate` antes de pytest en el job `server` de CI |
| Las migraciones de prueba como el dueño, y las pruebas con los permisos del servidor | `python -m app.tasks migrate` con la credencial del dueño en el job `server` de CI, y `run_as_server` de `tests/conftest.py` |
| Que los seeders corren por módulo y por nombre, y solo las funciones `seed_` asíncronas del módulo | `test_seeders_run_by_module_and_name` |
| Que un seeder que falla deshace las migraciones, que cada despliegue corre los seeders sin duplicar filas, y que `mock_data/` corre solo en desarrollo | [scripts/infra/deploy.sh](../scripts/infra/deploy.sh) de Canone, como dice [despliegue.md](despliegue.md#cumplimiento) |
| Las pruebas nunca llaman a la app con `TestClient` | ruff `TID251` con `fastapi.testclient` y `starlette.testclient` en `banned-api` |
| Un `pageToken` ilegible o con otros parámetros responde 422 | `test_invalid_page_token_points_to_the_parameter` |
| El rol de la app no cambia ni borra `event_log`, y la purga respeta la retención | `test_server_cannot_change_events` y `test_purge_deletes_only_expired_events` |
| Solo el rol de la app y el dueño leen `event_log` | `test_only_the_server_and_owner_read_events` |
| `GET /api/health/events` y `GET /api/health/event-log` exigen el token | `test_events_need_the_token` |
| Un token equivocado deja `authn_login_fail` | `test_wrong_token_is_an_event` |
| `GET /api/health` responde 204, o 503 si Valkey no contesta | `test_health_answers_with_its_dependencies` y `test_health_needs_valkey` |
| `GET /api/health/events` dice el último evento de cualquier nivel | `test_events_tell_the_last_event` |
| `GET /api/health/events` dice el disco de su carpeta | `test_events_tell_the_disk` |
| `GET /api/health/event-log` no responde una fila mientras siga abierta una transacción anterior | `test_event_log_waits_for_an_open_transaction` |
| Un 422 deja su evento: `input_validation_fail`, `input_validation_discrete_fail` o `malicious_extraneous` | `test_validation_error_is_an_event` |
| El arranque y la parada dejan su evento | `test_lifespan_logs_start_and_stop` |
| Una dirección malformada se omite y se nombra en `details` | `test_malformed_address_is_left_out` |
| El log no tiene retornos de carro ni saltos de línea de un valor | `test_log_lines_have_no_line_breaks` |
| Pillow vuelve a codificar la imagen derecha y sin metadatos, solo en los formatos de la lista y bajo su límite de píxeles | `test_reencode_turns_the_image_and_drops_the_metadata`, `test_reencode_rejects_a_format_off_the_list` y `test_reencode_rejects_an_image_past_the_pixel_limit` |
| Un archivo se responde como `attachment`, y de tipo desconocido como `application/octet-stream` | `test_download_is_an_attachment` |
| Las convenciones de [postgres.md](postgres.md) | Las pruebas de `tests/test_conventions.py` que nombra esa página |
