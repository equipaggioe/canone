# ADR-0011 · La pasada periódica es una función, y el disparador va aparte

- **Estado:** Aceptada. El script del punto 2, la espera del punto 4, el «apagado por defecto» del punto 6 y el punto 7 los reemplaza el [ADR-0041](0041-una-tarea-periodica-se-dispara-desde-la-pieza-y-su-interruptor-es-obligatorio.md)
- **Fecha:** 2026-09-23
- **Alcance:** `server/`, todos los repositorios

## Contexto

`fastapi.md` tiene una sección sobre el trabajo que no cabe en el request, y dice que no hay cola
de tareas. No cubre el trabajo **periódico**, que es otra cosa: nadie lo pidió, y hay que hacerlo
igual. Las retenciones del ADR-0008 lo necesitan, y hoy cada repositorio lo resolvió a su manera:

| Repositorio | Cómo |
|---|---|
| vettore | Siete lazos en `main.py`, con `@app.on_event`, ~45 líneas de andamiaje repetidas siete veces |
| concordia | Un lazo en el `lifespan` **y** un script en `scripts/ops/`, los dos sobre la misma función |
| banditore | Un proceso aparte, `python -m app.maintenance`, disparado a mano |
| navetta, presenze | No hay |

Los lazos de vettore no toman ningún candado: con dos workers, cada purga corre dos veces. Su
propio `core/rate_limit.py` ya documenta el mismo problema para el límite de tasa.

El acierto está en concordia, y está escrito en su `core/scheduler.py`: *«es un disparador, no el
mecanismo»*. Si la pasada es idempotente, perder el lazo no pierde nada —la siguiente vuelta,
venga de donde venga, encuentra lo mismo— y entonces **elegir el disparador deja de ser una
decisión que bloquee la implementación**.

## Decisión

1. **La pasada es una función en `services/`.** Idempotente, devuelve cuántas filas tocó, y no sabe
   quién la llamó. Toda la garantía vive ahí.
2. **El disparador va aparte, y pueden convivir dos** sobre la misma función: un script en
   `scripts/ops/` para cron o systemd, y el lazo del `lifespan` de la API. Un repositorio puede
   tener uno, el otro o los dos.
3. **Si hay lazo, hay candado.** `pg_try_advisory_lock` cuando la pasada es una operación global —
   el que no lo obtiene sale sin esperar ni reintentar— y `FOR UPDATE SKIP LOCKED` cuando reparte
   filas. Sin esto, el lazo multiplica el trabajo por número de workers, en silencio.
4. **`lifespan`, no `@app.on_event`**, que FastAPI dejó obsoleto. Y se espera a que la tarea termine
   al cerrar: si no, el proceso cierra la conexión con la última pasada a mitad de transacción.
5. **Una excepción nunca mata el lazo.** Un error no capturado termina la tarea y deja el proceso
   corriendo, aparentemente sano, sin volver a hacer nada nunca. Se captura, se registra y se sigue.
6. **Un interruptor y un intervalo por tarea**, y **apagado por defecto**: los tests y los scripts
   importan `app.main` y no deben quedarse con una tarea de fondo tocando la base sin pedirlo.
7. **Una sola tarea de fondo.** Lo que no hace falta en cada vuelta se cuenta por vueltas dentro de
   ella. Un segundo lazo es una segunda cosa que puede morir sin que se note.

## Consecuencias

- vettore colapsa siete lazos en uno y agrega el candado que no tiene.
- El proceso aparte de banditore encaja sin cambios: es el disparador por script del punto 2.
- Lo que hay que escribir dos veces es el andamiaje del lazo, no la pasada. Es corto y vive en un
  solo archivo por repositorio.
- El punto 6 significa que un despliegue que nunca encienda el interruptor no purga nada y no falla.
  Es el precio de que los tests no toquen la base solos; se nota en el arranque, que registra qué
  tareas quedaron activas.

## Descartado

- **Un planificador de verdad** (APScheduler, Celery). Celery necesita un broker. APScheduler no,
  pero no coordina varios procesos: su documentación advierte que compartir un almacén de tareas
  entre procesos ejecuta tareas dos veces o las pierde, que es el problema del punto 3.
- **Un lazo dentro de otro proceso de fondo que ya exista** —el enviador de avisos, por ejemplo—.
  Ata la limpieza a que ese proceso tenga sus credenciales: un despliegue sin avisos se quedaría
  también sin limpieza.
- **Borrar dentro de la petición**, aprovechando el usuario que pasa. Mete trabajo ajeno en su
  latencia y no corre si nadie entra.
- **Solo cron, sin lazo.** Es correcto, pero hace que el primer despliegue dependa de que alguien
  configure el temporizador, y hasta entonces nada se purga.
