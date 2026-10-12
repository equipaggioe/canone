# ADR-0043 · Una tarea periódica la dispara un timer de systemd

- **Estado:** Aceptada
- **Fecha:** 2026-10-10
- **Alcance:** la sección «Tareas periódicas» de [`plataformas/fastapi.md`](../plataformas/fastapi.md)
  y la sección «Procesos» de [`plataformas/despliegue.md`](../plataformas/despliegue.md)

## Contexto

El [ADR-0011](0011-la-pasada-es-una-funcion-y-el-disparador-va-aparte.md) ponía la pasada en una
función de `services/` y dejaba dos disparadores sobre ella: un script y el lazo del `lifespan`,
uno, el otro o los dos. El lazo llevaba un candado de Postgres, una captura de excepciones y un
interruptor con su intervalo. El [ADR-0041](0041-una-tarea-periodica-se-dispara-desde-la-pieza-y-su-interruptor-es-obligatorio.md)
llevó el script a `python -m app.tasks`, volvió obligatorios el interruptor y el intervalo en
`Settings`, y cancelaba la tarea al apagar el servidor.

Cuatro de esas reglas existían solo por el lazo. Y con los dos disparadores, el intervalo vivía en
`Settings` y en la unidad del timer.

## Decisión

Reemplaza el ADR-0011 y el ADR-0041.

1. Una tarea periódica es una función en `services/`.
2. La tarea trabaja sobre lo que encuentra en la base, no sobre lo que pasó desde la vuelta
   anterior.
3. La dispara un timer de systemd por tarea, con `python -m app.tasks <tarea>`.

## Consecuencias

- No hay candado: systemd no arranca una vuelta si la anterior sigue corriendo.
- No hay interruptor ni intervalo en `Settings`: se activa o se desactiva el timer, y el intervalo
  es su `OnCalendar=`. Las pruebas no tienen tareas que apagar.
- No hay nada que cancelar al apagar el servidor.
- En desarrollo ninguna tarea corre sola: se lanza a mano.
- Cada vuelta paga el arranque de un proceso de Python.

## Descartado

- **El lazo del `lifespan`:** corre en cada worker y pide un candado, un error no capturado lo mata
  con el proceso vivo, y obliga a un interruptor en `Settings` y a cancelarlo al apagar. El ADR-0011
  lo prefería porque sin él el primer despliegue dependía de configurar el timer; despliegue.md ya
  instala las unidades de systemd desde el primer despliegue.
- **El lazo y el timer juntos:** los dos disparadores se pisan y el intervalo vive en dos sitios.
- **pg_cron:** corre solo SQL. Una tarea que envía algo fuera de la base queda afuera, y la lógica
  se parte entre la base y `services/`.
- **Un planificador (APScheduler, Celery beat, arq):** suma una dependencia y un proceso para lo que
  systemd ya hace.
- **Que la tarea devuelva cuántas filas tocó:** nadie usa el número.
