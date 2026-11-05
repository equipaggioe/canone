# ADR-0121 · Una fuente citada solo en algunas secciones se marca «por partes»

- **Estado:** Aceptada
- **Fecha:** 2026-11-05
- **Alcance:** `plataformas/README.md`, `fuentes/README.md` y `scripts/verificar.py`

## Contexto

El [ADR-0108](0108-una-fuente-se-cita-entera-o-por-entradas-y-cada-parte-rige-en-una-sola-seccion.md)
deja dos valores para la columna «Cita», y 18 fuentes decían `entera` aunque las páginas solo citan
algunas de sus secciones. Si una cita perdía el nombre de su parte, pasaba a abarcar toda la fuente sin
que `verificar.py` avisara.

## Decisión

1. La columna «Cita» agrega el valor `por partes`: se adoptan únicamente las partes nombradas.
2. `verificar.py` falla si una cita de una fuente `por partes` no nombra sus partes, y si una fuente
   `entera` no tiene ninguna cita de la fuente entera.

## Consecuencias

- Las 18 fuentes cambian de valor, y sus citas siguen iguales.
- Una parte sigue rigiendo en una sola sección, como en una fuente entera.

## Descartado

- **Conservar `entera` para estas fuentes:** la columna diría más de lo que se adopta.
- **Fecha de descarga en las páginas web sin versión:** muestra la antigüedad de la copia, pero no evita
  que se desactualice.
