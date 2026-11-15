# ADR-0151 · Una tarea con otro calendario corre en su instancia de `PRODUCTO-task@`, y la app lo declara en `TIMERS`

- **Estado:** Aceptada
- **Fecha:** 2026-11-15
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md), «Tareas periódicas»; [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Procesos»; `install.py`, `uninstall.py`, `PRODUCTO-task@.service` y `PRODUCTO-task@.timer` de `plantilla/infra/`

## Contexto

El [ADR-0043](0043-una-tarea-periodica-la-dispara-un-timer-de-systemd.md) pide un timer de systemd
por tarea, con su intervalo en `OnCalendar=`. `install.py` solo instala dos, la purga y el barrido,
los dos diarios, y no instala unidades del repositorio. Una tarea con otro calendario no tenía
dónde correr: concordia corre su alerta de citas vencidas cada minuto en un bucle de la API, y
raccolta evalúa sus alertas cada hora de la misma forma, el disparador que el ADR-0043 descarta.

## Decisión

1. **`PRODUCTO-task@.service` corre `python -m app.tasks %i`** con la cuenta del servidor y el
   mismo aislamiento que el barrido, y **`PRODUCTO-task@.timer`** la dispara.
2. **`install.py --task <tarea>=<OnCalendar>`** habilita el timer de cada tarea y escribe su
   calendario en `PRODUCTO-task@<tarea>.timer.d/calendar.conf`. Falla con una tarea que tiene unidad
   propia (`migrate`, `mock`, `purge`, `sweep`), con una tarea repetida o con un calendario que
   `systemd-analyze calendar` no lee. Una tarea que ya no nombra ningún `--task` pierde su timer, y
   sin ninguna no quedan las plantillas.
3. **La app declara el calendario en `TIMERS` de `tasks.py`**, `{tarea: OnCalendar}`: queda en el
   código junto a la tarea, y quien instala lo lee de ahí.
4. `uninstall.py` detiene y borra los timers de cada tarea.

## Consecuencias

- Una app sin `TIMERS` se instala igual que antes.
- Cada vuelta paga el arranque de un proceso de Python, como dice el ADR-0043: cada minuto, una
  tarea que importa la app entera ocupa CPU de forma continua.
- `scripts/infra/deploy.sh` lo comprueba, y `seccomp.sh` y el job `exposure` de `infra.yml` cubren
  la unidad nueva.

## Descartado

- **Una unidad por tarea escrita por el repositorio:** canone fija las unidades y su aislamiento, y
  una del repositorio podría bajarlo.
- **El calendario solo en `install.py`, sin `TIMERS`:** quedaría en la configuración de cada
  máquina y no junto a la tarea que lo necesita.
- **Un timer cada minuto para todas las tareas, que la app filtra:** cada tarea pagaría el arranque
  cada minuto aunque corra una vez al día.
