# ADR-0217 · En una app que solo se usa con el puntero, un objetivo mide 24 × 24

- **Estado:** Aceptada. El usuario pidió el 2026-11-21 aplicar lo que recomendara la literatura. El punto 2 lo reemplaza el [ADR-0227](0227-un-objetivo-mas-chico-que-24-x-24-vale-con-su-circulo-de-24-libre.md)
- **Fecha:** 2026-11-21
- **Alcance:** `transversal.md`

## Contexto

«Accesibilidad» de `transversal.md` pedía 48 × 48 a «cada objetivo táctil», con la cita de WCAG
2.5.8. Una app de Qt es de escritorio y se usa con el puntero: no estaba claro si el 48 × 48 regía
en ella o si bastaba el 24 × 24 de 2.5.8 (pregunta 14 del plan de Consola). Los otros clientes se
usan también con el dedo: Flet y Flutter arman para el teléfono, y la web se abre en él.

Lo que se recomienda:

- WCAG 2.5.8 pide 24 × 24 a toda entrada de puntero, «no solo táctil, sino también ratón,
  trackpad, lápiz y otras». Dice que exigir el tamaño pensado para el dedo «no habría sido
  apropiado como umbral para todas las entradas de puntero», y que el grupo eligió 24 después de
  medir los objetivos de sitios muy visitados. Los 44 × 44 son del nivel AAA (2.5.5)
  ([Understanding 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)).
- Apple fija en macOS 28 × 28 pt por omisión y 20 × 20 pt como mínimo, contra 44 × 44 y 28 × 28
  en iOS ([HIG, *Accessibility*](https://developer.apple.com/design/human-interface-guidelines/accessibility)).
- Microsoft da el tamaño de 7,5 mm (40 × 40 px a 135 PPI) para el dedo, con el que vienen los
  controles de WinUI
  ([Guidelines for touch targets](https://learn.microsoft.com/en-us/windows/apps/develop/input/guidelines-for-targeting)),
  y una densidad compacta, que baja el alto de los controles, para las apps de escritorio que se
  usan sobre todo con el ratón o el teclado
  ([Compact sizing](https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/compact-sizing)).
- Material pide 48 × 48 dp a un objetivo táctil
  ([Touch target size](https://support.google.com/accessibility/android/answer/7101858)).

Ninguna guía pide 48 × 48 en el escritorio, y Apple y Microsoft le dan menos que al teléfono.

## Decisión

1. El objetivo táctil sigue en 48 × 48, en dp en las apps y en px de CSS en la web.
2. En una app que solo se usa con el puntero, como la de Qt, cada objetivo mide al menos 24 × 24
   px independientes del dispositivo, salvo un enlace dentro de una frase.

## Consecuencias

- `tests/test_accessibility.py` de Qt ya mide 24 × 24 (ADR-0216); no cambia.
- Consola cumple: sus objetivos miden 24 px desde su ADR-0095.
- Si una app de Qt llega a usarse con el dedo, rige el 48 × 48.

## Descartado

- **48 × 48 en todo cliente:** ninguna guía de escritorio lo pide, y en una ventana densa como la
  de Consola agranda cada botón, pestaña y asa al doble de alto.
- **44 × 44, de 2.5.5:** es del nivel AAA, y la sección no lo pide en ningún cliente.
- **Los 20 × 20 de Apple:** quedan por debajo de WCAG, que es el estándar de la sección.
