# ADR-0068 · Una versión se despliega desde un tag, con un artefacto y un script

- **Estado:** Aceptada
- **Fecha:** 2026-10-22
- **Alcance:** la sección «Versiones» de [`plataformas/despliegue.md`](../plataformas/despliegue.md)

## Contexto

`despliegue.md` decía cómo queda el servidor, pero no cómo llega una versión a él. Tampoco había
dónde viviera una versión nueva de la web, de la landing o de un instalable, y
[`repositorio.md`](../repositorio.md) decía que el repositorio no traía scripts de despliegue.

## Decisión

1. Se despliega un tag. El CI construye un artefacto con el servidor y el build de cada superficie
   web, y lo publica en un release de GitHub con su SHA-256.
2. Cada versión queda en `releases/<versión>/` y el enlace `current` apunta a la activa. Los datos
   quedan fuera, en `/var/lib/<app>/`.
3. Un script, `scripts/deploy.py`, instala la versión en el servidor, y una persona lo lanza por
   `ssh`.
4. Si `GET /api/health` falla, `current` vuelve a la versión anterior. El rollback no deshace
   migraciones.
5. Caddy sirve cada superficie web desde `current/<pieza>/`. La PWA es `web/`.
6. Los instalables de `desktop/` se adjuntan al mismo release y `deploy` los copia a `downloads/`
   con un nombre fijo por sistema.

## Consecuencias

- La web, el servidor y los instalables de una versión salen de un solo tag.
- Tras una migración que no sirve al código anterior, el rollback deja el código viejo sobre la
  base nueva.
- Los instalables de `mobile/` quedan fuera: dependen de las tiendas y de la firma.

## Descartado

- **Desplegar desde Actions por `ssh`:** GitHub guardaría una llave con acceso al servidor.
- **Un timer en el servidor que consulta los releases:** agrega una pieza y retrasa el despliegue.
