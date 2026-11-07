# ADR-0125 · Un `numeric` va sin precisión ni escala

- **Estado:** Aceptada
- **Fecha:** 2026-11-06
- **Alcance:** [plataformas/postgres.md](../plataformas/postgres.md) y
  `plantilla/server/tests/test_conventions.py`

## Contexto

El [ADR-0023](0023-un-monto-se-guarda-como-numeric-sin-escala-y-sus-decimales-los-decide-cada-repositorio.md)
dejaba sin precisión ni escala solo los montos. Una prueba no puede saber qué columna guarda un monto,
y la razón, que *Arbitrary Precision Numbers* redondea al guardar lo que excede la escala declarada,
vale para cualquier `numeric`.

## Decisión

1. Toda columna `numeric` va sin precisión ni escala.

## Consecuencias

- Ningún `numeric` redondea al guardar.
- `test_numerics_are_unscaled` lo comprueba en todas las columnas.

## Descartado

- **Solo los montos, sin prueba:** la regla queda sin herramienta, y la misma pérdida silenciosa
  sigue posible en cualquier otro `numeric`.
