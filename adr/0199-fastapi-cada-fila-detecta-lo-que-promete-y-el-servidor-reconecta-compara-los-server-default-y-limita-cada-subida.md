# ADR-0199 · Cada fila de `fastapi.md` detecta lo que promete, y el servidor reconecta tras un reinicio de PostgreSQL, compara los `server_default` y limita cada subida

- **Estado:** Aceptada. El punto 4 es *(propuesta)*.
- **Fecha:** 2026-11-20
- **Alcance:** [plataformas/fastapi.md](../plataformas/fastapi.md) y `plantilla/server/`: `database.py`, `tasks.py`, `tracing.py`, `services/files.py`, `alembic/env.py` y sus pruebas

## Contexto

Se revisó `fastapi.md` con los cinco pasos de [plataformas/README.md](../plataformas/README.md#revisión). Cada fila de «Cumplimiento» se probó rompiendo su convención en una copia de la plantilla del servidor, en Debian 13 con PostgreSQL 17 y Valkey, con FastAPI 0.163.1, SQLAlchemy 2.1.9, Alembic 1.20.1, Pydantic 2.14.3, OpenTelemetry 1.45.2, Pillow 13.0.0, pytest 9.2.0 y ruff 0.17.5.

- `test_schemas_inherit_schema` solo miraba `schemas/`: un `BaseModel` en un router pasaba.
- Un `Enum` que no es `str` y no está en una columna no lo veían ni `test_enums_are_checked_text` ni `UP042`.
- `test_otlp_variables_export_nothing` pasaba sin `telemetry={"auto_configure": False}`: sin el exportador OTLP instalado, FastAPI solo avisa y no agrega nada. Con `opentelemetry-exporter-otlp-proto-http` instalado, agrega un procesador.
- `test_log_lines_have_no_line_breaks` probaba la clase del formateador, no el handler que instala la app: cambiar el formateador de `install()` pasaba.
- `test_reencode_rejects_an_image_past_the_pixel_limit` pasaba sin el filtro de avisos de `reencode`, porque `filterwarnings = ["error"]` de pytest hacía ese trabajo.
- `alembic check` no ve un cambio de `server_default`. Con `compare_server_default=True` lo ve, y sobre la plantilla no da falsos positivos. Tampoco ve un valor nuevo de un `StrEnum`, que la página ya manda escribir a mano.
- Ninguna prueba ve si los seeders corrieron, y `tasks.py` no se compara con la plantilla: un `migrate` partido en dos transacciones pasaba las 95 pruebas. El seeder con el que `deploy.sh` prueba que no se duplican filas es idempotente por su `WHERE NOT EXISTS`, no por `deploy.py`.
- Sin `pool_pre_ping`, después de reiniciar PostgreSQL la primera consulta de cada conexión del pool falla con `DBAPIError`. Con `pool_pre_ping=True`, no.
- Un `UploadFile` acepta 50 MB sin ningún límite.
- `@app.on_event` ya falla en Pyrefly con `deprecated = "error"`.
- Con `OTEL_PROPAGATORS=none` y sin el propagador propio, cada petición da `AttributeError`.

## Decisión

1. Cada fila de «Cumplimiento» detecta lo que promete:
   - `test_schemas_inherit_schema` recorre todos los módulos de la app.
   - `test_enums_are_strenums` exige `StrEnum` en todo enum de la app.
   - La sonda de OTLP comprueba además que `auto_configure` sea `False`.
   - La prueba del log formatea con `tracing.log_handler()`, el handler que instala la app.
   - La prueba del límite de píxeles corre con `filterwarnings("default")`.
   - Las filas de `alembic check`, de la base de prueba y de `deploy.sh` se acotan a lo que su herramienta hace cumplir.
   - Entra la fila de los archivos que se copian sin editar, con `verificar.py --repo`.
2. El engine lleva `pool_pre_ping=True`, y `env.py` lleva `compare_server_default=True`.
3. Cada recurso fija en una constante el tamaño máximo de un archivo. Una subida que lo pasa responde 413, con `files.read`.
4. *(propuesta)* `migrate`, `mock` y los seeders pasan de `tasks.py` a `database.py`, que se copia sin editar. Así `verificar.py` exige en cada repositorio la transacción única que prueba `deploy.sh`. `tasks.py` queda solo con el registro de tareas.
5. Cada convención va con el origen de su asunto y en su lugar:
   - El borrado por `ON DELETE` sale de *Session Basics, Deleting*.
   - La clave `uuid` de `<recurso>_file` sale de *Filename Safety*.
   - En Push, lo que dicen pywebpush y autopush va aparte de lo que dice RFC 8030.
   - Las elecciones van antes que las convenciones adoptadas.
   - Los permisos de una tabla pasan a «Migraciones».
6. Salen la convención del extra `asyncio`, la de `lifespan`, el enlace a un ADR, el enlace a MDN y lo que repetía `postgres.md` (las particiones de la purga) o una fila de Cumplimiento (el `alembic check` del CI, el CI que revisa quién lee `event_log`). La razón de `auto_configure` nombra la condición en la que se cumple.

## Consecuencias

- Un repositorio copia el nuevo `database.py`, `env.py`, `tracing.py`, `services/files.py`, `tests/test_conventions.py`, `tests/test_files.py` y `tests/test_tasks.py`, y saca de su `tasks.py` lo que pasó a `database.py`.
- Un repositorio que ya tiene un `server_default` distinto en su base y en su modelo empieza a fallar en `alembic check` hasta escribir la migración.
- Queda sin herramienta que un seeder sea idempotente, que el tipo de un problema use el esquema de su problema y que `/api/health` responda 503 con la base caída.
- No está comprobado que una actualización de paquetes reinicie PostgreSQL sin reiniciar el servidor: `pool_pre_ping` se justifica por cualquier reinicio de PostgreSQL con la app arriba.

## Descartado

- **Meter `tasks.py` entre los archivos que se copian sin editar:** cada repositorio agrega sus tareas a `TASKS` y sus calendarios a `TIMERS`.
- **Que la sonda de OTLP instale el exportador:** agregaría una dependencia que la app no usa.
