# ADR-0026 · El `type` de un problema es un URI `https` fijo, y la validación tiene su propio tipo

- **Estado:** Aceptada
- **Fecha:** 2026-10-01
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md),
  `plantilla/server/src/app/problems.py` y `errors.py`, y todo cliente que lea errores de la API

## Contexto

El [ADR-0015](0015-el-sobre-de-error-sigue-el-rfc-9457.md) fijó `type` como
`tag:<dominio>,<año>:<nombre>` y descartó un URI `https` porque «el dominio cambia entre entornos».
Esa objeción vale para un URI armado con el host de cada entorno, no para un identificador fijo.

RFC 9457 §3.1.1 advierte que pasar de un `tag:` a un URI resoluble «would require switching to a
resolvable URI, creating a new identity for the problem type and thus introducing a breaking
change», y §4 pide que el URI de un tipo resuelva a su documentación.

El 422 de validación salía como `about:blank` con la extensión `errors`. Según §4.2.1, `about:blank`
no tiene más semántica que su código HTTP, y según §3.2 las extensiones las define cada tipo.

## Decisión

1. `type` es `https://<dominio>/problems/<nombre>`, con el mismo dominio en todos los entornos.
   Reemplaza el punto 3 del ADR-0015.
2. La base y cada tipo viven en `problems.py`, un módulo propio de cada sistema; `errors.py` sigue
   siendo canónico.
3. Un error de validación es de tipo `https://<dominio>/problems/validation`.

## Consecuencias

- Mientras no se sirva la documentación, la página contradice el SHOULD de §4. Se puede servir
  después sin cambiar ningún `type`.
- En desarrollo, el `type` apunta al dominio de producción. Los clientes no lo resuelven: §3.1.1
  dice que no deben hacerlo de forma automática.

## Descartado

- **Seguir con `tag:`:** documentar los tipos más adelante cambiaría la identidad de cada uno.
- **Tomar el dominio de `Settings`:** cambiaría entre entornos, y el cliente compara el `type`.
