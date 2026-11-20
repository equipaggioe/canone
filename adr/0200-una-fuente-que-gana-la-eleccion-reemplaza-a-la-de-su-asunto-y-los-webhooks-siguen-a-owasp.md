# ADR-0200 · Una fuente que gana la elección reemplaza a la de su asunto, y los webhooks siguen a OWASP

- **Estado:** Aceptada
- **Fecha:** 2026-11-20
- **Alcance:** «Revisión» de [plataformas/README.md](../plataformas/README.md), «Correo y SMS», «Llamadas de voz y video» y «Cumplimiento» de [plataformas/fastapi.md](../plataformas/fastapi.md), la fila de los seeders de [plataformas/despliegue.md](../plataformas/despliegue.md), `fuentes/`, `scripts/verificar.py`, `scripts/contar_enunciados.py` y las pruebas de `plantilla/server/`

## Contexto

La revisión de `fastapi.md` del [ADR-0199](0199-fastapi-cada-fila-detecta-lo-que-promete-y-el-servidor-reconecta-compara-los-server-default-y-limita-cada-subida.md) dejó temas sin confirmar y defectos fuera de la página. Esto es lo que se comprobó.

- OWASP publica el *Webhook Security Cheat Sheet*. Cubre las decisiones de quien recibe un webhook: el esquema de la firma, aceptar cualquier firma que valga, el tiempo constante, la tolerancia del timestamp, la idempotencia por el id del evento y el 401 sin detalle. Recomienda Standard Webhooks como esquema para un protocolo nuevo. Es de orden 2 y Standard Webhooks de orden 3, así que por «Elección entre fuentes» le gana. El paso 2 de «Revisión» impedía proponerla, porque las convenciones del asunto ya estaban escritas.
- coturn 4.6.1 revisa el vencimiento de una credencial temporal en `get_user_key` (`userdb.c`) solo mientras la sesión no tiene guardada su clave (`hmackey_set` en `ns_turn_server.c`). Las peticiones siguientes de la misma asignación solo verifican la integridad del mensaje.
- `DESCARTADAS` de `verificar.py` prohibía declarar `psycopg` o `pytest-asyncio` en el servidor, algo que ninguna página escribe. Se probó en Windows, con deptry 0.25.1 y pytest 9.2.0. Un `psycopg` declarado y sin usar ya hace fallar deptry con `DEP002`. `pytest-asyncio` 1.5.0 instalado junto al plugin de AnyIO detiene pytest con un `INTERNALERROR`, porque `filterwarnings = ["error"]` vuelve error su aviso de configuración. Un `pytest-asyncio` del grupo de desarrollo no lo marca deptry, pero `uv sync` lo instala.
- `bitacoras_solo_lectura` de `verificar.py` exigía una regla que solo estaba en el ADR-0008, buscaba por el nombre del archivo del router y listaba tablas que `fastapi.md` ya no admite: los eventos van en una sola tabla, `event_log`. Que el servidor no cambie ni borre un evento ya lo hacen cumplir los permisos de la base, con su prueba.
- Tres convenciones no tenían herramienta. Con el 422 apuntando a `Problem`, o con un esquema vacío, `test_errors_are_problems` pasaba. Una `/api/health` que no mira la base, o un token equivocado de nivel `critical`, pasaban las pruebas. Las pruebas nuevas fallan con cada uno, y las 98 pasan en Debian 13 con PostgreSQL 17 y Valkey.

## Decisión

1. Una revisión puede proponer una fuente nueva para convenciones ya escritas si, por «Elección entre fuentes», le gana a la que hoy sigue su asunto. Esto reemplaza la primera mitad del punto 10 del [ADR-0163](0163-una-revision-recorre-el-documento-entero-y-propone-tambien-lo-que-falta.md).
2. Los webhooks de «Correo y SMS» siguen al *Webhook Security Cheat Sheet* de OWASP. Standard Webhooks pasa a ser el esquema de la firma, que se enlaza en su versión 1.0.2, y sale de `fuentes/`: ya no es origen de ninguna convención. Entran aceptar el webhook si una firma vale, solo de los esquemas esperados, y responder 401 sin decir por qué; y responder 200 a un webhook repetido sin repetir su efecto.
3. La duración de una credencial de TURN enlaza el código de coturn 4.6.1 que prueba que se revisa al abrir el relay.
4. Sale `DESCARTADAS` de `verificar.py`, con `dependencias`, que solo la usaba ella.
5. Sale `bitacoras_solo_lectura` de `verificar.py`.
6. `test_errors_are_problems` exige además el esquema del problema de cada error, y el de `validation` en el 422. Entran `test_health_needs_the_database` y el nivel `warn` en `test_wrong_token_is_an_event`.
7. La fila de los seeders de `despliegue.md` deja de decir «sin duplicar filas»: lo asegura el seeder de prueba, no `deploy.py`.
8. Sale `alembic/versions/.gitkeep` de la plantilla: la carpeta ya tiene la migración de `event_log`.

## Consecuencias

- Una revisión compara la fuente de cada asunto con las demás candidatas, aunque sus convenciones ya estén escritas.
- Un repositorio con un webhook propio lo verifica con el esquema de Standard Webhooks y responde 401 y 200 como dice «Correo y SMS».
- Un router de `event_log` con una ruta que escribe ya no lo marca `verificar.py`. Lo que el servidor no puede hacer sobre `event_log` lo prueban los permisos de la base.
- Si una versión de `pytest-asyncio` deja de avisar, instalarlo junto a AnyIO ya no detiene pytest. No se comprobó que entonces cambie el resultado de alguna prueba.

## Descartado

- **Mantener Standard Webhooks como fuente del asunto:** pierde la elección contra OWASP, que además cubre la idempotencia y el 401 que Standard Webhooks no fija.
- **Escribir en `fastapi.md` que no se declara `psycopg` ni `pytest-asyncio`:** no hay síntoma que nombrar más allá de lo que ya hacen fallar deptry y pytest.
- **Escribir la regla de las bitácoras en `fastapi.md`:** buscar por el nombre del archivo deja pasar un router con otro nombre, y los permisos de la base ya cubren lo que el servidor no puede hacer sobre `event_log`.
