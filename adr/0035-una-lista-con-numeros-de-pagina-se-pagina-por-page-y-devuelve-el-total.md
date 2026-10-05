# ADR-0035 · Una lista con números de página se pagina por `page` y devuelve el total

- **Estado:** Aceptada
- **Fecha:** 2026-10-05
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md) y sus clientes

## Contexto

El [ADR-0034](0034-la-paginacion-es-por-cursor-con-reglas-propias.md) dejó solo la paginación por
cursor. Un catálogo, unos resultados de búsqueda o una tabla de administración muestran números de
página: saltan a la página 7, dicen «página 3 de 12» y se comparten como `?page=3`. Nada de eso se
puede armar en el cliente con un cursor.

## Decisión

Reemplaza el punto 1 del ADR-0034.

1. Hay dos modos, y una ruta tiene uno solo:
   - Por cursor, el modo por defecto: `limit` y `cursor`, y `{"items", "nextCursor"}` sin total.
   - Numerado, para una lista que muestra números de página: `limit` y `page`, y
     `{"items", "total"}`.
2. `limit` vale 50 por defecto y 100 como máximo en los dos modos.

## Consecuencias

- Una página numerada salta o repite filas si la lista cambia, y su total cuenta el conjunto
  filtrado en cada petición. En un catálogo pesa poco: cambia poco entre una página y otra.

## Descartado

- **Numerar en el cliente con los cursores ya recibidos:** no salta a una página no visitada ni
  conoce el total.
- **`offset` en vez de `page`:** `?page=3` es la dirección que se comparte.
- **20 por defecto:** en una pantalla alta de escritorio, apenas pasa de una pantalla.
