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

## Cómo se hace cumplir

| Regla | Con qué |
|---|---|
| Contraste de los tokens | Una prueba por cliente sobre el módulo de tokens |
