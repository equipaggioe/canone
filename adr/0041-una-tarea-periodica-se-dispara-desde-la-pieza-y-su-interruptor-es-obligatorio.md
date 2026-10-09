# ADR-0041 · Una tarea periódica se dispara desde la pieza, y su interruptor es un campo obligatorio

- **Estado:** Aceptada
- **Fecha:** 2026-10-08
- **Alcance:** la sección «Tareas periódicas» de [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

El [ADR-0011](0011-la-pasada-es-una-funcion-y-el-disparador-va-aparte.md) ponía el script que
dispara una tarea en `scripts/ops/`, la dejaba apagada por defecto, juntaba todas en una sola tarea de
fondo y esperaba a que la pasada terminara al apagar el servidor. [`repositorio.md`](../repositorio.md) deja en `scripts/` solo lo del repositorio entero, y
`fastapi.md` no da valores por defecto a ningún campo de `Settings`.

## Decisión

Reemplaza el script del punto 2, la espera del punto 4, el «apagado por defecto» del punto 6 y el
punto 7 del ADR-0011.

1. El script es `python -m app.tasks`, dentro de la pieza.
2. El interruptor y el intervalo de cada tarea son campos obligatorios de `Settings`.
3. Al apagar el servidor, la tarea se cancela sin esperar a que termine la pasada.

## Consecuencias

- Las pruebas apagan las tareas en su entorno, como fijan cualquier otro campo de `Settings`.
- `tasks.py` entra al árbol de `fastapi.md`.
- Una pasada cortada hace *rollback*, y la repite la vuelta siguiente. Una tarea que envía algo
  fuera de la base puede repetir lo que envió antes del corte.

## Descartado

- **Un script en `scripts/ops/`:** `scripts/` es del repositorio entero.
- **Apagado por defecto:** sería el único campo de `Settings` con valor por defecto.
- **Una sola tarea de fondo:** es una preferencia sin síntoma que la pida.
- **Esperar a que termine la pasada:** alarga el apagado, y si pasa el límite de systemd el proceso
  muere igual.
