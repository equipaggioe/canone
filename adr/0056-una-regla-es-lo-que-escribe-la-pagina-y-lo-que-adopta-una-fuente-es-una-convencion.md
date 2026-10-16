# ADR-0056 · Una regla es lo que escribe la página, y lo que adopta una fuente es una convención

- **Estado:** Aceptada
- **Fecha:** 2026-10-16
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

`plataformas/README.md` llamaba «regla» tanto a lo que dice una fuente como a lo que escribe la
página, y «regla propia» unas veces a todo lo que escribe la página y otras solo a lo que no se
apoya en una fuente. La carpeta `estandares/` guardaba también guías y especificaciones que no son
estándares.

## Decisión

1. Una convención es lo que se cumple: la adopta una fuente citada o la escribe la página como
   regla.
2. Una regla es solo lo que escribe la página. Lo que dice una fuente es una convención.
3. Una regla propia es la que no se apoya en ninguna fuente citada.
4. Elegir una fuente de mayor número en un asunto que otra de menor número ya cubre es una regla
   propia. Reemplaza el punto 4 del
   [ADR-0030](0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md).
5. Un estándar es una clase de fuente, la de los órdenes 1 y 2. La carpeta con las copias de las
   fuentes citadas se llama `fuentes/`.
6. Lo que la página deja sin efecto de una fuente lleva razón, como lo que contradice o endurece.
   Reemplaza en eso el punto 6 del
   [ADR-0018](0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md).

## Consecuencias

- Cada término nombra una sola cosa en `plataformas/README.md`. Las páginas se revisan con estos
  términos.
- Los enlaces a `estandares/` pasan a `fuentes/` en las páginas y en los ADR. Los títulos de los ADR
  viejos siguen diciendo «estándares».

## Descartado

- **Conservar `estandares/`:** el nombre decía que la carpeta guarda solo estándares.
