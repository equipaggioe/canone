# ADR-0115 · Lo que se cumple es una convención, adoptada de una fuente o propia de Canone

- **Estado:** Aceptada
- **Fecha:** 2026-11-03
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

El [ADR-0056](0056-una-regla-es-lo-que-escribe-la-pagina-y-lo-que-adopta-una-fuente-es-una-convencion.md)
llamaba «convención» a lo que se cumple, «regla» a lo que escribe la página y «regla propia» a lo
que no se apoya en ninguna fuente citada. El commit 4f406e1, del 2026-11-02, reescribió
`plataformas/README.md` con otros términos sin registrar la decisión en un ADR; este la registra.
Las definiciones están en «Terminología» de ese archivo.

## Decisión

1. Lo que se cumple es una convención: adoptada, si la establece una fuente citada, o propia, si la
   establece Canone. Reemplaza el punto 1 del ADR-0056.
2. «Regla» deja de ser un término de `plataformas/README.md`: lo que escribe la página es una
   convención propia. Reemplaza el punto 2 del ADR-0056.
3. Una convención propia es tanto la que resuelve lo que ninguna fuente citada cubre como la que
   elige entre las opciones de una fuente o la modifica. Reemplaza el punto 3 del ADR-0056.

## Consecuencias

- Una sola palabra nombra lo que se cumple, y el adjetivo dice de dónde sale.
- «Propia» ya no nombra solo lo que no se apoya en una fuente. Para eso,
  `plataformas/README.md` habla de decisiones no cubiertas.
- Los ADR anteriores y sus títulos conservan «regla» y «regla propia».

## Descartado

- **Conservar «regla» para lo que escribe la página:** hacían falta dos palabras para lo que se
  cumple, y «regla propia» no nombraba todo lo que escribe la página.
