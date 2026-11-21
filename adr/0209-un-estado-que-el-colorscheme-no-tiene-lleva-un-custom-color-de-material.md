# ADR-0209 · Un estado que el `ColorScheme` no tiene lleva un custom color de Material

- **Estado:** Aceptada. El usuario pidió reevaluar la propuesta mirando solo si la forma de
  Material sirve, sin pesar si su código se mantiene y sin obligación de adoptarlo como fuente, y
  escribirla si se mantenía (2026-11-21). Los puntos marcados *(propuesta)* no se confirmaron uno
  por uno
- **Fecha:** 2026-11-21
- **Alcance:** «Tema» y «Accesibilidad» de
  [plataformas/transversal.md](../plataformas/transversal.md#tema), «Tema» de `flutter.md`,
  `android.md` y `flet.md`, `plantilla/scripts/tokens.py`, `plantilla/brand/tokens/` y
  `plantilla/flet/theme.py`

## Contexto

Consola muestra éxito y advertencia, como texto y en sus LED, y el `ColorScheme` de Material no
tiene esos roles: `tokens.py` fallaba con un rol de más.

Material agrega un color a un esquema con un *custom color*. En
[`theme_utils.ts`](https://raw.githubusercontent.com/material-foundation/material-color-utilities/4dbd965df653f8c82d09c0c96c8067d4b7fa9070/typescript/utils/theme_utils.ts)
de material-color-utilities, `customColor()` devuelve, para cada modo, un `ColorGroup` con
`color`, `onColor`, `colorContainer` y `onColorContainer`, que saca de los tonos 40, 100, 90 y 10
de una paleta en el modo claro y 80, 20, 30 y 90 en el oscuro, y que con `blend` acerca el tono al
color de la marca. Es la misma forma que tiene `error` en el `ColorScheme`.

Lo que se comprobó (2026-11-21):

| Qué | Resultado |
| :--- | :--- |
| `ColorScheme` de Flutter y de Compose | No admiten roles fuera de los suyos. Flutter agrega colores a `ThemeData` con un `ThemeExtension`; en Compose van en un `CompositionLocal` |
| `ft.Theme` de Flet 1.1.2 | No tiene campo de extensiones: los custom colors no siguen solos al modo |
| Lo generado sin custom colors | Igual byte por byte a lo que generaba el `tokens.py` anterior |
| Flutter 3.47.9 | `dart format` no cambia lo generado, `dart analyze --fatal-infos` con el `analysis_options.yaml` de la plantilla no tiene hallazgos, y un widget test pasa del modo claro al oscuro: a mitad de la animación el color está interpolado y al final es el de `darkCustom` |
| Compose | ktlint 1.8.0 con `android_studio` no tiene hallazgos. Compila con Kotlin 2.4.21 y su plugin de Compose contra `material3-desktop` 1.9.0 de JetBrains, junto a un tema que provee `LocalCustomColors` con `CompositionLocalProvider` y una función `@Composable` que lo lee; el enum armado da los colores de `brand/tokens/` |
| Flet 1.1.2 y Qt | `ruff format` y ruff, con la configuración de la plantilla, no tienen hallazgos; `custom()` de `theme.py` devuelve el `CustomColors` del modo claro, del oscuro y del sistema en oscuro. Con PySide6 6.12.0, `palette()` arma la paleta de cada modo con los custom colors en el mismo diccionario |
| `tokens.py --check` | Falla ante una familia incompleta, un `onX` sin su `x`, un custom color que está en un solo modo y un par bajo 4.5:1 |
| Consola, en oscuro | `SUCCESS` (#3fb950) y `WARNING` (#d29922) dan de 4,72 a 7,50 contra sus tres fondos |

## Decisión

1. **Un estado que el `ColorScheme` no tiene lleva un custom color de Material:** cuatro roles,
   `x`, `onX`, `xContainer` y `onXContainer`, que son los de `ColorGroup`. Es una convención
   propia que enlaza `theme_utils.ts` en un commit fijo, y no se copia en `fuentes/`: es código de
   una biblioteca, no un documento que tome posición, y no daría tres convenciones.
2. **El éxito es `success`, y la advertencia, `warning`.**
3. **Un custom color se nombra con minúsculas y dígitos**, y no con un rol del `ColorScheme`.
   Todos los temas y los modos tienen los mismos. `tokens.py` reconoce cada uno por su rol `x` y
   falla si le falta otro de sus roles. *(Propuesta:* se admite cualquier otro custom color, además
   de los de estado.)
4. **Los pares de contraste de cada custom color:** `onX` contra `x` y `onXContainer` contra
   `xContainer`, y `x` contra cada superficie, a 4.5:1, porque es el color de su estado en un
   texto.
5. **Lo generado:**
   - Flutter: la clase `CustomColors`, un `ThemeExtension` con `copyWith` y `lerp`, y los campos
     `lightCustom` y `darkCustom` del enum. `lerp` falla si el otro tema no tiene `CustomColors`.
   - Compose: la data class `CustomColors`, `LocalCustomColors` sin valor por defecto y los campos
     `lightCustom` y `darkCustom`, en el mismo `ColorTheme.kt`.
   - Flet: la dataclass `CustomColors` y los campos `light_custom` y `dark_custom`.
   - Qt: los roles van en el mismo diccionario del esquema.
   - Web: una variable CSS y un color de UnoCSS por rol, como los demás.
   - Sin custom colors no se genera `CustomColors`.
6. **En Flet, `custom()` de `theme.py`** devuelve los custom colors del modo que muestra la
   página, y un control que los usa se vuelve a pintar cuando el modo cambia.
7. **`brand/tokens/` de la plantilla trae `success` y `warning`** *(propuesta)*, con los tonos
   que da material-color-utilities para #3fb950 y #d29922, sin `blend`.

## Consecuencias

- Consola agrega `success` y `warning` a sus `brand/tokens/`, y `test_theme.py` deja de encontrar
  literales para esos colores.
- Cada producto asigna los cuatro roles de cada custom color, también los que no use, como pasa con
  los 46 del `ColorScheme`.
- En Flet, los custom colors no siguen solos al modo: cada control que los usa se pinta de nuevo.
- Cambiar `tokens.py` deja desactualizado lo generado en cada repositorio hasta volver a correrlo.

## Descartado

- **Copiar `theme_utils.ts` en `fuentes/`:** no cumple los requisitos de una fuente. Lo que sirve
  de él es la forma de la familia, y eso se escribe como convención propia.
- **Calcular los tonos con HCT y `blend`:** en `brand/tokens/` cada rol es un alias de `palette`, y
  el contraste lo comprueba `tokens.py`; un cálculo tapaba el color que elige la marca.
- **Usar `tertiary` u otro rol del `ColorScheme` para un estado:** pierde su sentido, y en Consola
  `tertiary` ya es otro color.
- **Solo `x` y `onX`:** un chip o un aviso de estado necesitan el contenedor, y la familia de
  Material tiene los cuatro.
- **Agrupar los roles, como `color.success.onColor`:** `error` es plano en el `ColorScheme`, y los
  custom colors se escriben igual.
- **En Flutter, una clase aparte sin `ThemeExtension`:** no cambia con `themeMode` ni se anima con
  el tema.
- **Un valor por defecto en `LocalCustomColors`:** un tema que no lo provee mostraría colores que
  nadie eligió.
