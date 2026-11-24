# FastAPI

Un servidor en FastAPI. Se suma a [python.md](python.md).

## Proyecto

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
      <revisión>_accounts.py
      <revisión>_<cambio>.py
  src/app/
    __init__.py
    main.py
    methods.py
    openapi.py
    config.py
    database.py
    store.py
    dependencies.py
    errors.py
    ijson.py
    tracing.py
    enums.py
    tasks.py
    pages.py
    translations.py
    blocklist.txt
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
      account/
        __init__.py
        account.py
        account_session.py
        passkey.py
        password.py
        phone.py
        throttled.py
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
      account.py
      auth.py
      authorization.py
      health.py
      <recurso>.py
    routers/
      __init__.py
      account.py
      auth.py
      authorization.py
      health.py
      passkey.py
      password.py
      problems.py
      sms.py
      <recurso>.py
    services/
      __init__.py
      account.py
      attestation.py
      authenticators.py
      authorization.py
      clients.py
      codes.py
      events.py
      files.py
      health.py
      limits.py
      messages.py
      notices.py
      passkeys.py
      passwords.py
      registration.py
      sessions.py
      sms.py
      <recurso>.py
    locale/
      <idioma>/
        LC_MESSAGES/
          messages.po
  tests/
    __init__.py
    conftest.py
    authenticator.py
    test_account.py
    test_authorization.py
    test_conventions.py
    test_events.py
    test_files.py
    test_health.py
    test_messages.py
    test_methods.py
    test_passkeys.py
    test_passwords.py
    test_registration.py
    test_sessions.py
    test_sms.py
    test_tasks.py
    test_<recurso>.py
```

Plantilla: [plantilla/server/](../plantilla/server/) y el job `server` de [plantilla/.github/workflows/ci.yml](../plantilla/.github/workflows/ci.yml). Se copian sin editar `blocklist.txt`, `alembic.ini`, `alembic/README`, `alembic/env.py`, `alembic/script.py.mako`, cada `__init__.py`, `database.py`, `openapi.py`, `store.py`, `tracing.py`, `models/base.py`, `models/ruff.toml`, `routers/problems.py`, `schemas/base.py`, `schemas/page.py`, `services/files.py`, `tests/test_conventions.py`, `tests/test_events.py`, `tests/test_files.py` y `tests/test_tasks.py`. Los demás se copian y se completan.

## Estilo

- Cada columna y cada relación de un modelo se declaran en una sola línea, y el código de `models/` no tiene el límite de 99 caracteres de [python.md](python.md#estilo): el modelo se lee de arriba abajo, una declaración por renglón.

## Paquetes

- Cada modelo va en su propio archivo, dentro de la carpeta de su dominio.
- Un recurso lleva el mismo nombre de archivo en `routers/`, `services/` y `schemas/`.

## Configuración

- La configuración es una instancia de `Settings`, que hereda de `BaseSettings` de pydantic-settings.
- `Settings` lleva solo lo que cambia entre despliegues. Lo que no cambia es una constante del módulo que lo usa: se versiona y se prueba con el código.
- Todo campo de `Settings` es obligatorio y sin valor por defecto.
- `Settings(_secrets_dir=os.environ["CREDENTIALS_DIRECTORY"])` lee solo los archivos de esa carpeta, sin variables de entorno: cada valor sale de un solo lugar. Cada archivo se llama como su campo con el prefijo `app_`, el que pone systemd al cargar la carpeta ([despliegue.md](despliegue.md#configuración)), y `env_prefix="app_"` lo quita. Una carpeta que no existe solo da un aviso, y cada campo falla igual por faltar. [pydantic-settings 2.16.3](https://raw.githubusercontent.com/pydantic/pydantic-settings/v2.16.3/pydantic_settings/sources/providers/secrets.py)
- En desarrollo, `uv run --env-file .env` apunta `CREDENTIALS_DIRECTORY` a `credentials/`, que git ignora.

## Base de datos

Estándares: [*Session Basics*](../fuentes/sqlalchemy/session_basics.rst) y la [extensión asyncio](../fuentes/sqlalchemy/asyncio.rst) de SQLAlchemy.

- La sesión es una `AsyncSession` con asyncpg.
- Una relación bidireccional declara `back_populates` en los dos lados.
- Un enum hereda de `StrEnum`. La `Base` guarda solo esos como `text` con `CHECK`; un `str, Enum` se vuelve un enum nativo de Postgres que guarda el nombre y no el valor.
- Un array de un `StrEnum` lleva `create_constraint=False` en su `Enum`, y la tabla declara su `CHECK` con `<@`: SQLAlchemy no genera ese `CHECK`, y con `create_constraint=True` falla al compilar. [SQLAlchemy 2.1.9](https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_1_9/lib/sqlalchemy/dialects/postgresql/base.py)
- Una columna `created_at` es `CreatedAt`, y una `updated_at` es `UpdatedAt`, de la `Base`. Las dos toman `now()`; `updated_at` lo toma en cada `UPDATE` que emite SQLAlchemy.
- Una columna espacial se declara con `geo_point()` o `geo_line()`, que crean un `Geography` por columna y piden `spatial_index`: lleva el índice GiST si alguna consulta la busca por su geometría. GeoAlchemy2 copia el `nullable` entre la columna y su tipo, y un `Geography` compartido en un `Annotated` mezcla el de todas las columnas que lo usan. [GeoAlchemy2 0.21.0](https://raw.githubusercontent.com/geoalchemy/geoalchemy2/0.21.0/geoalchemy2/admin/__init__.py)
- `GeoPoint` y `GeoLine` son alias de `WKBElement`, solo para `Mapped[...]`.
- El engine lleva `pool_pre_ping=True`: una conexión del pool que PostgreSQL cerró al reiniciarse hace fallar la petición que la toma. [SQLAlchemy 2.1.9](https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_1_9/doc/build/core/pooling.rst)
- Una relación de uno a muchos deja el borrado al `ON DELETE` de la clave foránea del hijo. Si es `CASCADE`, lleva las cascadas `save-update`, `merge`, `delete` y `delete-orphan`, con `passive_deletes=True`; si es `RESTRICT`, lleva `passive_deletes="all"`. Sin eso, el ORM carga los hijos para ponerles `NULL`: un `CASCADE` falla por el `NOT NULL`, y un `RESTRICT` cambia en silencio una fila que no le pertenece al padre ([Session Basics, *Deleting*](../fuentes/sqlalchemy/session_basics.rst)).
- Toda relación lleva `lazy="raise"`: lo que se lee de ella se carga antes con una opción de carga, como `selectinload` ([asyncio, *Preventing Implicit IO when Using AsyncSession*](../fuentes/sqlalchemy/asyncio.rst)).
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
- Todo cambio de un modelo lleva su migración.
- Los permisos de una tabla los da la migración que la crea: quedan versionados y el CI los prueba.
- En un servidor que guarda geografía, `env.py` le pasa a Alembic los `alembic_helpers` de GeoAlchemy2. Sin ellos, la autogeneración crea el índice espacial dos veces y propone borrar `spatial_ref_sys`. [GeoAlchemy2 0.21.0](https://raw.githubusercontent.com/geoalchemy/geoalchemy2/0.21.0/doc/alembic.rst)
- `env.py` compara los `server_default`, con `compare_server_default=True` ([Autogenerate, *What does Autogenerate Detect*](../fuentes/alembic/autogenerate.rst)).
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
- `extra="forbid"` en el esquema base: el OpenAPI declara `additionalProperties: false` en cada esquema, también en los de respuesta, y con eso el cliente generado falla ante un campo que no conoce. Los esquemas del problem+json, `Problem`, `ValidationProblem` y `FieldError`, llevan `extra="ignore"`: el cliente ignora un miembro que no conoce ([transversal.md](transversal.md#errores)).
- `json_schema_serialization_defaults_required=True` en el esquema base, y `False` en `Problem` y `FieldError`: el OpenAPI de una respuesta declara requerido un campo con valor por defecto, y el de un problem+json, no.
- `validate_by_name=False` en los esquemas de entrada: el cliente escribe solo en camelCase, y un campo en snake_case responde 422 en vez de aceptarse con dos nombres.
- Los parámetros de query se declaran en un esquema de entrada. Un parámetro desconocido responde 422 en vez de ignorarse.

## Inyección de dependencias

- Las dependencias y los parámetros de una ruta se declaran con `Annotated`.
- La dependencia de la `AsyncSession` lleva `scope="function"`. El commit corre antes de enviar la respuesta: si falla, el cliente recibe el error y no un 200.

## Routers

- Los routers se incluyen en un `APIRouter(prefix="/api")` de `main.py`.
- Un `DELETE` borra la fila de verdad. Una columna `deleted_at` se escribe con un `PATCH`, como cualquier otro campo, y nunca reemplaza al borrado: un `DELETE` que solo marca la fila obliga a filtrar cada consulta y cada índice único.

## Tareas

- El trabajo que sigue a la respuesta va en `BackgroundTasks`.
- Una tarea periódica es una función en `services/`.
- La tarea trabaja sobre lo que encuentra en la base, no sobre lo que pasó desde la vuelta anterior: una vuelta perdida la recupera la siguiente.
- La dispara un timer de systemd con `python -m app.tasks <tarea>`: systemd no arranca una vuelta si la anterior sigue corriendo.
- La purga y el barrido corren cada día, en sus unidades de [despliegue.md](despliegue.md#procesos). Cualquier otra tarea declara su calendario en `TIMERS` de `tasks.py`, como `{"alert": "minutely"}`, el `OnCalendar=` que recibe `install.py --task`: el calendario queda en el código, junto a la tarea.
- Una tarea que maneja un navegador declara su calendario en `BROWSER_TIMERS` de `tasks.py`, con la forma de `TIMERS`, y no en `TIMERS`: corre en la unidad de [despliegue.md](despliegue.md#procesos) que deja correr a Chromium, con `install.py --browser`.
- Esa tarea maneja con Playwright el Chromium de Debian, `executable_path="/usr/bin/chromium-headless-shell"`, que instala `packages.py --browser`: se actualiza con la máquina, y el que baja Playwright solo cambia con su versión.

## Archivos

Estándares: de OWASP, el [*File Upload Cheat Sheet*](../fuentes/owasp/File_Upload.md) y el [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md).

Contrato: [transversal.md](transversal.md#archivos).

- El servidor recibe un archivo como `UploadFile`.
- Cada archivo es una fila de una tabla hija de su recurso, `<recurso>_file`.
- La fila de un archivo guarda su tipo, su tamaño y su nombre original.
- Un barrido borra los archivos, y las carpetas de tamaños, con más de una hora en disco y sin fila en ninguna tabla `_file`. El margen deja terminar la subida que todavía no confirmó su fila.
- Antes de volver a codificar una imagen se aplica su orientación EXIF: sin eso queda girada.
- Una imagen que se muestra en más de un tamaño, como una tarjeta en una lista y la misma imagen en grande, se guarda una vez por tamaño, en WebP, en la carpeta del ID de su fila: `<id>/<tamaño>.webp`, con el lado mayor de una constante del recurso y sin el original. Una pantalla con muchas tarjetas baja la pequeña de cada una, no la original. `files.sizes` las codifica de una sola decodificación, y `files.store_sizes` las escribe.
- Una subida que pasa el tamaño máximo de su recurso responde 413: `files.read` la lee hasta ese tamaño.
- El nombre original tiene a lo sumo 255 caracteres y nunca forma una ruta en disco ([File Upload, *Filename Safety*](../fuentes/owasp/File_Upload.md)).
- Un usuario descarga a lo sumo 300 archivos por minuto: una pantalla llena de imágenes pide unas 50 ([File Upload, *Upload and Download Limits*](../fuentes/owasp/File_Upload.md)).
- Toda imagen se vuelve a codificar con Pillow antes de guardarse, sin sus metadatos ([File Upload, *File Content Validation*](../fuentes/owasp/File_Upload.md)).
- Cada recurso acepta solo los tipos de archivo que necesita, de una lista, y ninguno acepta ZIP ([File Upload, *List Allowed Extensions*](../fuentes/owasp/File_Upload.md) y [*File Content Validation*](../fuentes/owasp/File_Upload.md)).
- El servidor comprueba el tipo de un archivo por su contenido: el `Content-Type` y la extensión que manda el cliente no lo deciden ([File Upload, *Content-Type Validation*](../fuentes/owasp/File_Upload.md) y [*File Signature Validation*](../fuentes/owasp/File_Upload.md)).
- Pillow decodifica una imagen solo en los formatos de la lista del recurso y con su límite de píxeles, `Image.MAX_IMAGE_PIXELS` ([File Upload, *File Content Validation*](../fuentes/owasp/File_Upload.md) y [*Upload and Download Limits*](../fuentes/owasp/File_Upload.md)).
- Cada recurso fija en una constante el tamaño máximo de un archivo ([File Upload, *Upload and Download Limits*](../fuentes/owasp/File_Upload.md)).
- La tabla `<recurso>_file` tiene clave `uuid`, y el archivo en disco se llama con el `uuid` de su fila ([File Upload, *Filename Safety*](../fuentes/owasp/File_Upload.md)).
- Subir un archivo exige una sesión y el permiso de su recurso, y bajarlo, el permiso de su recurso ([File Upload, *User Permissions*](../fuentes/owasp/File_Upload.md)).
- Un archivo se responde con `Content-Disposition: attachment`, y con `application/octet-stream` si su tipo es desconocido o binario ([HTTP Security Response Headers Cheat Sheet, *Secure File Download Headers*](../fuentes/owasp/HTTP_Headers.md)).

## Correo y SMS

Estándar: el [*Webhook Security Cheat Sheet*](../fuentes/owasp/Webhook_Security.md) de OWASP.

- El correo sale por la API de correo de Equipaggio, `PUT /email/{id}`, y el SMS, por su pasarela, `PUT /sms/{id}`.
- La URL de la API de Equipaggio es la constante `API` de `services/messages.py`, la misma en todo despliegue, y la clave del cliente, `equipaggio_key` de `Settings`.
- Cada correo lleva una parte en texto y otra en HTML.
- Un correo rebotado llega por el webhook de Equipaggio. El servidor marca la dirección como inválida, y la app le dice al usuario que su correo no llega.
- La clave pública de una firma asimétrica sale de `Settings`, nunca de la petición.
- Un webhook con un `webhook-timestamp` a más de 5 minutos de la hora del servidor se rechaza ([Webhook Security, *Replay Attack Protection*](../fuentes/owasp/Webhook_Security.md)).
- El servidor verifica las firmas de `webhook-signature` con el esquema de [Standard Webhooks 1.0.2](https://github.com/standard-webhooks/standard-webhooks/blob/v1.0.2/spec/standard-webhooks.md#signature-scheme), el del webhook de Equipaggio: sobre `webhook-id`, `webhook-timestamp` y el cuerpo tal como llegó, sin volver a serializarlo ([Webhook Security, *Signature Verification*](../fuentes/owasp/Webhook_Security.md)).
- El servidor acepta el webhook si una de sus firmas vale, y solo de los esquemas que espera; si ninguna vale, responde 401 sin decir por qué ([Webhook Security, *Signature Verification*](../fuentes/owasp/Webhook_Security.md)).
- Una firma simétrica se compara en tiempo constante ([Webhook Security, *Signature Verification*](../fuentes/owasp/Webhook_Security.md)).
- El servidor guarda el `webhook-id` de cada webhook procesado, y a uno repetido le responde 200 sin repetir su efecto ([Webhook Security, *Idempotency and Duplicate Events*](../fuentes/owasp/Webhook_Security.md)).

## Envíos al exterior

- Primero la evidencia en la base, después el envío best-effort. Un fallo de entrega no tumba la operación.
- Un correo o un SMS de una petición se encola con `messages.later` en su sesión, y `get_session` lo envía después del commit, también el de un `KeptError`: una petición que se deshace no envía nada, y un envío que falla va al log con su traceback.
- El servidor llama a otro servicio, como Nominatim o la API de correo, con un solo `httpx.AsyncClient` para toda la app, salvo FCM y Web Push, que van por sus bibliotecas.

## Errores

Contrato: [transversal.md](transversal.md#errores).

- Un error con tipo propio se lanza con `AppError`; uno que su código de estado ya explica, con `HTTPException`, y sale como `about:blank`.
- Un error que tiene que dejar escrito un cambio, como el fallo de una contraseña o el borrado de una sesión por reúso, se lanza envuelto en `KeptError`: la dependencia de la sesión hace commit y después deja salir el error que envuelve. Es la excepción al rollback de [Base de datos](#base-de-datos).

## Fechas

Contrato: [transversal.md](transversal.md#fechas).

- Los campos de fecha y hora de los esquemas son `Timestamp`, del esquema base: entra solo como cadena RFC 3339 y queda en UTC. `AwareDatetime` acepta también un número como epoch y una hora sin segundos, y conserva el desfase que recibe; un `datetime`, además, una hora sin zona.
- Los campos de fecha sin hora de los esquemas son `Day`, del esquema base: entra solo como cadena `AAAA-MM-DD`. `date` acepta también un número como epoch y una fecha con hora en cero.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- El servidor traduce con Babel.
- Las pruebas leen los catálogos compilados: el job `server` de CI los compila con `pybabel compile` antes de pytest.
- El `.mo` no se versiona: `release.yml` lo compila del `.po` con `pybabel compile -d src/app/locale` y viaja en el artefacto.
- El servidor guarda el idioma de `Accept-Language` con el FID de cada instalación de la app, y en el usuario el último elegido, para el correo.

## Límite de tasa

Estándar: [RFC 6585](../fuentes/rfc/rfc6585.txt).

- Los contadores viven en Valkey, compartidos por todos los procesos.
- Cada límite es una ventana deslizante, en `services/limits.py`: un sorted set por clave guarda la hora de cada intento, y un script de Lua cuenta el intento en todos los límites de la petición solo si ninguno está lleno.
- Todo 429 lleva `Retry-After`: el cliente sabe cuándo reintentar ([RFC 6585 §4](../fuentes/rfc/rfc6585.txt)).
- Una petición que pasa su límite responde 429 ([RFC 6585 §4](../fuentes/rfc/rfc6585.txt)).
- El `detail` de un 429 dice qué límite se pasó ([RFC 6585 §4](../fuentes/rfc/rfc6585.txt)).

## Llamadas de voz y video

Estándar: [RFC 8656](../fuentes/rfc/rfc8656.txt).

Contrato: [transversal.md](transversal.md#llamadas-de-voz-y-video).

- Una credencial de TURN dura 1 hora. coturn la revisa solo al abrir el relay, así que vencer no corta una llamada en curso. [coturn 4.6.1](https://raw.githubusercontent.com/coturn/coturn/4.6.1/src/server/ns_turn_server.c)
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
- En producción no se sirven el OpenAPI ni su documentación.
- El `operationId` es el tag seguido del nombre de la función, en camelCase: el tag lo hace único en toda la API ([OpenAPI, *Operation Object*](../fuentes/openapi/openapi-3.1.2.md)).
- Cada operación declara sus errores como `application/problem+json` con el esquema del problema, y el 422 con el del problema `validation` ([OpenAPI, *Responses Object*](../fuentes/openapi/openapi-3.1.2.md)).
- Un `GET`, un `HEAD` o un `DELETE` no lleva cuerpo ([OpenAPI, *Operation Object*](../fuentes/openapi/openapi-3.1.2.md)).

## Paginación

Contrato: [transversal.md](transversal.md#paginación).

- La petición es `PageParams`, o `SkipParams` si acepta `skip`. La respuesta es `Page[T]`, o `CountedPage[T]` si devuelve `totalSize`.
- El token guarda la columna y el `id` del último elemento, y los filtros, cifrados con Fernet y la clave `page_token_key` de `Settings`.

## Pagos

Estándar: el [*Secure Integration of Third-Party Payment Gateways Cheat Sheet*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md) de OWASP.

Contrato: [transversal.md](transversal.md#pagos).

- Con Stripe, el servidor llama a su API con los métodos `_async` de `stripe`, que van por httpx, y verifica cada notificación con `construct_event`: los métodos sin el sufijo bloquean el bucle de eventos. [stripe 17.0.0](https://raw.githubusercontent.com/stripe/stripe-python/v17.0.0/README.md)
- El servidor valida cada producto, precio y descuento del pedido y calcula el total con sus propios datos antes de crear la orden en la pasarela ([Payment Gateways, *1. Sending Order data*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- Solo una notificación de servidor a servidor confirma un pago: los parámetros de la redirección del usuario no ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- El servidor verifica la autenticidad de cada notificación de la pasarela, con su firma ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- Un pedido se cumple solo después de consultar el estado del pago en la API de la pasarela, y si el monto, la moneda y el id de la orden son los esperados ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- El ID de cada evento procesado se guarda con una restricción única: un evento se procesa una sola vez, aunque llegue repetido o dos entregas lleguen a la vez ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- Una notificación que llega tarde o fuera de orden se verifica y se concilia con el estado actual del pago, aunque el pago haya vencido ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).
- Cada inicio de pago, redirección y notificación va al registro de eventos con su hora y su IP, el id de la notificación, el resultado de su validación y la orden, sin cabeceras ni cuerpos crudos, credenciales ni datos de pago ([Payment Gateways, *2. Redirect to webhook*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md) y [*Logging and Monitoring*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)).

## Permisos

Estándares: el [*Authorization Cheat Sheet*](../fuentes/owasp/Authorization.md) de OWASP y [RFC 9110](../fuentes/rfc/rfc9110.txt).

- Cada ruta declara quién la llama con una dependencia: `public`, o la de su permiso, marcada con `@access` de `dependencies.py`.
- Una sola consulta, filtrada por el usuario, decide entre el 404 y el 403 de un recurso, y no confirma que exista uno ajeno.
- Un recurso que no pertenece al usuario responde 404, como si no existiera; uno que el usuario ve pero sobre el que no puede hacer esa acción responde 403 ([RFC 9110 §15.5.4](../fuentes/rfc/rfc9110.txt) y [§15.5.5](../fuentes/rfc/rfc9110.txt)).
- Un permiso combina el rol y la relación: el rol de la cuenta da las acciones que puede hacer, y su relación con el recurso, como ser su dueño o miembro de su organización, los recursos sobre los que las hace ([Authorization Cheat Sheet, *Prefer Attribute and Relationship Based Access Control over RBAC*](../fuentes/owasp/Authorization.md)).
- El servidor comprueba el permiso en cada petición, sobre el objeto concreto que pide, con una configuración global: el router de `/api` lleva `deny_by_default`, que responde 404 a una ruta que no declara quién la llama. Lo que oculta un cliente no cuenta como control ([Authorization Cheat Sheet, *Validate the Permissions on Every Request*](../fuentes/owasp/Authorization.md) y [*Verify that Authorization Checks are Performed in the Right Location*](../fuentes/owasp/Authorization.md)).
- Ninguna ruta queda abierta por omisión, ni por la configuración por defecto de una biblioteca: el acceso que da cada una está escrito en ella ([Authorization Cheat Sheet, *Deny by Default*](../fuentes/owasp/Authorization.md)).
- Una cuenta tiene solo los permisos que necesita ([Authorization Cheat Sheet, *Enforce Least Privileges*](../fuentes/owasp/Authorization.md)).
- Un permiso que falla lanza una excepción que responde el manejador de errores de la app, sin datos internos ([Authorization Cheat Sheet, *Exit Safely when Authorization Checks Fail*](../fuentes/owasp/Authorization.md)).
- Cada permiso tiene una prueba de que quien no lo tiene recibe 403 o 404 ([Authorization Cheat Sheet, *Enforce Least Privileges*](../fuentes/owasp/Authorization.md) y [*Create Unit and Integration Test Cases for Authorization Logic*](../fuentes/owasp/Authorization.md)).

## Push

Estándar: [RFC 8030](../fuentes/rfc/rfc8030.txt).

Contrato: [transversal.md](transversal.md#push).

- El servidor envía a FCM con `messaging.send_each_async` del Admin SDK, con el FID en `fid`.
- Un FID al que FCM responde `UNREGISTERED` se borra: FCM ya no le entrega nada. [FCM](https://firebase.google.com/docs/cloud-messaging/manage-tokens)
- El servidor envía Web Push con `webpush_async` de pywebpush y una sola `aiohttp.ClientSession` para toda la app: sin ella, cada envío abre una sesión nueva.
- El endpoint de una suscripción web lo elige el cliente, y el servidor le hace un `POST`. Por eso la suscripción se rechaza con 422 si el host de su endpoint es una dirección IP, y la `ClientSession` de Web Push resuelve cada nombre con un resolver que descarta las direcciones que `ipaddress` no marca como globales y se conecta a la que resolvió: un endpoint no lleva al servidor a su propia red, a la máquina ni a los metadatos del proveedor. aiohttp no pasa por el resolver una dirección IP escrita en la URL. [aiohttp 3.14.5](https://raw.githubusercontent.com/aio-libs/aiohttp/v3.14.5/aiohttp/connector.py)
- Cada Web Push lleva su TTL: pywebpush manda 0 si no se le da otro, y un aviso con TTL 0 se pierde si el navegador no está en línea. [pywebpush 2.5.0](https://raw.githubusercontent.com/web-push-libs/pywebpush/4a2b66dae1408a19eb2c3f724ef0792f5258e72b/pywebpush/__init__.py)
- Una suscripción web que responde 410 se borra: el servicio de push de Firefox responde 410 a una suscripción que ya no vale. [autopush](https://raw.githubusercontent.com/mozilla-services/autopush-rs/60841760e34878715780bdc57309a31d1d33fd95/docs/src/errors.md)
- El TTL de un aviso que no caduca es de 28 días ([RFC 8030 §5.2](../fuentes/rfc/rfc8030.txt)).
- Una suscripción web se rechaza con 422 si su endpoint no es una URL `https` ([RFC 8030 §8](../fuentes/rfc/rfc8030.txt)).
- Una suscripción web que responde 404 se borra: venció ([RFC 8030 §7.3](../fuentes/rfc/rfc8030.txt)).

## Registro de eventos

Estándares: el [*Logging Cheat Sheet*](../fuentes/owasp/Logging.md) y el [*Application Logging Vocabulary Cheat Sheet*](../fuentes/owasp/Logging_Vocabulary.md) de OWASP.

- Los eventos van en una sola tabla, `event_log`, y un cambio de fila también es un evento, con los campos cambiados en `details`: lo que pasó alrededor de una hora se lee en una consulta.
- `actor_label` guarda el identificador tal como llegó: así queda el intento sobre una cuenta que no existe.
- Un valor de una fila entra en `details` solo si su tabla y su campo están en una lista blanca: una columna nueva no se registra sola. Un campo fuera de la lista se registra como cambiado, sin su valor.
- Un evento se escribe en su propia transacción, salvo el de un cambio de fila, que va en la del cambio: un fallo queda aunque la petición se deshaga, y un cambio deshecho no queda.
- El rol de la app se llama como la app, y solo tiene `INSERT` y `SELECT` sobre `event_log`: un error o una inyección en la app no cambian ni borran el rastro. El rol no es el dueño de la tabla.
- `actor_id` es un `uuid` sin clave foránea, y `ip_address`, un `inet`: el rastro sobrevive a la cuenta, e `inet` rechaza una dirección malformada.
- La purga es una tarea periódica que borra lo que pasó la retención con la credencial del dueño del esquema, la de las migraciones: el servidor no la recibe.
- Un evento que no se puede escribir hace fallar la operación que lo registra: un rastro incompleto no pasa en silencio.
- La retención de `event_log` es una constante en días en `services/events.py`, y la plantilla guarda 365.
- `action` es el nombre del vocabulario sin sus parámetros, como `authn_login_fail`. Los parámetros van en sus columnas: así se consultan ([Logging Vocabulary, *The Vocabulary*](../fuentes/owasp/Logging_Vocabulary.md)).
- `level` es `info`, `warn` o `critical`, el nivel que el vocabulario da al evento ([Logging Vocabulary, *The Vocabulary*](../fuentes/owasp/Logging_Vocabulary.md)).
- `event_log` se retiene un plazo fijo, mayor que cero: la IP y el user agent son datos personales ([Logging Cheat Sheet, *Disposal of logs*](../fuentes/owasp/Logging.md)).
- Solo el rol de la app y el dueño leen `event_log`, y ningún rol es miembro de ellos. La migración de `event_log` se lo quita a `<app>_read`, que lee el resto de la base ([despliegue.md](despliegue.md#postgresql)) ([Logging Cheat Sheet, *Protection*](../fuentes/owasp/Logging.md)).
- La copia en solo lectura de `event_log` es el respaldo de [despliegue.md](despliegue.md#respaldos), en cada corrida ([Logging Cheat Sheet, *Protection*](../fuentes/owasp/Logging.md)).
- Detectar que una fila de `event_log` se cambió o se borró le toca a quien la copia fuera de la máquina por la ruta de [Salud](#salud): en la máquina, solo el dueño y `root` pueden cambiarla, y `root` también cambia lo que lo detectaría ([Logging Cheat Sheet, *Protection*](../fuentes/owasp/Logging.md)).
- Cada evento guarda cuándo, desde dónde, quién y qué: `occurred_at`, `ip_address`, `user_agent`, `actor_id`, `actor_label`, `action`, `level`, `target_type`, `target_id` y `details` en `jsonb` y, si el repositorio es multi-tenant, `tenant_id` ([Logging Cheat Sheet, *Event attributes*](../fuentes/owasp/Logging.md)).
- `trace_id` es el trace-id del span actual, el mismo del log y del `traceId` del error ([Logging Cheat Sheet, *Event attributes*](../fuentes/owasp/Logging.md)).
- Se registran los inicios de sesión, buenos y fallidos, como `authn_login_success`, `authn_login_successafterfail`, `authn_login_fail` y `authn_login_fail_max`; el bloqueo de un autenticador, como `authn_login_lock`; el cambio de contraseña, como `authn_password_change` o `authn_password_change_fail`, cada token para acceder a un servicio que se crea, se revoca o se borra, como `authn_token_created`, `authn_token_revoked` y `authn_token_delete`, y el token revocado que se vuelve a presentar, como `authn_token_reuse`, también el secreto de refresco que ya rotó. Los tokens de una sesión registran los eventos de la sesión ([Logging Vocabulary, *Authentication*](../fuentes/owasp/Logging_Vocabulary.md)).
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

## Salud

- `GET /api/health` responde 204, o 503 si la base o Valkey no contestan.
- `GET /api/health/events` responde `lastCriticalAt`, la hora del último evento `critical` de `event_log`, y `lastBackupAt`, la fecha de `last-backup` de [despliegue.md](despliegue.md#respaldos), o `null` si no hay. Quien lo consulta decide cuándo avisar: el servidor no fija umbrales.
- La misma ruta responde `lastEventAt`, la hora del último evento de `event_log` de cualquier nivel, o `null`.
- La misma ruta responde `diskFreeBytes` y `diskTotalBytes`, del disco de su `StateDirectory=`. El libre es el que puede escribir un usuario sin privilegios, como PostgreSQL.
- La ruta exige el token de `health_token` en `Authorization: Bearer`, comparado en tiempo constante, y sin él responde 401.
- Un token equivocado deja un evento `authn_login_fail`, de nivel `warn`.
- El servidor lee `last-backup` en la carpeta padre de su `StateDirectory=`, sin otra configuración.
- `GET /api/health/event-log`, con el mismo token, responde las filas de `event_log` en un `Page` de [Paginación](#paginación), en orden de transacción.
- `event_log` tiene la columna `xid`, un `xid8` con `pg_current_xact_id()` por defecto, y la ruta solo responde las filas con un `xid` menor que `pg_snapshot_xmin(pg_current_snapshot())`.

## Trazas

- La app configura un `TracerProvider` del SDK de OpenTelemetry: sin él, FastAPI no crea spans y no hay trace-id.
- La telemetría no sale del proceso: el `TracerProvider` no tiene exportador, y la app crea FastAPI con `telemetry={"auto_configure": False}`. Una traza no ve la base ni sigue a otro servicio, y su trace-id ya está en cada log y en cada error. Sin ese parámetro, si el exportador OTLP llega instalado, como con `fastapi[standard]`, `FASTAPI_OTEL_AUTO_CONFIGURE=true` y `OTEL_EXPORTER_OTLP_ENDPOINT` le agregan uno sin cambiar el código. [FastAPI 0.165.0](https://raw.githubusercontent.com/fastapi/fastapi/0.165.0/fastapi/telemetry/_runtime.py)
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
- Una conexión sin mensajes no se cierra: la conexión existe para esperar eventos del servidor, y el ping de Uvicorn ya cierra la que se cayó.
- Los mensajes no llevan nonce: WSS ya impide que alguien fuera de la conexión repita un mensaje.
- Los contadores de los límites del WebSocket viven en Valkey, compartidos por todos los procesos.
- Un usuario tiene a lo sumo 10 conexiones abiertas, y la siguiente se rechaza en el handshake ([WebSocket Security, *Denial-of-Service Protection*](../fuentes/owasp/WebSocket_Security.md)).
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
| Los archivos que se copian sin editar coinciden con la plantilla | `verificar.py --repo` |
| Todo campo de `Settings` es obligatorio | `test_settings_are_required` |
| Las dependencias y los parámetros con `Depends`, `Query`, `Path`, `Header`, `Cookie`, `Body`, `Form` o `File` se declaran con `Annotated` | ruff `FAST002` |
| El commit corre antes de enviar la respuesta | `test_failed_commit_is_a_server_error` |
| Un `KeptError` hace commit de lo que escribió la petición y sale como el error que envuelve, y otro error lo deshace | `test_kept_error_commits_what_the_request_wrote` |
| Los nombres en camelCase: todo esquema de la app hereda del esquema base | `test_schemas_inherit_schema` |
| El esquema base lee por nombre, y el de entrada solo por alias | `test_schemas_read_rows_by_name` |
| `lazy="raise"` | `test_relationships_raise` |
| Una relación de uno a muchos deja el borrado al `ON DELETE` | `test_one_to_many_leaves_deletes_to_the_database` |
| `Timestamp` en los esquemas | `test_schema_datetimes_are_timestamps` |
| `Day` en los esquemas, y que solo lee `AAAA-MM-DD` | `test_schema_dates_are_days` y `test_day_takes_only_a_full_date` |
| Un enum hereda de `StrEnum` | `test_enums_are_strenums`, `test_enums_are_checked_text` y ruff `UP042` |
| Una columna o relación por línea, y `models/` sin el límite de 99 | `test_mapped_attributes_fit_one_line`, y `ruff format` con `line-length = 320`, el máximo de ruff, en `models/ruff.toml` |
| `traceparent` no continúa la traza | `test_traceparent_starts_a_new_trace` |
| La app no se configura la telemetría desde el entorno, y las variables OTLP no agregan un exportador | `test_otlp_variables_export_nothing` |
| Un solo tag por router y el `operationId` en camelCase | `test_operation_ids` |
| Cada operación declara sus errores solo como problem+json, con el esquema de su problema, y el 422 con el de `validation` | `test_errors_are_problems` |
| `Problem`, `ValidationProblem` y `FieldError` sin `additionalProperties: false` | `test_problems_let_extensions_through` |
| El OpenAPI de una respuesta declara requerido cada campo de su esquema | `test_response_fields_are_required` |
| Cada ruta de `routers/` declara quién la llama, y el router de `/api` responde 404 a la que no lo declara | `test_routes_declare_access` y `test_undeclared_route_is_not_found` |
| `server/openapi.json` coincide con la app | `test_openapi_file_is_current` |
| Un cambio de modelo que la autogeneración detecta, también de un `server_default`, sin su migración | `uv run alembic check` después de las migraciones, en el job `server` de CI |
| La base de prueba con las migraciones | `uv run python -m app.tasks migrate` antes de pytest en el job `server` de CI |
| Las migraciones de prueba como el dueño, y las pruebas con los permisos del servidor | `python -m app.tasks migrate` con la credencial del dueño en el job `server` de CI, y `run_as_server` de `tests/conftest.py` |
| Que los seeders corren por módulo y por nombre, y solo las funciones `seed_` asíncronas del módulo | `test_seeders_run_by_module_and_name` |
| Que un seeder que falla deshace las migraciones, que cada despliegue corre los seeders, y que `mock_data/` corre solo en desarrollo | [scripts/infra/deploy.sh](../scripts/infra/deploy.sh) de Canone, como dice [despliegue.md](despliegue.md#cumplimiento), sobre el `database.py` que se copia sin editar |
| Las pruebas nunca llaman a la app con `TestClient` | ruff `TID251` con `fastapi.testclient` y `starlette.testclient` en `banned-api` |
| El rol de la app no cambia ni borra `event_log`, y la purga respeta la retención | `test_server_cannot_change_events` y `test_purge_deletes_only_expired_events` |
| Solo el rol de la app y el dueño leen `event_log` | `test_only_the_server_and_owner_read_events` |
| `GET /api/health/events` y `GET /api/health/event-log` exigen el token | `test_events_need_the_token` |
| Un token equivocado deja `authn_login_fail`, de nivel `warn` | `test_wrong_token_is_an_event` |
| `GET /api/health` responde 204, o 503 si la base o Valkey no contestan | `test_health_answers_with_its_dependencies`, `test_health_needs_the_database` y `test_health_needs_valkey` |
| `GET /api/health/events` dice el último evento de cualquier nivel | `test_events_tell_the_last_event` |
| `GET /api/health/events` dice el disco de su carpeta | `test_events_tell_the_disk` |
| `GET /api/health/event-log` no responde una fila mientras siga abierta una transacción anterior | `test_event_log_waits_for_an_open_transaction` |
| Un 422 deja su evento: `input_validation_fail`, `input_validation_discrete_fail` o `malicious_extraneous` | `test_validation_error_is_an_event` |
| El arranque y la parada dejan su evento | `test_lifespan_logs_start_and_stop` |
| Una dirección malformada se omite y se nombra en `details` | `test_malformed_address_is_left_out` |
| El log de la app no tiene retornos de carro ni saltos de línea de un valor | `test_log_lines_have_no_line_breaks` |
| Pillow vuelve a codificar la imagen derecha y sin metadatos, solo en los formatos de la lista y bajo su límite de píxeles | `test_reencode_turns_the_image_and_drops_the_metadata`, `test_reencode_rejects_a_format_off_the_list` y `test_reencode_rejects_an_image_past_the_pixel_limit` |
| Cada tamaño de una imagen es un WebP derecho y sin metadatos, con su lado mayor, en la carpeta de su fila, y el barrido borra la carpeta sin fila | `test_sizes_keep_the_ratio_turn_the_image_and_drop_the_metadata`, `test_sizes_reject_a_format_off_the_list` y `test_sweep_deletes_only_old_files_without_row` |
| Una subida que pasa el tamaño máximo responde 413 | `test_read_rejects_a_file_past_the_limit` |
| Un archivo se responde como `attachment`, y de tipo desconocido como `application/octet-stream` | `test_download_is_an_attachment` |
| Un correo o un SMS sale después del commit, también el de un `KeptError`, y una petición que se deshace no envía nada | `test_messages_go_after_the_commit` |
| Un envío que falla va al log y no cambia la respuesta | `test_failed_delivery_does_not_fail_the_request` |
| Una petición que pasa su límite responde 429 con `Retry-After`, el `detail` del límite y el evento `excess_rate_limit_exceeded`, en una ventana deslizante | `test_email_gets_one_code_a_minute_and_five_an_hour` |
| La cuenta guarda el idioma de `Accept-Language` al entrar | `test_sign_in_keeps_the_language_of_the_account` |