# ADR-0201 · Un producto elige sus temas y sus modos, y el modo es otro modificador

- **Estado:** Aceptada. El usuario pidió que cada repositorio pueda tener un tema con un modo, con
  los dos o varios temas, y reevaluar, con pruebas y con la literatura, e implementar las demás
  recomendaciones (2026-11-20)
- **Fecha:** 2026-11-20
- **Alcance:** «Tema» de [plataformas/transversal.md](../plataformas/transversal.md#tema) y de cada
  cliente, «Accesibilidad» de `transversal.md`, «Estilos» de
  [plataformas/sveltekit.md](../plataformas/sveltekit.md#estilos), `plantilla/` y
  `scripts/verificar.py`

## Contexto

El [ADR-0062](0062-los-colores-de-un-producto-salen-de-brand-tokens-en-dtcg-y-un-generador-arma-el-esquema-de-cada-cliente.md)
dejaba un solo modificador, `theme`, con `light` y `dark`, y en propuesta los pares de contraste,
la paleta de Qt y los nombres de archivo.

Lo que dice la literatura:

| Fuente | Qué dice |
| :--- | :--- |
| [DTCG Resolver §2.1](../fuentes/dtcg/resolver.html) | Los modificadores conviene que no se pisen: cada uno aporta tokens distintos |
| [Qt Style Sheets, Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet.qdoc) | «Style sheets are a tool for prototyping and for small, local adjustments»; para producción, un `QStyle`. «Don't use this function to switch themes at runtime» |
| [QProxyStyle, Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/styles/qproxystyle.cpp) | «It is the recommended way to adjust the platform style in a production application» |
| [Fusion, Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/styles/qfusionstyle_p_p.h) | El marco de un campo es `window().color().darker(140)` y la grilla de una tabla, `darker(120)`, sin caso para un fondo oscuro |
| [ColorScheme de Compose](https://raw.githubusercontent.com/androidx/androidx/androidx-main/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/ColorScheme.kt) | `outline` es para bordes y «adds contrast for accessibility purposes»; `outlineVariant`, para bordes decorativos |
| [Tailwind CSS Compatibility](https://tailwindcss.com/docs/compatibility) y [MDN, `light-dark()`](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark) | Wind4 pide Safari 16.4; `light-dark()` está en todos los navegadores desde mayo de 2024 |
| [MDN, `script-src`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/script-src) | Un script en línea necesita `'unsafe-inline'`, un nonce o un hash |

Se probó en un repositorio con los cinco clientes y dos temas, con los dos modos, solo con el claro
y solo con el oscuro, y con un tema y un modo (2026-11-20):

| Prueba | Resultado |
| :--- | :--- |
| Flet 1.1.2 y PySide6 6.12 | La elección se guarda y se relee; un tema guardado que ya no existe falla con `KeyError`; ruff, `ruff format` y pyrefly sin hallazgos en cada combinación |
| Flutter 3.47.9 | `dart format` no cambia lo generado, `flutter analyze` sin hallazgos, y un widget test recorre `ColorTheme.values` en cada combinación |
| Compose | ktlint 1.8.0 con `android_studio` sin hallazgos; compila con Kotlin 2.4.21 contra `material3-desktop` 1.9.0 de JetBrains, y con AGP 9.5.1 y el BOM 2026.09.00 hasta empaquetar |
| SvelteKit 3.2.0 en Chromium (Playwright 1.65.1) | Cada combinación de tema, modo y modo del sistema da el color esperado, sin violaciones de la CSP; con un solo modo, el modo del sistema no cambia nada; `theme.js` pone los atributos antes de que empiece `<body>` |
| Fusion, en capturas offscreen | Con el `QProxyStyle`, el marco de campos, spin boxes, combo boxes, listas y paneles y la grilla de las tablas se ven en los dos modos, y el foco en 2 px de `primary` |
| knip 6.45.1 | Sin `/** @public */`, un producto de un solo tema falla por `themes`, `Theme` e `initialTheme`; `static/theme.js` sale como archivo sin usar si no está en `entry` |

El generador anterior no había pasado nunca por `dart format`, ktlint ni prettier: su Kotlin tenía
el formato que ktlint corrige.

## Decisión

1. **Cada producto elige sus temas y sus modos:** uno o más temas, y `light`, `dark` o los dos.
   `colors.resolver.json` tiene `theme`, con un contexto por tema y el inicial en `default`, y
   `mode`, con los modos del producto. Los archivos de un tema solo tienen `palette`, y los de un
   modo, solo `color`: los dos modificadores no se pisan.
2. **Con un solo modo, el cliente lo usa siempre**; con los dos, el usuario elige como dice el
   [ADR-0160](0160-el-usuario-elige-el-modo-claro-u-oscuro-en-cada-dispositivo.md).
3. **Un tema se nombra con minúsculas y dígitos**, y dos temas iguales hacen fallar al generador.
4. **Cada cliente recibe el enum `ColorTheme`**, con un campo por modo y el tema inicial:
   `ColorTheme.initial` en Dart y Kotlin, `INITIAL` en Python, `initialTheme` en TypeScript. Lo
   generado sale con el formato de `dart format`, ktlint, `ruff format` y prettier.
5. **Los archivos generados** son `colors.dart`, `ColorTheme.kt`, el `colors.py` de Flet y de Qt
   y `colors.ts`. El de Kotlin se llama como su única clase, como pide ktlint.
6. **Los pares de contraste** viven en `tokens.py`: los del ADR-0062, punto 7, más `primary` y
   `error` contra cada superficie, a 4.5:1, porque Material los usa como texto en un botón de texto
   y en el error de un campo.
7. **Qt dibuja con `Style`, un `QProxyStyle` sobre Fusion, y sin hojas de estilo.** `Dark` es
   `outline`; `Style` dibuja en él el marco de campos, spin boxes, combo boxes y paneles, en 2 px
   de `Highlight` con el foco, y la grilla de las tablas en `Mid`. Los botones con `variant` toman
   sus colores en `Style`.
8. **En la web**, el tema va en `data-theme` y el modo en `data-mode`. `colorsCss` escribe un
   bloque por tema y modo, cada uno con su `color-scheme`.
9. **`static/theme.js`, canónico, copia la elección en `<html>` antes de pintar**, y `app.html` lo
   carga en el `<head>`. `knip.json` lo declara en `entry`. `src/lib/theme.ts` es el punto de
   partida que guarda y aplica la elección.
10. **La elección se guarda en las claves `mode` y `theme`** del almacén de preferencias de cada
    cliente.

## Consecuencias

- Agregar un tema es agregar su archivo de paleta y un contexto, y pasar a tener los dos modos es agregar el archivo del otro modo: el generador no cambia.
- Los `theme.py` y `theme.ts` de la plantilla son para los dos modos: con uno, el repositorio les quita la elección del modo.
- El tamaño de lo generado crece con cada tema.

## Descartado

- **Dos caminos, uno para claro y oscuro y otro para varios temas:** dos generadores, dos formas de código en los clientes y dos comprobaciones que se separan con el tiempo.
- **Un solo modificador con contextos planos**, como `light`, `dark` y `sepia`: no dice cuál sigue al modo oscuro del sistema, y cada tema repite todos los roles.
- **`secondary` y `tertiary` como texto sobre una superficie:** Material no los usa así.
- **La hoja de estilo para los marcos de Qt:** Qt la deja para prototipos y pide no cambiar de tema con ella, y un spin box con borde de hoja de estilo pierde sus botones si no se le dibujan también.
- **`light-dark()` en la web:** escribe cada rol una sola vez, pero llega a Safari 17.5, más tarde que lo que pide Wind4. La repetición queda en un archivo generado.
- **Un script en línea con su hash puesto a mano en la CSP:** hay que mantener el hash con cada cambio del script.
- **Los roles de bisel que deriva `QPalette(button, window)`:** en el modo oscuro el marco hundido sigue sin verse.
- **`Color.kt`, el nombre de la plantilla de Android Studio:** ktlint pide que el archivo se llame como su única clase.
- **Los tamaños y la tipografía como tokens:** cambian de unidad por cliente, y Flutter, Compose y Flet ya traen la escala de Material.
