# ADR-0164 · Lo que se instala en la máquina va en `despliegue.md`, también la unidad de una pieza

- **Estado:** Aceptada. El usuario pidió aplicar la propuesta (2026-11-16)
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/README.md`](../plataformas/README.md), «Alcance»,
  [`plataformas/java.md`](../plataformas/java.md) y
  [`plataformas/despliegue.md`](../plataformas/despliegue.md)

## Contexto

«Alcance» decía cómo se reparte una convención entre la página de una pieza y las de contrato, pero
no entre la página de una pieza y `despliegue.md`. Las páginas ya seguían un reparto: la unidad del
servidor está en `despliegue.md` y no en `fastapi.md`, y lo mismo la instalación de PostgreSQL y de
Valkey. `java.md` era la única que escribía su unidad de systemd.

## Decisión

1. **Lo que se instala en la máquina va en `despliegue.md`**, también la unidad que corre una pieza.
   La página de la pieza escribe lo que está en su carpeta del repositorio.
2. Las cinco convenciones de la unidad de una pieza en Java, y sus dos filas de «Cumplimiento»,
   pasan de `java.md` a «Procesos» de `despliegue.md`.
3. `java.md` sigue siendo una página: la pieza es código del repositorio, con su carpeta, sus
   dependencias y su compilación.
4. `despliegue.md` dice que regula cómo se publica cada versión además de cómo queda la máquina.

## Consecuencias

- `java.md` queda con «Proyecto», una convención de «Proceso» y una fila de «Cumplimiento».
- Quien trabaja en la unidad de una pieza en Java lee `despliegue.md`.

## Descartado

- **Pasar todo `java.md` a `despliegue.md`:** Caddy, coturn y Valkey son programas ajenos que solo
  se configuran, y la pieza en Java tiene código en el repositorio.
