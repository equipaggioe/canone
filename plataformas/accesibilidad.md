# Accesibilidad

Que todos puedan usar cada cliente.

## Criterios

Estándar: [WCAG 2.2](../estandares/w3c/wcag22.html) de W3C.

- Todos los clientes cumplen el nivel AA, también las apps. Es la vara que nombra la guía de
  Flutter, y una sola para todos los clientes.
- Cada objetivo táctil mide al menos 48 × 48: dp en las apps y px de CSS en la web. Endurece los 24
  px del criterio 2.5.8, porque la web también se usa en el teléfono, y es la medida que Android
  recomienda.
- El módulo de tokens de diseño cumple los criterios 1.4.3 y 1.4.11 en el tema claro y en el
  oscuro, y una prueba de cada cliente calcula el contraste de cada par de color de texto y de
  fondo. El contraste no se elige a ojo.

## Web

Estándares: las [advertencias del compilador](../estandares/svelte/compile-warnings.md) de Svelte y
[`sv check`](../estandares/svelte/sv-check.md).

- `svelte-check` corre con `--fail-on-warnings`. Las advertencias `a11y_*` del compilador rompen
  CI.

## Flutter

Estándares: de Flutter, [*Accessibility*](../estandares/flutter/accessibility.md),
[*UI design and styling*](../estandares/flutter/accessibility-ui-design.md),
[*Assistive technologies*](../estandares/flutter/accessibility-assistive.md) y
[*Accessibility testing*](../estandares/flutter/accessibility-testing.md).

- Cada pantalla tiene una prueba de widget con las cuatro guías: `androidTapTargetGuideline`,
  `iOSTapTargetGuideline`, `labeledTapTargetGuideline` y `textContrastGuideline`.

## Android

Estándares: de Android, [*Make apps more accessible*](../estandares/android/accessibility-apps.md)
y [*Principles for improving app accessibility*](../estandares/android/accessibility-principles.md),
y de Compose, [*Accessibility testing*](../estandares/compose/accessibility-testing.md).

- Las pruebas de UI de Compose llaman a `enableAccessibilityChecks()`.

## Flet

Estándar: [*Accessibility*](../estandares/flet/accessibility.md) de Flet.

## Qt

Estándares: [*Accessibility*](../estandares/qt/accessible.qdoc) de Qt y la propiedad
`accessibleName` de [`QWidget`](../estandares/qt/qwidget.qdoc).

## Cómo se hace cumplir

| Regla | Con qué |
|---|---|
| Contraste de los tokens | Una prueba por cliente sobre el módulo de tokens |
| Advertencias `a11y_*` en la web | `svelte-check --fail-on-warnings` en CI |
| Objetivos, etiquetas y contraste en Flutter | Las guías de `flutter_test` en cada pantalla |
| Objetivos, etiquetas y contraste en Android | `enableAccessibilityChecks()` en las pruebas de UI |
