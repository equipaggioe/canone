# ADR-0064 · Una revisión da un veredicto con evidencia sobre cada regla, fuente y fila

- **Estado:** Aceptada
- **Fecha:** 2026-10-21
- **Alcance:** `plataformas/`

## Contexto

Dos revisiones de los mismos cambios en `python.md` dieron listas distintas: cada una informó solo
lo que encontró mal, recorrió la página en otro orden y afirmó de memoria lo que marca una
herramienta. Las dos encontraron además problemas que ningún criterio escrito nombraba: una fila
cuya herramienta cubría solo parte de lo que decía, y dos reglas de Async que se contradecían.

## Decisión

1. Una revisión da un veredicto sobre cada fuente citada, cada regla y cada fila de «Cómo se hace
   cumplir», contra los criterios de `plataformas/README.md`.
2. Cada veredicto lleva su evidencia: comprobado, con el comando que lo reproduce; leído, con la
   línea de la fuente, o sin confirmar. Lo que marca una herramienta se comprueba con un
   experimento.
3. Dos reglas de una página no chocan: una que deja casos fuera de otra los nombra.
4. Las herramientas de una fila hacen cumplir todo lo que nombra su primera columna.

## Consecuencias

- Dos revisiones de la misma página recorren lo mismo, y lo que no se evaluó se ve.
- Revisar lleva más tiempo: cada veredicto necesita su evidencia o queda sin confirmar.

## Descartado

- **Informar solo los hallazgos:** lo que no se miró no se distingue de lo que está bien.
