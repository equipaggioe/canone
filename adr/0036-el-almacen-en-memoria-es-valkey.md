# ADR-0036 · El almacén en memoria de todas las piezas es Valkey

- **Estado:** Aceptada
- **Fecha:** 2026-10-07
- **Alcance:** [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

fastapi.md guardaba en Redis la caché de Nominatim, los contadores del límite de tasa y el pub/sub
del WebSocket. Se quiere un solo almacén en memoria para todos los usos que puedan aparecer: caché,
límites, sesiones, pub/sub, colas de tareas, candados, streams, JSON y búsqueda.

## Decisión

El almacén en memoria es Valkey, el mismo para todos los usos.

## Consecuencias

- Valkey es una copia de Redis 7.2: los comandos, Lua y las bibliotecas escritas para Redis
  funcionan sin ajustes.
- Licencia BSD, mantenido por la Linux Foundation.

## Descartado

- **Dragonfly:** usa todos los núcleos, ocupa menos memoria y guarda en disco sin duplicar la
  memoria, pero un script de Lua tiene que declarar sus llaves. Las colas que usan Lua sin
  declararlas, como BullMQ, piden opciones propias, o cada script bloquea todo el almacén. Su
  ventaja aparece cuando una instancia necesita muchos núcleos o mucha memoria. Licencia BSL hasta
  2030.
- **Redis:** cambió de licencia en 2024 (RSAL y SSPL) y otra vez en 2025, cuando agregó AGPL.
  Valkey nació de esa bifurcación, con licencia BSD y gobernado por una fundación.
