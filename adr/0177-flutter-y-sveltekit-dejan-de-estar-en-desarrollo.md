# ADR-0177 · `flutter.md` y `sveltekit.md` dejan de estar en desarrollo

- **Estado:** Aceptada. El usuario pidió quitar la nota a las páginas que la tuvieran (2026-11-17)
- **Fecha:** 2026-11-17
- **Alcance:** [`plataformas/flutter.md`](../plataformas/flutter.md),
  [`plataformas/sveltekit.md`](../plataformas/sveltekit.md) y [`stack.md`](../stack.md)

## Decisión

1. **`flutter.md` y `sveltekit.md` se aplican a los repositorios**, y sus bloques de `stack.md`
   también.
2. **«Tema» conserva su nota** en `transversal.md` y en cada cliente: es una sección, no una
   página.

## Consecuencias

- `verificar.py --repo` exige `flutter.md` y `sveltekit.md` a los repositorios que tengan esas
  piezas. Un repositorio que todavía no las cumple falla su CI hasta adaptarse.
