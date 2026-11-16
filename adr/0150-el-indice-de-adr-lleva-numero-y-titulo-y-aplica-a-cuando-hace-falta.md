# ADR-0150 · El índice de ADR lleva número y título, y «Aplica a» cuando hay decisiones que tocan solo algunas piezas

- **Estado:** Aceptada
- **Fecha:** 2026-11-14
- **Alcance:** [`documentacion.md`](../documentacion.md#reglas) y el `README.md` de `adr/` de cada
  repositorio

## Contexto

La regla decía «número, título y nada más». El índice de canone llevaba además «Aplica a» y
«Estado», y los de los otros 15 repositorios usaban cinco formatos: con «Título» o «Decisión» como
segunda columna, con o sin «Estado», y parametri con «Pieza».

Comprobado el 2026-11-14 comparando las 149 filas del índice de canone con la línea «Estado» de cada
ADR: coincidían en el fondo. La 0137 decía «por 0140» sin «ADR-», y la 0116 y la 0147 iban
abreviadas. El costo de la copia era que cada reemplazo obliga a editar el estado en dos lugares.

La 0012 decía «Rechazada por ADR-0027», un estado que no está en la lista. Había sido una propuesta
que el ADR-0027 no adoptó.

## Decisión

1. **El índice lleva las columnas «#» y «Título».**
2. **Lleva además «Aplica a» cuando hay decisiones que tocan solo algunas piezas**, como en canone o en
   parametri: sirve para saber qué ADR tocan una pieza sin abrirlos.
3. **El estado no va en el índice**: está en cada ADR.
4. La 0012 pasa a «Descartada por ADR-0027».

## Consecuencias

- Reemplazar un ADR ya no toca el índice.
- Los índices de los demás repositorios no siguen esta regla hasta que se ajuste cada uno.
- Para saber si una decisión fue reemplazada hay que abrir su ADR.

## Descartado

- **Conservar «Estado» y escribir en `adr/README.md` la excepción a la regla:** deja a canone con
  una regla distinta de la de los repositorios que la siguen.
