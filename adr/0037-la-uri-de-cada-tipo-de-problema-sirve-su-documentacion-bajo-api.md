# ADR-0037 · La URI de cada tipo de problema sirve su documentación, bajo `/api`

- **Estado:** Aceptada
- **Fecha:** 2026-10-07
- **Alcance:** [`plataformas/transversal.md`](../plataformas/transversal.md),
  [`plataformas/fastapi.md`](../plataformas/fastapi.md), `plantilla/server/src/app/errors.py` y
  `routers/problems.py`, y todo cliente que lea errores de la API

## Contexto

El [ADR-0026](0026-el-type-de-un-problema-es-un-uri-https-fijo.md) fijó `type` como
`https://<dominio>/problems/<nombre>` y dejó la documentación sin servir, contradiciendo el SHOULD
de RFC 9457 §4 «mientras no se sirva». La página no tenía una razón propia para contradecirlo.

La API se sirve en el mismo origen que la web, bajo `/api`: una ruta `/problems/` la atendería la
web.

## Decisión

1. `type` es `https://<dominio>/api/problems/<nombre>`, con el mismo dominio en todos los entornos.
   Reemplaza el punto 1 del ADR-0026.
2. El servidor sirve en esa URI una página HTML con el título del tipo, su código y cómo se
   resuelve.
3. Cada tipo se define una sola vez en `errors.py`, con su `title`, su `status` y cómo se resuelve.
   `AppError` recibe el tipo.
4. *(propuesta)* La ruta vive en `routers/problems.py`, fuera del esquema de OpenAPI.

## Consecuencias

- La página sigue RFC 9457 sin contradecirlo.
- Un tipo nuevo se agrega en `errors.py`, y su página sale de esa misma definición.
- En desarrollo, el `type` apunta al dominio de producción.

## Descartado

- **No servir la documentación:** no había razón propia para contradecir el RFC.
- **`/problems/` sin `/api`:** esa ruta la atiende la web.
