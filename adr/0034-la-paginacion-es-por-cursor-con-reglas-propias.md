# ADR-0034 · La paginación es por cursor, con reglas propias

- **Estado:** Aceptada. El punto 1 lo reemplaza el [ADR-0035](0035-una-lista-con-numeros-de-pagina-se-pagina-por-page-y-devuelve-el-total.md)
- **Fecha:** 2026-10-05
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md) y sus clientes

## Contexto

Ningún estándar de los órdenes 1 a 3 cubre la paginación de una API REST. RFC 8288 solo define cómo
se expresa el enlace `next`. Las guías de Zalando y la AIP-158 de Google la cubren, y las listas de
las apps se recorren casi siempre con scroll infinito.

## Decisión

1. La paginación son reglas propias: por cursor, con `limit` y `cursor` en la petición y
   `{"items", "nextCursor"}` en la respuesta. Las reglas completas están en `fastapi.md`.

## Descartado

- **El capítulo de paginación de Zalando:** le faltan el `limit` por defecto y máximo y el error
  ante un cursor inválido, y su regla #161 pide enlaces donde la página usa cursores.
- **AIP-158:** está escrita para APIs definidas en proto, que llegan a HTTP/JSON por transcodificación.
- **RFC 8288 con reglas propias:** cubre una sola de las decisiones, y un cliente generado desde
  OpenAPI no lee la cabecera `Link`.
