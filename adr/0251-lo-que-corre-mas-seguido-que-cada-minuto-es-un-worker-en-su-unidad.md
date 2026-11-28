# ADR-0251 · Lo que corre más seguido que cada minuto es un worker, en su unidad

- **Estado:** Aceptada el 2026-11-19 por el desarrollador, en el plan de despliegue de equipaggio:
  el tipo de proceso *worker*, `WORKERS` en `tasks.py`, la unidad `<app>-worker@<tarea>` con la
  cuenta y las credenciales del servidor, `install.py --worker`, que `deploy.py` la reinicia antes
  que el servidor y `uninstall.py` la borra, y la cola con `FOR UPDATE SKIP LOCKED`.
- **Fecha:** 2026-11-27
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md), «Tareas»;
  [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Procesos», «PostgreSQL» y
  «Desinstalar»; `tasks.py` y `test_tasks.py` de `plantilla/server/`; `install.py`, `deploy.py`,
  `database.py`, `uninstall.py` y `PRODUCTO-worker@.service` de `plantilla/infra/`

## Contexto

El [ADR-0043](0043-una-tarea-periodica-la-dispara-un-timer-de-systemd.md) deja cada tarea periódica
en un timer de systemd, y cada vuelta paga el arranque de un proceso de Python. Equipaggio tiene
cuatro procesos que corren sin parar: el correo y los webhooks cada segundo, el sondeo cada 30 s y
el reparto de los SMS a los teléfonos. Con un timer, un proceso nuevo por segundo; sin una unidad de
Canone, quien despliega tendría que escribirla, y el README dice que no la escribe. Cada uno tomaba
un `pg_try_advisory_lock` para no correr dos veces.

12-Factor, «Concurrency», separa los tipos de proceso, como el web y el *worker*, y deja que el
gestor de procesos del sistema los corra y los reinicie.

## Decisión

Reemplaza el punto 3 del ADR-0043 para lo que corre más seguido que cada minuto.

1. Lo que corre más seguido que cada minuto es un *worker*: declara en `WORKERS` de `tasks.py` los
   segundos entre sus vueltas, como `{"mailer": 1}`, y `python -m app.tasks <tarea>` lo corre sin
   fin. La vuelta es una función de `services/`, como una tarea.
2. Una vuelta que falla va al log, y el worker sigue con la siguiente.
3. El worker corre en `<app>-worker@<tarea>.service`, con la cuenta y las credenciales del
   servidor. `install.py --worker <tarea>` la habilita, `deploy.py` la reinicia antes que el
   servidor y `uninstall.py` la borra.
4. Un worker corre en una sola copia, la de su unidad, y no lleva candado.
5. Un worker que toma filas de una cola las toma con `FOR UPDATE SKIP LOCKED`.

Al implementar se eligió *(propuesta)*:

6. `install.py --worker` arranca el worker si ya hay una versión activa, y si no lo deja para
   `deploy.py`. Un worker que ningún `--worker` nombra pierde su unidad, y uno con unidad propia, o
   también en `--task` o `--browser`, hace fallar `install.py`.
7. `deploy.py` detiene los workers con el servidor antes de migrar, `database.py empty` los detiene
   con el servidor, y `uninstall.py database` los detiene con el servidor y los timers.
8. La unidad lleva `Restart=on-failure`, como la del servidor: el worker no termina solo, y uno que
   cae por un error al arrancar vuelve a intentarlo.

## Consecuencias

- Cada vuelta deja de pagar el arranque de Python, y un proceso que corre cada segundo no queda en
  manos de quien despliega.
- Sale el candado de cada proceso: systemd no arranca una segunda copia de la unidad.
- Con `FOR UPDATE SKIP LOCKED`, una vuelta no espera la fila que otra transacción tiene tomada, y
  una copia lanzada a mano no toma las mismas filas.
- El código anterior no corre sobre la base migrada, ni en el servidor ni en un worker.
- Un worker que se cae lo reinicia systemd, y uno que pierde la base registra cada vuelta fallida
  hasta que vuelve.
- Consola pasa `--worker` a `install.py` por cada tarea de `WORKERS`, como pasa `--task` por cada
  una de `TIMERS`.

## Descartado

- **Un timer por segundo:** un proceso de Python por vuelta, y systemd no baja de su
  `AccuracySec=` de un minuto por defecto sin que cada timer lo pida.
- **Un lazo en el `lifespan` del servidor:** corre en cada worker de Uvicorn y pide un candado, como
  descartó el ADR-0043.
- **Una unidad propia en cada repositorio:** quien despliega no escribe unidades (README,
  «Responsabilidades»).
- **Mantener el `pg_try_advisory_lock`:** cuida lo que la unidad ya cuida, y un segundo proceso que
  no lo toma sale con error en vez de esperar.
