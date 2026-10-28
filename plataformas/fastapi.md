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
  src/app/
    __init__.py
    main.py
    openapi.py
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
    locale/
      <idioma>/
        LC_MESSAGES/
          messages.po
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
`schemas/` y `services/`, `models/event/`, `services/events.py`, la migración de `event_log` y
`tests/conftest.py`.

<br>

---
---

<br>

## Configuración

- La configuración es una instancia de `Settings`, que hereda de `BaseSettings` de
  pydantic-settings.
- `Settings` lleva solo lo que cambia entre despliegues. Lo que no cambia es una constante del
  módulo que lo usa: se versiona y se prueba con el código
  ([ADR-0076](../adr/0076-lo-que-cambia-entre-despliegues-sale-de-un-solo-archivo-y-lo-demas-es-codigo.md)).
- Todo campo de `Settings` es obligatorio y sin valor por defecto.
- `Settings(_secrets_dir=os.environ["CREDENTIALS_DIRECTORY"])` lee solo los archivos de esa
  carpeta, sin variables de entorno: cada valor sale de un solo lugar. Cada archivo se llama como
  su campo con el prefijo `app_`, el que pone systemd al cargar la carpeta
  ([despliegue.md](despliegue.md#configuración)), y `env_prefix="app_"` lo quita. Una carpeta que
  no existe solo da un aviso, y cada campo falla igual por faltar.
- En desarrollo, `uv run --env-file .env` apunta `CREDENTIALS_DIRECTORY` a `credentials/`, que git
  ignora.

## Esquemas

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- `alias_generator=to_camel` y `serialize_by_alias=True` en el esquema base.
- `validate_by_name=True` en el esquema base: el código y las filas usan los nombres de Python, en
  snake_case. Sin él, `from_attributes` busca en una fila el alias, `createdAt`, y no encuentra
  `created_at`.
- `extra="forbid"` y `validate_by_name=False` en los esquemas de entrada: el cliente escribe solo
  en camelCase, y un campo en snake_case responde 422 en vez de aceptarse con dos nombres.
- Los parámetros de query se declaran en un esquema de entrada. Un parámetro desconocido responde
  422 en vez de ignorarse.

## Base de datos

Estándares: las preguntas *When do I make a `sessionmaker`?* y *When do I construct a `Session`,
when do I commit it, and when do I close it?* de
[*Session Basics*](../fuentes/sqlalchemy/session_basics.rst), y las secciones *Using AsyncSession
with Concurrent Tasks* y *Preventing Implicit IO when Using AsyncSession* de la
[extensión asyncio](../fuentes/sqlalchemy/asyncio.rst) de SQLAlchemy.

- `AsyncSession` con asyncpg.
- `lazy="raise"` en toda relación.
- Una relación bidireccional declara `back_populates` en los dos lados.
- Cada modelo va en su propio archivo, dentro de la carpeta de su dominio.
- Cada columna y cada relación se declaran en una sola línea. Contradice las 99 de
  [python.md](python.md): el modelo se lee de arriba abajo, una declaración por renglón.
- Un enum hereda de `StrEnum`. La `Base` guarda solo esos como `text` con `CHECK`; un `str, Enum`
  se vuelve un enum nativo de Postgres que guarda el nombre y no el valor.
- Una columna `created_at` es `CreatedAt`, y una `updated_at` es `UpdatedAt`, de la `Base`. Las
  dos toman `now()`; `updated_at` lo toma en cada `UPDATE` que emite SQLAlchemy.

## Migraciones

Estándar: la sección *What does Autogenerate Detect (and what does it not detect?)* de la
[autogeneración](../fuentes/alembic/autogenerate.rst) de Alembic.

- `alembic/` sale de la plantilla `async` de Alembic: las migraciones corren con asyncpg, como la
  app.
- La `MetaData` de la `Base` lleva una `naming_convention`: una migración no puede borrar ni cambiar
  una restricción sin nombre.

## Inyección de dependencias

- Las dependencias y los parámetros de una ruta se declaran con `Annotated`.
- La dependencia de la `AsyncSession` lleva `scope="function"`. El commit corre antes de enviar la
  respuesta: si falla, el cliente recibe el error y no un 200.

## Routers

- Los routers se incluyen en un `APIRouter(prefix="/api")` de `main.py`.
- Un recurso lleva el mismo nombre de archivo en `routers/`, `services/` y `schemas/`.
- Un `DELETE` borra la fila de verdad. Una columna `deleted_at` se escribe con un `PATCH`, como
  cualquier otro campo, y nunca reemplaza al borrado: un `DELETE` que solo marca la fila obliga a
  filtrar cada consulta y cada índice único.

## Ciclo de vida

- El arranque y el cierre van en el `lifespan` de la app: `on_event` está obsoleto.

## Tareas en segundo plano

- El trabajo que sigue a la respuesta va en `BackgroundTasks`.

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

Estándar: [*File Upload Cheat Sheet*](../fuentes/owasp/File_Upload.md) de OWASP.

Contrato: [transversal.md](transversal.md#archivos).

- El servidor recibe un archivo como `UploadFile`.
- Toda imagen se vuelve a codificar con Pillow antes de guardarse, aplicando antes la orientación
  EXIF. Endurece OWASP, que lo deja como opcional: borra los metadatos de la foto, y sin aplicar
  antes la orientación queda girada.
- Cada archivo es una fila de una tabla hija de su recurso, `<recurso>_file`.
- La fila de un archivo guarda su tipo, su tamaño y su nombre original.
- El archivo en disco se llama con el ID de su fila.
- Un archivo tiene los permisos de su recurso.
- Un barrido borra los archivos con más de una hora en disco y sin fila en ninguna tabla `_file`.
  El margen deja terminar la subida que todavía no confirmó su fila.

## Autenticación

Estándares: de [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt), las secciones 2.1.1 y 2.1.2
de *AAL1*, 3.2.2 *Rate Limiting (Throttling)*, 4.1 *Authenticator Binding* y 4.6 *Account
Notifications*, y las secciones 2.2.1 y 2.2.2 de *AAL2* en las cuentas de administración.

- Una cuenta se registra con un correo o con un teléfono, verificado con un código.
- Una cuenta no tiene nombre de usuario.
- El registro responde 409 si la cuenta ya existe.
- Una IP que recibe 10 respuestas 409 del registro en 15 minutos queda bloqueada 30 minutos: quien
  prueba correos o teléfonos en serie busca cuentas existentes.
- Una cuenta de administración inicia sesión solo con passkeys.
- Cambiar el correo, el teléfono o una passkey pide volver a autenticarse en ese momento.
- El correo y el teléfono se cambian desde una sesión abierta, con un código enviado al nuevo, y el
  viejo recibe un aviso.
- Las direcciones de aviso son el correo, el teléfono y el push a las apps con sesión abierta: una
  cuenta con un solo medio también tiene dos.
- El límite de fallos consecutivos es 100.
- Desde el quinto fallo consecutivo, el siguiente intento espera 30 segundos, que se duplican con
  cada fallo hasta una hora, y un intento antes de tiempo responde 429: llegar a los 100 fallos
  lleva unos cuatro días, y el titular lo ve antes.
- Los fallos consecutivos y la hora del siguiente intento viven en la base: sin ventana de tiempo,
  perderlos le regala al atacante 100 intentos nuevos.
- El titular ve en la app cada intento fallido y cada autenticador deshabilitado.
- Un autenticador deshabilitado cierra solo el login con él: las sesiones abiertas siguen.
- El titular vuelve a habilitarlo desde una sesión abierta o, si es la contraseña, restableciéndola.
- El login con contraseña responde el mismo error exista o no la cuenta.

## Código por SMS

Estándar: la sección 3.1.3.2 *Out-of-Band Verifiers* de
[NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt).

Contrato: [transversal.md](transversal.md#código-por-sms).

- El servidor valida el número con `phonenumbers`.
- Verificar el primer código de un número sin cuenta crea la cuenta.
- El código vive en Valkey, con un TTL de 10 minutos.
- Un código nuevo reemplaza al anterior: solo vale el último.
- Cada número recibe un SMS por minuto, hasta 5 por hora y hasta 10 por día, y cada IP pide hasta
  10 por hora.
- Un código se invalida al tercer intento fallido.
- Quien perdió su número y no tiene otra forma de entrar recupera la cuenta con un administrador.

## Contraseñas

Estándares: de [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt), la sección 3.1.1
*Passwords*, salvo sus tres últimos párrafos, sobre cómo se guarda la contraseña, y los que cita
[transversal.md](transversal.md#contraseñas), y la sección 4.2 *Account Recovery*; y la sección
*Argon2id* del [*Password Storage Cheat Sheet*](../fuentes/owasp/Password_Storage.md) de OWASP.

Contrato: [transversal.md](transversal.md#contraseñas).

- Una contraseña se guarda con `PasswordHash.recommended()` de pwdlib: Argon2id con 64 MiB y 3
  pasadas, por encima de los mínimos de OWASP.
- Toda contraseña tiene al menos 8 caracteres. Contradice NIST, que pide 15 cuando la contraseña es
  el único factor: una de 15 aleja al usuario.
- La lista de bloqueo es un archivo del servidor.
- Una cuenta restablece su contraseña con un código que recibe, a su elección, en el correo o en el
  teléfono que registró.
- La solicitud para restablecer responde 404 si la cuenta no existe, y una IP que recibe 10 en 15
  minutos queda bloqueada 30 minutos: el registro ya revela si la cuenta existe.
- El código para restablecer tiene 6 dígitos, vive en Valkey con un TTL de 10 minutos, y uno nuevo
  reemplaza al anterior.
- Un código para restablecer se invalida al tercer intento fallido, y cada fallo cuenta entre los
  fallos consecutivos de la contraseña.
- Cada correo y cada número reciben un código para restablecer por minuto, y hasta 5 por hora.
- Cambiar la contraseña cierra las demás sesiones y renueva los tokens de la sesión que hizo el
  cambio; restablecerla cierra todas.

## Correo y SMS

Estándar: [Standard Webhooks](../fuentes/standard-webhooks/standard-webhooks.md).

- El correo sale por la API de correo de Equipaggio, `PUT /email/{id}`, y el SMS, por su pasarela,
  `PUT /sms/{id}`.
- Cada correo lleva una parte en texto y otra en HTML.
- Un correo rebotado llega por el webhook de Equipaggio. El servidor marca la dirección como
  inválida, y la app le dice al usuario que su correo no llega.

## Envíos al exterior

- Primero la evidencia en la base, después el envío best-effort. Un fallo de entrega no tumba la
  operación.

## Errores

Contrato: [transversal.md](transversal.md#errores).

- Un error con tipo propio se lanza con `AppError`; uno que su código de estado ya explica, con
  `HTTPException`, y sale como `about:blank`.

## Fechas

Contrato: [transversal.md](transversal.md#fechas).

- Los campos de fecha y hora de los esquemas son `Timestamp`, del esquema base: entra solo como
  cadena RFC 3339 y queda en UTC. `AwareDatetime` acepta también un número como epoch y una hora sin
  segundos, y conserva el desfase que recibe; un `datetime`, además, una hora sin zona.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- El servidor traduce con Babel.
- El `.mo` no se versiona: `release.yml` lo compila del `.po` con
  `pybabel compile -d src/app/locale` y viaja en el artefacto. Un `.mo` versionado puede quedar
  desfasado de su `.po`, y el código de una versión no cambia en el servidor.
- El servidor guarda el idioma de `Accept-Language` con el FID de cada instalación de la app, y en
  el usuario el último elegido, para el correo.

## Límite de tasa

Estándar: la sección 4 de [RFC 6585](../fuentes/rfc/rfc6585.txt), *429 Too Many Requests*.

- Los contadores viven en Valkey, compartidos por todos los procesos.
- Todo 429 lleva `Retry-After`. Endurece RFC 6585, que lo deja opcional: el cliente sabe cuándo
  reintentar.

## Llamadas de voz y video

Contrato: [transversal.md](transversal.md#llamadas-de-voz-y-video).

- Una credencial de TURN dura 1 hora. coturn la revisa solo al abrir el relay, así que vencer no
  corta una llamada en curso.
- La llamada que suena vive en Valkey, con su oferta y un TTL de 60 segundos. Una llamada sin
  respuesta en ese plazo queda perdida.

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

- Las respuestas de Nominatim se guardan en Valkey.

## Montos

Contrato: [transversal.md](transversal.md#montos).

- Un monto es `Decimal` en los esquemas y entra solo como cadena. Pydantic acepta también un número
  JSON, lo declara así en el OpenAPI de las peticiones y lo recorta si excede un `double`.
- Un monto se serializa sin exponente. Pydantic lo escribe con `str`, que puede dar `1E-7`.

## OpenAPI y clientes

Estándar: el *Operation Object* y el *Responses Object* de la
[especificación OpenAPI 3.1](../fuentes/openapi/openapi-3.1.2.md).

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- Cada router lleva un solo tag, y el `operationId` es el tag seguido del nombre de la función, en
  camelCase. El tag lo hace único en toda la API.
- El OpenAPI se exporta a `server/openapi.json`, versionado, y una prueba falla si no coincide con
  la app. Un cambio de contrato se ve en el diff.
- Cada operación declara sus errores como `application/problem+json` con el esquema del problema, y
  el 422 con el del problema `validation`. Endurece OpenAPI, que solo espera que se documenten los
  errores conocidos: un cliente generado tipa el error que de verdad recibe.
- En producción no se sirven el OpenAPI ni su documentación. El contrato está en el repositorio, y
  nadie de afuera necesita el mapa de la API.

## Paginación

Contrato: [transversal.md](transversal.md#paginación).

- La petición es `PageParams`, o `SkipParams` si acepta `skip`. La respuesta es `Page[T]`, o
  `CountedPage[T]` si devuelve `totalSize`.
- El token guarda la columna y el `id` del último elemento, y los filtros, cifrados con Fernet y
  la clave `PAGE_TOKEN_KEY`.

## Pagos

Contrato: [transversal.md](transversal.md#pagos).

- El ID de cada evento procesado se guarda con una restricción única: dos entregas simultáneas del
  mismo evento no se procesan las dos.

## Passkeys

Contrato: [transversal.md](transversal.md#passkeys).

- Las passkeys se validan con `webauthn`.
- Toda passkey es descubrible (`residentKey="required"`): el usuario entra sin escribir su correo.
- El challenge vive en Valkey y se borra al usarlo.
- El titular ve sus passkeys, con su nombre y su último uso, y borra la que quiera: así revoca la
  de un dispositivo perdido.
- Una cuenta con passkey se recupera con el código para restablecer de «Contraseñas».
- La recuperación se aplica 24 horas después, sin cerrar las sesiones, y el titular la cancela
  desde la app: quien roba el correo no entra antes de que el dueño la vea.
- Una cuenta de administración pide `userVerification="required"`: sin esa verificación la passkey
  es un solo factor.
- Una cuenta de administración la recupera otro administrador, nunca un código: quien roba el
  correo o el teléfono no se lleva la administración.

## Permisos

Estándares: [*Authorization Cheat Sheet*](../fuentes/owasp/Authorization.md) de OWASP y las
secciones 15.5.4 *403 Forbidden* y 15.5.5 *404 Not Found* de
[RFC 9110](../fuentes/rfc/rfc9110.txt).

- Cada ruta declara con una dependencia de FastAPI el permiso que exige. El permiso queda a la
  vista en la ruta.
- Un recurso que no pertenece al usuario responde 404, como si no existiera; uno que el usuario ve
  pero sobre el que no puede hacer esa acción responde 403. Es la opción que RFC 9110 da para
  ocultar un recurso: una sola consulta, filtrada por el usuario, resuelve las dos cosas y no
  confirma que el recurso existe.

## Push

Estándares: [RFC 8030](../fuentes/rfc/rfc8030.txt) y [RFC 8291](../fuentes/rfc/rfc8291.txt).

Contrato: [transversal.md](transversal.md#push).

- El servidor envía a FCM con `messaging.send_each_async` del Admin SDK, con el FID en `fid`.
- El servidor envía Web Push con `webpush_async` de pywebpush y una sola `aiohttp.ClientSession`
  para toda la app: sin ella, cada envío abre una sesión nueva.
- Un Web Push de un aviso que no caduca lleva un TTL de 28 días, el de FCM por defecto: con el TTL 0
  de pywebpush, se pierde si el navegador no está en línea.
- Una suscripción web que responde 404 o 410 se borra: los servicios de push responden 410, aunque
  RFC 8030 pide 404.

## Registro de eventos

Estándares: las secciones *Where to record event data*, *Which events to log*, *Event attributes*,
*Data to exclude*, *Customizable logging*, *Event collection*, *Verification*, *Protection* y
*Disposal of logs* del [*Logging Cheat Sheet*](../fuentes/owasp/Logging.md) de OWASP, y la sección
*The Vocabulary* del
[*Application Logging Vocabulary Cheat Sheet*](../fuentes/owasp/Logging_Vocabulary.md) de OWASP.

- Los eventos van en una sola tabla, `event_log`: lo que pasó alrededor de una hora se lee en una
  consulta. Un cambio de fila también es un evento, con los campos cambiados en `details`.
- `action` es el nombre del vocabulario sin sus parámetros, como `authn_login_fail`. Los parámetros
  van en sus columnas: así se consultan.
- Las demás columnas son `occurred_at`, `actor_id`, `actor_label`, `target_type`, `target_id`,
  `level`, `ip_address`, `user_agent`, `trace_id`, `details` en `jsonb` y, si el repositorio es
  multi-tenant, `tenant_id` en todo evento.
- `actor_label` guarda el identificador tal como llegó: así queda el intento sobre una cuenta que
  no existe.
- `level` es `info`, `warn` o `critical`, el nivel que el vocabulario da al evento.
- `trace_id` es el trace-id del span actual, el mismo del log y del `traceId` del error.
- Un valor de una fila entra en `details` solo si su tabla y su campo están en una lista blanca:
  una columna nueva no se registra sola. Un campo fuera de la lista se registra como cambiado, sin
  su valor.
- La retención de `event_log` es una constante en días, mayor que cero, en `services/events.py`:
  la IP y el user agent son datos personales. La plantilla guarda 365.
- Un evento se escribe en su propia transacción, salvo el de un cambio de fila, que va en la del
  cambio: un fallo queda aunque la petición se deshaga, y un cambio deshecho no queda.
- El rol de la app solo tiene `INSERT` y `SELECT` sobre `event_log`: un error o una inyección en la
  app no cambian ni borran el rastro. El rol no es el dueño de la tabla.
- Solo el rol de la app y el dueño leen `event_log`, y ningún rol es miembro de ellos: la
  revisión periódica de quién lee que pide *Protection* corre en cada CI.
- La copia en solo lectura que pide *Protection* es el respaldo de
  [despliegue.md](despliegue.md#respaldos), en cada corrida.
- *Protection* queda sin efecto en detectar que un registro se cambió o se borró: solo pueden
  hacerlo el dueño y `root`, y `root` también cambia lo que lo detectaría. Lo que pasó hasta el
  último respaldo queda en una copia que no se reescribe.
- *Protection* queda sin efecto en registrar y vigilar cada acceso: solo leen la app y quien opera
  el servidor, y vigilar es un proceso de operación.
- El rol de la app se llama como la app.
- La purga es una tarea periódica que borra lo que pasó la retención con la credencial del dueño
  del esquema, la de las migraciones: el servidor no la recibe.
- Los permisos de una tabla los da la migración que la crea: quedan versionados y el CI los prueba.
- `actor_id` es un `uuid` sin clave foránea, y `ip_address`, un `inet`: el rastro
  sobrevive a la cuenta, e `inet` rechaza una dirección malformada.

## Reintentos

Contrato: [transversal.md](transversal.md#reintentos).

## Salud

- `GET /api/health` responde 204, o 503 si la base o Valkey no contestan: un servidor con una
  dependencia caída no está vivo aunque el proceso responda.
- `GET /api/health/events` responde `lastCriticalAt`, la hora del último evento `critical` de
  `event_log`, y `lastBackupAt`, la fecha de `last-backup` de
  [despliegue.md](despliegue.md#respaldos), o `null` si no hay. Quien lo consulta decide cuándo
  avisar: el servidor no fija umbrales.
- La misma ruta responde `lastEventAt`, la hora del último evento de `event_log` de cualquier
  nivel, o `null`: si `event_log` deja de recibir eventos, `lastCriticalAt` sigue en `null`, como
  cuando no pasó nada grave.
- La misma ruta responde `diskFreeBytes` y `diskTotalBytes`, del disco de su `StateDirectory=`:
  con el disco lleno PostgreSQL deja de escribir, y `SELECT 1` sigue respondiendo. El libre es el
  que puede escribir un usuario sin privilegios, como PostgreSQL.
- La ruta exige el token de `health_token` en `Authorization: Bearer`, comparado en tiempo
  constante, y sin él responde 401.
- El servidor lee `last-backup` en la carpeta padre de su `StateDirectory=`, sin otra
  configuración.

## Sesión

Estándares: [RFC 7519](../fuentes/rfc/rfc7519.txt), [RFC 8725](../fuentes/rfc/rfc8725.txt), la
sección 4.14 *Refresh Token Protection* de [RFC 9700](../fuentes/rfc/rfc9700.txt) y, en el nivel 1
de ASVS 5.0 de OWASP, el capítulo
[V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md) y las secciones V3.3
*Cookie Setup* y V3.5 *Browser Origin Separation* de
[V3 *Web Frontend Security*](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md).

Contrato: [transversal.md](transversal.md#sesión).

- La web y las apps comparten la tabla de sesiones: cambia solo el token que presenta cada una.
- Cada inicio de sesión crea una fila de sesión, con su creación y su último uso. La sesión vence
  tras 30 días sin uso, y cerrar sesión borra la fila.
- El último uso se actualiza al refrescar, en una app, y a lo sumo cada 15 minutos, en la web: una
  escritura por petición cargaría la base sin mover el vencimiento.
- Una tarea periódica borra las sesiones vencidas.
- El token de la web es un valor aleatorio de 256 bits, y la fila guarda su SHA-256: quien lee la
  base no se lleva ninguna sesión.
- La cookie de la web es `__Host-session`, `HttpOnly` y `SameSite=Strict`, con 30 días de `Max-Age`
  que se renuevan con el último uso. Endurece V3.3, que pide el prefijo y los dos atributos en el
  nivel 2: ningún script la lee, ninguna petición de otro sitio la lleva y ningún subdominio la
  reemplaza.
- Una petición con la cookie y un método que no es seguro responde 403 si su `Origin` falta o no es
  el del servidor. De las opciones de V3.5.2, es la que no le pide nada a la web.
- El token de acceso de una app es un JWT firmado con HS256 que vence en 15 minutos, con el id de su
  sesión en `sid`.
- El id de una sesión de una app que se cierra o se borra queda 15 minutos en Valkey, lo que dura su
  último token de acceso, y el servidor rechaza el JWT de una sesión de esa lista. Es la lista de
  revocación entre las opciones de V7.4.1.
- El token de refresco es el id de su sesión y un secreto aleatorio de 256 bits, firmados con HMAC,
  y el secreto rota en cada uso. La firma es la integridad que RFC 9700 pide al token que lleva su
  sesión.
- La fila de una sesión de una app guarda el SHA-256 del secreto vigente y el del anterior. El
  anterior vale mientras el vigente no se usó. Contradice RFC 9700, que lo invalida en el acto: una
  respuesta perdida cerraría la sesión del dueño y le avisaría de un robo.
- Presentar el anterior reemplaza el vigente, y el anterior no cambia. Si el vigente pasara a ser el
  anterior, un dueño y un ladrón que refrescan por turnos nunca presentarían un reúso.
- Cualquier otro secreto de la sesión es un reúso: borra la sesión, y el titular lo ve en la app.
  Un token robado se descubre cuando el dueño vuelve a refrescar.
- Un token de refresco con la firma inválida o de una sesión que no existe responde 401, sin aviso.

## Trazas

Estándar: la regla `trace-id` de la sección 3.2.2.2 *version-format* y la sección 3.2.2.3
*trace-id* de [Trace Context](../fuentes/w3c/trace-context-1.md) de W3C.

- La app configura un `TracerProvider` del SDK de OpenTelemetry: sin él, FastAPI no crea spans y no
  hay trace-id.
- El propagador global de OpenTelemetry ignora `traceparent`: cada petición y cada WebSocket
  empiezan una traza nueva. El cliente no elige el id con el que se buscan sus registros. Es un
  propagador propio: con `OTEL_PROPAGATORS=none`, FastAPI falla en cada petición.
- Cada vuelta de una tarea periódica empieza su propia traza.
- Cada línea de log lleva el trace-id del span actual.

## Versión mínima de cliente

Contrato: [transversal.md](transversal.md#versión-mínima-de-cliente).

- La configuración guarda la versión mínima de cada pieza.
- La comprobación es una dependencia del router de `/api`: corre antes que las dependencias de cada
  ruta y que la validación, y un cliente viejo recibe `client-outdated` antes que un 401 o un 422.

## WebSocket

Estándar: las secciones *Origin Header Validation*, *Message-Level Authorization*, *Input
Validation* y *Denial-of-Service Protection* del
[*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

Contrato: [transversal.md](transversal.md#websocket).

- Cada proceso se suscribe a Valkey y reenvía a sus conexiones, con un canal por usuario.
- Un handshake con la cookie exige un `Origin` igual al de la web, y uno con `Authorization` no lo
  revisa. Contradice OWASP, que lo pide en todo handshake: una app nativa no manda `Origin`, y el
  secuestro entre sitios solo existe con la credencial que el navegador agrega por su cuenta.
- Un usuario tiene a lo sumo 10 conexiones abiertas, y la siguiente se rechaza en el handshake:
  alcanza para varias pestañas y dispositivos. Manda a lo sumo 100 mensajes por minuto, y la
  conexión que se pasa se cierra con 1008. Los contadores viven en Valkey, compartidos por todos
  los procesos.
- Una conexión sin mensajes no se cierra. Contradice OWASP, que pide cerrar las inactivas: la
  conexión existe para esperar eventos del servidor, y el ping de Uvicorn ya cierra la que se cayó.
- Los mensajes no llevan nonce. Contradice OWASP, que lo pide contra la repetición: WSS ya impide
  que alguien fuera de la conexión repita un mensaje.

<br>

---
---

<br>

## Pruebas

- Las pruebas asíncronas corren con el plugin de pytest de AnyIO, con `anyio_mode = "auto"`, y
  `anyio_backend` es `asyncio`: asyncpg y la app solo corren en asyncio.
- Las pruebas corren contra PostgreSQL. Ven los mismos tipos y restricciones que producción.
- La base de prueba se arma con `alembic upgrade head` antes de pytest: las pruebas ven el esquema
  de las migraciones, no el de los modelos.
- Las migraciones de prueba entran como el rol dueño del esquema, y cada conexión de las pruebas
  toma el rol del servidor con `SET ROLE`: una prueba tiene los permisos del servidor en
  producción, y una tabla sin su `GRANT` falla en el CI. Lo que corre el dueño, como la purga, se
  prueba con el fixture `owner`.
- Las pruebas corren contra Valkey, que se vacía en cada prueba: un conteo de intentos no pasa de
  una prueba a la siguiente.
- Cada prueba corre en una transacción que se deshace al terminar, y las sesiones de la app se unen
  a ella con `join_transaction_mode="create_savepoint"`: un commit de la app no sale de la prueba.
- Una prueba llama a la app con `AsyncClient` y `ASGITransport` de httpx, y a un WebSocket con
  `ASGIWebSocketTransport` de httpx-ws, nunca con `TestClient`: corren en el loop de la prueba y
  ven su transacción, y `TestClient` corre la app en otro loop.
- Una dependencia se reemplaza en una prueba con `app.dependency_overrides`.

<br>

---
---

<br>

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Todo campo de `Settings` es obligatorio | `test_settings_are_required` |
| Las dependencias y los parámetros de una ruta con `Annotated` | ruff `FAST002` |
| El commit corre antes de enviar la respuesta | `test_failed_commit_is_a_server_error` |
| Los nombres en camelCase: todo esquema hereda del esquema base | `test_schemas_inherit_schema` |
| El esquema base lee por nombre, y el de entrada solo por alias | `test_schemas_read_rows_by_name` |
| `lazy="raise"` | `test_relationships_raise` |
| `Timestamp` en los esquemas | `test_schema_datetimes_are_timestamps` |
| Un enum hereda de `StrEnum` | `test_enums_are_checked_text` y ruff `UP042` |
| Una columna o relación por línea | `test_mapped_attributes_fit_one_line`, y `ruff format` con `line-length = 320`, el máximo de ruff, en `models/ruff.toml` |
| `traceparent` no continúa la traza | `test_traceparent_starts_a_new_trace` |
| Un solo tag por router y el `operationId` en camelCase | `test_operation_ids` |
| `server/openapi.json` coincide con la app | `test_openapi_file_is_current` |
| La versión mínima de cliente, en tres enteros | `test_outdated_client_is_rejected` |
| La base de prueba con las migraciones | `uv run alembic upgrade head` antes de pytest en el job `server` de CI |
| Las migraciones de prueba como el dueño, y las pruebas con los permisos del servidor | `alembic upgrade head` con la credencial del dueño en el job `server` de CI, y `run_as_server` de `tests/conftest.py` |
| Las pruebas nunca llaman a la app con `TestClient` | ruff `TID251` con `fastapi.testclient` y `starlette.testclient` en `banned-api` |
| Un `pageToken` ilegible o con otros parámetros responde 422 | `test_invalid_page_token_points_to_the_parameter` |
| El rol de la app no cambia ni borra `event_log`, y la purga respeta la retención | `test_server_cannot_change_events` y `test_purge_deletes_only_expired_events` |
| Solo el rol de la app y el dueño leen `event_log` | `test_only_the_server_and_owner_read_events` |
| `GET /api/health/events` exige el token | `test_events_need_the_token` |
| `GET /api/health/events` dice el último evento de cualquier nivel | `test_events_tell_the_last_event` |
| `GET /api/health/events` dice el disco de su carpeta | `test_events_tell_the_disk` |
| Las reglas de [postgres.md](postgres.md) | Las pruebas de `tests/test_conventions.py` que nombra esa página |
