# ADR-0198 · La sección «Tema» deja de estar en desarrollo

- **Estado:** Aceptada. El usuario pidió quitar la nota «En desarrollo» a todo lo que tenga que ver
  con «Tema» (2026-11-20)
- **Fecha:** 2026-11-20
- **Alcance:** «Tema» de [plataformas/transversal.md](../plataformas/transversal.md#tema) y de cada
  cliente, [plantilla/README.md](../plantilla/README.md) y `scripts/verificar.py`

## Contexto

El [ADR-0116](0116-la-seccion-tema-esta-en-desarrollo-y-no-se-implementa.md) dejó la sección en
desarrollo. Antes de quitar la nota se generó el tema de los cinco clientes desde el
`brand/tokens/` de la plantilla, en un repositorio de prueba (2026-11-20):

| Cliente | Resultado |
| :--- | :--- |
| Flet 1.1.2 | `LIGHT` y `DARK` con los 46 roles; `theme.py` aplica y guarda el modo; `test_theme.py`, ruff y pyrefly pasan |
| Qt (PySide6 6.12) | Fusion y la paleta de cada modo, con el texto inactivo al 38 %; `test_theme.py` pasa |
| Flutter 3.47.9 | `flutter analyze` sin hallazgos y un widget test con los dos esquemas pasa |
| Compose | `Colors.kt` compila con Kotlin 2.4.21 contra `material3-desktop` 1.9.0 de JetBrains, no con AGP |
| SvelteKit 3.2.0 | El build usa las variables generadas; el CSS no tiene reglas `data-theme` |

También se comparó el generador con Terrazzo 2.10.0 y Style Dictionary 5.8.0:

- Style Dictionary no lee el resolver: con `colors.resolver.json` genera un CSS vacío, sin error. Para Flutter y Compose escribe constantes sueltas, no un `ColorScheme`.
- Terrazzo lee el resolver tal como está, pero no escribe Dart, Kotlin ni Python, y su regla de contraste solo mide el contexto por defecto: un par a 1,08:1 en el modo oscuro pasó sin error.

## Decisión

1. **«Tema» se aplica a los repositorios**, en `transversal.md` y en cada cliente.
2. **`scripts/tokens.py` sigue siendo el generador.**
3. **`verificar.py --repo` vuelve a exigirla:** corre `colores_generados`, y `tests/test_theme.py` de Qt y de Flet es canónico.

## Consecuencias

- Un repositorio con un cliente falla su CI hasta tener `brand/tokens/`, la copia de `scripts/tokens.py` y lo generado al día.

## Descartado

- **Terrazzo o Style Dictionary en lugar de `tokens.py`:** ninguno genera los esquemas de los cinco clientes, y sumarían Node a productos que no lo usan.
