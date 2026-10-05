# ADR-0033 · Un módulo propio para lo que se usa en varias partes de la app

- **Estado:** Aceptada
- **Fecha:** 2026-10-05
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md) y `plantilla/server/`

## Contexto

Las fuentes de `fastapi.md` solo ubican `main.py`, `dependencies.py` y `routers/` (*Bigger
Applications*) y `config.py` (*Settings in another module*). Los demás módulos del layout no tenían
fuente, y sus razones salían de la misma plantilla que se estaba revisando.

## Decisión

1. Lo que se usa en varias partes de la app va en su propio módulo, el criterio con el que
   *Bigger Applications* crea `dependencies.py`.
2. `errors.py` tiene la excepción de la app, las URI de los tipos de problema, el esquema `Problem`
   y los handlers, y cada proyecto lo completa. Reemplaza el punto 2 del
   [ADR-0026](0026-el-type-de-un-problema-es-un-uri-https-fijo.md).
3. `schemas/base.py` tiene solo las clases padre de los esquemas, y `schemas/page.py`, `Page[T]`.
4. Un recurso lleva el mismo nombre de archivo en `routers/`, `services/` y `schemas/`.

## Consecuencias

- `errors.py` deja de ser canónico: `scripts/verificar.py` ya no lo compara.
- `problems.py` desaparece.

## Descartado

- **Justificar un módulo por los archivos que lo usan en la plantilla:** la plantilla es lo que se
  revisa, no una fuente.
- **Agrupar los módulos en un paquete `core/`:** agrega un nivel sin fuente, y `main.py` y
  `dependencies.py` igual quedan fuera.
