# ADR-0116 · La sección «Tema» está en desarrollo y no se implementa

- **Estado:** Aceptada, salvo el punto 2, que sigue en propuesta
- **Fecha:** 2026-11-03
- **Alcance:** «Tema» de [plataformas/transversal.md](../plataformas/transversal.md#tema) y de cada cliente, [plantilla/README.md](../plantilla/README.md) y `scripts/verificar.py`

## Contexto

`transversal.md` ya decía que la sección estaba en desarrollo y que ningún producto la usaba, pero `verificar.py` exigía `tests/test_theme.py` en toda pieza de PySide6 o de Flet, y esa prueba exige la sección. Quien llevaba un repositorio a Canone tenía que implementar algo todavía en revisión.

## Decisión

1. **La sección «Tema» está en desarrollo y no se implementa.** Ningún repositorio la sigue mientras la nota esté en `transversal.md`, y no seguirla no es una desviación ni lleva ADR propio.
2. *(propuesta)* **`verificar.py` no exige nada de ella.** Sale `CANONICOS_PIEZA`, cuya única entrada por pieza era `tests/test_theme.py`, y las filas de esa prueba en «Cumplimiento» de `qt.md` y `flet.md`. `colores_generados` se queda: solo actúa si un repositorio tiene `brand/tokens/`.

## Consecuencias

- El [ADR-0062](0062-los-colores-de-un-producto-salen-de-brand-tokens-en-dtcg-y-un-generador-arma-el-esquema-de-cada-cliente.md) sigue como el diseño en revisión.
- Una pieza nueva no copia `theme.py`, `tests/test_theme.py`, `scripts/tokens.py` ni `brand/tokens/`, aunque la plantilla los conserve.
- Cuando la sección salga de desarrollo, un ADR nuevo vuelve a exigirla y `verificar.py` recupera la comprobación.

## Descartado

- **Dejar la exigencia de `tests/test_theme.py` en `verificar.py`.** Un repositorio tendría que copiar una prueba que falla por no implementar lo que la nota le dice que no implemente.
