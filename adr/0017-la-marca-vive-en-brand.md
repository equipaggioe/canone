# ADR-0017 · El logo y los colores del producto viven en `brand/`

- **Estado:** Aceptada
- **Fecha:** 2026-09-27
- **Alcance:** todos los repositorios; `repositorio.md` y `scripts/verificar.py`

## Contexto

`banditore`, `cassetti`, `equipaggio` y `vettore` tienen una carpeta `brand/` con el logo y los
colores, y `verificar.py` falla en los cuatro con «`brand/` no es un nombre de pieza». La regla de
nombres es para piezas, y `brand/` no lo es: no corre en ningún lado, la leen la landing, la web y
las apps.

## Decisión

1. `brand/` es una carpeta fija del primer nivel, como `docs/` y `scripts/`.
2. Guarda el logo y los colores del producto, y nada que se ejecute.

## Consecuencias

- `verificar.py` deja de marcar `brand/` en los cuatro repositorios.
- Qué archivos lleva `brand/` no se fija aquí: cada repositorio tiene los suyos.

## Descartado

- **Mover el logo a `packages/brand/`:** `packages/` es código instalable, y un logo no se instala.
- **Copiarlo dentro de cada pieza:** una copia por pieza es una fuente de verdad por pieza.
