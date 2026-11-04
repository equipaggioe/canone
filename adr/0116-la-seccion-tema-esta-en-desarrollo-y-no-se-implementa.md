# ADR-0116 · La sección «Tema» está en desarrollo y no se implementa

- **Estado:** Aceptada
- **Fecha:** 2026-11-04
- **Alcance:** «Tema» de [plataformas/transversal.md](../plataformas/transversal.md#tema) y de cada cliente, [plantilla/README.md](../plantilla/README.md) y `scripts/verificar.py`

## Contexto

`transversal.md` ya decía que la sección estaba en desarrollo y que ningún producto la usaba, pero `verificar.py` exigía `tests/test_theme.py` en toda pieza de PySide6 o de Flet, y esa prueba exige la sección. Quien llevaba un repositorio a Canone tenía que implementar algo todavía en revisión.

## Decisión

1. **La sección «Tema» está en desarrollo y no se implementa.** Ningún repositorio la sigue mientras la nota esté en `transversal.md`, y no seguirla no es una desviación ni lleva ADR propio.
2. **`verificar.py` sigue exigiendo `tests/test_theme.py`.** Un repositorio con una pieza de PySide6 o de Flet no copia la prueba y queda con ese incumplimiento: es lo que recuerda que la sección falta.

## Consecuencias

- El [ADR-0062](0062-los-colores-de-un-producto-salen-de-brand-tokens-en-dtcg-y-un-generador-arma-el-esquema-de-cada-cliente.md) sigue como el diseño en revisión.
- Una pieza nueva no copia `theme.py`, `tests/test_theme.py`, `scripts/tokens.py` ni `brand/tokens/`, aunque la plantilla los conserve.
- El job `canone` del CI de esos repositorios queda en rojo hasta que la sección salga de desarrollo y cada uno la implemente. Como `release.yml` corre primero `ci.yml`, hasta entonces tampoco publican un release.

## Descartado

- **Que `verificar.py` deje de exigir `tests/test_theme.py`.** El CI quedaría en verde y nada recordaría que la sección falta.
