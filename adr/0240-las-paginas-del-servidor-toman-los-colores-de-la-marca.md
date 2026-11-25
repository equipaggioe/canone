# ADR-0240 · Las páginas del servidor toman los colores de la marca

- **Estado:** Propuesta
- **Fecha:** 2026-11-24
- **Alcance:** `autenticacion.md`, `transversal.md`, `plantilla/scripts/tokens.py`,
  `scripts/verificar.py` y `plantilla/server/`

## Contexto

La página de autorización usaba los colores del navegador, y era lo único que cada producto tenía que
editar en `pages.py`, que por eso era un punto de partida. Los colores de todo cliente ya salen de
`brand/tokens/`.

## Decisión

1. `scripts/tokens.py` genera `server/src/app/colors.py` si el servidor tiene `pages.py`: las variables
   CSS del tema inicial, en su modo, o en los dos según el del sistema.
2. `pages.py` usa esas variables y ningún otro color, y se copia sin editar.
3. `verificar.py --canone` comprueba que `colors.py` de la plantilla salga de su `brand/tokens/`.

## Consecuencias

- La página sigue el tema inicial y el modo del sistema aunque el usuario haya elegido otros en la
  app: son preferencias de cada dispositivo, y el navegador del sistema no las tiene.
- Un repositorio con cuentas tiene `brand/tokens/`, aunque no tenga un cliente.
- `scripts/tokens.py` es canónico: cada repositorio con un cliente copia el nuevo.

## Descartado

- **`pages.py` como punto de partida:** cada producto escribiría los colores a mano, y nada
  comprobaría su contraste ni el script de la página.
- **Un archivo CSS aparte:** la página no carga recursos.
