# ADR-0123 · `deploy.py` vuelve a una versión guardada con sus mismas migraciones, y borra la nueva que no arrancó

- **Estado:** Aceptada
- **Fecha:** 2026-11-06
- **Alcance:** «Versiones» de [plataformas/despliegue.md](../plataformas/despliegue.md),
  `plantilla/infra/deploy.py` y `scripts/infra/deploy.sh`

## Contexto

`deploy.py` fallaba con `already exists` ante cualquier versión que siguiera en `releases/`. Guardaba
cinco versiones, pero no servía para volver a ninguna: ante una versión mala había que publicar otra.
Una versión nueva que no respondía a la salud dejaba `current` en la anterior y su carpeta en
`releases/`, así que el mismo tag no se podía volver a desplegar. Lo vio Consola el 2026-11-02 en un
VPS de prueba.

## Decisión

1. `deploy.py <tag>` con una versión que `releases/` guarda la vuelve a activar sin instalarla, si sus
   heads de Alembic son los de la activa. Si no lo son, falla sin cambiar nada.
2. Al volver, baja otra vez del release los instalables de esa versión y los comprueba con su `.sha256`
   firmado: al publicarlos salen de la carpeta de la versión.
3. Si la versión a la que se vuelve no responde a la salud, `current` vuelve a la que estaba activa.
4. La versión activa no se vuelve a instalar.
5. Una versión nueva que no responde a la salud y no trajo migraciones se borra después de volver a la
   anterior.

## Consecuencias

- Volver atrás es el mismo comando que desplegar, y Consola no cambia para usarlo.
- Volver con instalables pide que GitHub responda, como desplegar.
- No se vuelve a una versión de otras migraciones: para eso hay que publicar una versión nueva.

## Descartado

- **Un comando aparte para volver (`--back`):** la intención es la misma, que corra ese tag, y el
  comando no puede confundirse porque la carpeta dice si la versión está guardada.
- **Copiar los instalables en vez de moverlos al publicar:** ocupa el disco de cada versión guardada
  para un caso que ya cubre volver a bajarlos con la firma.
- **Volver también a una versión de otras migraciones:** su código correría sobre un esquema que no
  conoce, lo mismo que descarta el [ADR-0068](0068-una-version-se-despliega-desde-un-tag-con-un-artefacto-y-un-script.md).
