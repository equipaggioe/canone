# ADR-0149 · Las unidades que corren la app permiten `mbind`, la llamada con que el OpenBLAS de numpy fija la memoria de sus hilos

- **Estado:** Aceptada
- **Fecha:** 2026-11-14
- **Alcance:** [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Procesos»; `PRODUCTO.service`, `PRODUCTO-migrate@.service`, `PRODUCTO-mock@.service`, `PRODUCTO-purge.service` y `PRODUCTO-sweep.service` de `plantilla/infra/`

## Contexto

Al instalar concordia el 2026-11-14 en un Debian 13 (systemd 257), `concordia.service` moría con
`SIGSYS` al arrancar, y `deploy.py` no veía `GET /api/health`. El kernel registró `syscall=237`,
`mbind`, del grupo `@resources` que la unidad niega. La llama el OpenBLAS de la rueda de numpy
2.5.4 al importarse: con el filtro de la unidad, `import numpy` muere, y también `cv2`,
`onnxruntime`, `scipy` e `imagehash`, que lo importan. Pillow sí importa. Con `mbind` permitida,
importan los cinco, y `systemd-analyze security` da 1.2 en vez de 1.1.

## Decisión

1. **Cada unidad que corre Python de la app** agrega `SystemCallFilter=mbind` después de
   `SystemCallFilter=~@privileged @resources`: solo esa llamada vuelve, y el resto de `@resources`
   sigue negado.
2. **`scripts/infra/seccomp.sh` lo comprueba** en el job `seccomp` de `infra.yml`: numpy importa con
   el filtro de cada unidad, y sin la excepción no importa.

## Consecuencias

- Una app con numpy corre en la máquina sin cambiar su unidad.
- `mbind` solo cambia la política de memoria NUMA del propio proceso.

## Descartado

- **`SystemCallErrorNumber=EPERM`**, que devuelve un error en vez de matar: una llamada negada
  fallaría en silencio en cualquier biblioteca, y canone pide que falle ruidosamente.
- **Sacar `@resources` del filtro.** Vuelven también `setrlimit`, `sched_setscheduler` y el resto
  del grupo, que la app no usa.
