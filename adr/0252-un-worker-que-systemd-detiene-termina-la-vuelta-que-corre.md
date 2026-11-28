# ADR-0252 · Un worker que systemd detiene termina la vuelta que corre

- **Estado:** Aceptada el 2026-11-27 por el desarrollador, al revisar el ADR-0251
- **Fecha:** 2026-11-27
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md), «Tareas»; `tasks.py` y
  `test_tasks.py` de `plantilla/server/`

## Contexto

`deploy.py` reinicia cada worker del
[ADR-0251](0251-lo-que-corre-mas-seguido-que-cada-minuto-es-un-worker-en-su-unidad.md) en cada
versión, y systemd lo detiene con `SIGTERM`. Sin un handler, Python termina en el acto: comprobado
con Python 3.13.5 en Debian 13, el proceso sale con 143 y no corre el `finally` que cierra el pool de la
base y el cliente de Web Push. La vuelta queda cortada donde esté.

## Decisión

1. Un worker que recibe `SIGTERM` termina la vuelta que corre, no empieza otra y sale, con sus
   conexiones cerradas.

## Consecuencias

- Un despliegue no corta una vuelta entre lo que hace fuera de la base, como enviar un correo, y su
  commit.
- El worker sale con 0, y `Restart=on-failure` no lo vuelve a arrancar.
- Una vuelta que pasa de `TimeoutStopSec=`, 90 s por defecto, la mata systemd igual.

## Descartado

- **Dejar que `SIGTERM` termine el proceso:** corta la vuelta a medias en cada despliegue.
- **`loop.add_signal_handler`:** asyncio no lo tiene en Windows, y las pruebas del worker no
  correrían en la máquina de quien desarrolla.
