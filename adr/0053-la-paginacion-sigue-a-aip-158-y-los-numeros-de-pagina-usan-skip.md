# ADR-0053 · La paginación sigue a AIP-158, y los números de página usan `skip`

- **Estado:** Aceptada
- **Fecha:** 2026-10-15
- **Alcance:** la sección «Paginación» de [plataformas/fastapi.md](../plataformas/fastapi.md#paginación)
  y de [plataformas/transversal.md](../plataformas/transversal.md#paginación); el servidor y sus
  clientes

## Contexto

El [ADR-0034](0034-la-paginacion-es-por-cursor-con-reglas-propias.md) hizo de la paginación reglas
propias, con `limit`, `cursor` y `nextCursor`, y descartó AIP-158 por estar escrita para proto. El
[ADR-0035](0035-una-lista-con-numeros-de-pagina-se-pagina-por-page-y-devuelve-el-total.md) sumó un
segundo modo, con `page` y `total`. Ninguna fuente general de un organismo oficial cubre la
paginación de una API HTTP, y los campos de AIP-158 pasan a JSON sin cambios.

## Decisión

1. La fuente es AIP-158, y el contrato va en `transversal.md`.
2. `pageSize` vale 50 por defecto y 100 como máximo.
3. La respuesta es `{"items", "nextPageToken"}`, con `nextPageToken` siempre presente y `""` en la
   última página.
4. Una lista que muestra números de página acepta `skip` y devuelve `totalSize`. Las demás no.
5. Con `skip`, un `pageSize` mayor que 100 responde 422.
6. El token se cifra con Fernet y la clave `PAGE_TOKEN_KEY`.
7. Un `pageToken` ilegible o con otros parámetros responde 422 de tipo `validation`, con
   `parameter: "pageToken"`.

## Consecuencias

- Reemplaza el ADR-0034 y el ADR-0035: hay un solo modo, y las clases son `PageParams`,
  `SkipParams`, `Page[T]` y `CountedPage[T]`.
- El servidor suma `cryptography`, que `webauthn` ya exige, y el secreto `PAGE_TOKEN_KEY`. Cambiar
  la clave invalida los tokens en uso.
- Un `pageSize` mayor que 100 sin `skip` se recorta, como pide AIP-158: el cliente sigue
  `nextPageToken` y no pierde filas.

## Descartado

- **RFC 9865:** pagina por cursor, pero solo para SCIM.
- **OData:** la página siguiente es una URL, que un cliente generado no tipa.
- **El perfil de cursor de JSON:API:** exige el formato de documento de JSON:API.
- **`limit`, `cursor` y `nextCursor`:** apartarse de los nombres de AIP-158 obliga a escribir una
  contradicción, y su única razón sería que son comunes.
- **Nombrar la lista por el recurso:** no hay un `Page[T]` genérico, y cada cliente necesita un
  adaptador por lista.
- **El modo numerado con `page`:** AIP-158 ya da `skip` y `totalSize`, y la URL que se comparte es
  la de la web, no la de la API.
- **Recortar también con `skip`:** el cliente calcula `skip` con el tamaño que pidió, y un recorte
  se saltaría filas sin aviso.
- **base64url:** AIP-158 no lo da por suficiente.
- **PyJWT:** firma pero no cifra.
- **Guardar el estado en Valkey:** un viaje a Valkey por página y tokens que vencen.
