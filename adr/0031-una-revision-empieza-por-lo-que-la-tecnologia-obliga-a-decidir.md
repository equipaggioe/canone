# ADR-0031 · Una revisión empieza por lo que la tecnología obliga a decidir

- **Estado:** Aceptada
- **Fecha:** 2026-10-05
- **Alcance:** `plataformas/`

## Contexto

El [ADR-0028](0028-una-pagina-esta-completa-cuando-sus-estandares-cubren-lo-que-hay-que-decidir.md)
decía que una página está completa cuando sus estándares cubren todo lo que la tecnología obliga a
decidir. Desde el [ADR-0030](0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md),
una regla propia también responde una decisión, así que una página con reglas propias parecía no
estar nunca completa.

## Decisión

Reemplaza el punto 1 del ADR-0028.

1. Una revisión empieza por la lista de lo que la tecnología obliga a decidir. Cada punto se
   responde con una fuente citada o, si ninguna lo cubre, con una regla propia.

## Consecuencias

- Una decisión que aparece después se agrega en la siguiente revisión; la página no queda
  incompleta por eso.

## Descartado

- **Quitar la regla:** la revisión volvería a mirar solo los puntos que la página ya tiene, que es
  como quedaron fuera la codificación de los archivos de texto y las advertencias de seguridad de
  `python.md`.
