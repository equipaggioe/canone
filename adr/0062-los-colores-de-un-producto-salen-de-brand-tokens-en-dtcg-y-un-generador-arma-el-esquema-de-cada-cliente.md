# ADR-0062 · Los colores de un producto salen de `brand/tokens/` en DTCG, y un generador arma el esquema de cada cliente

- **Estado:** Aceptada, salvo los puntos 7, 8 y 9, que siguen en propuesta
- **Fecha:** 2026-10-17
- **Alcance:** la sección «Tema» de [plataformas/transversal.md](../plataformas/transversal.md#tema)
  y la de cada cliente; `brand/`, `scripts/` y los clientes de cada repositorio

## Contexto

`transversal.md` pedía un módulo de tokens por cliente, y que la web y las apps tuvieran la misma
paleta, con un archivo que dijera de cuál era espejo. Cada cliente copiaba los colores a mano y
tenía su propia prueba de contraste: una diferencia entre clientes no se notaba sin revisarlos.

## Decisión

1. Los colores de un producto van en `brand/tokens/`, en el formato de DTCG 2025.10, con su
   módulo de color y su resolver. Es la única fuente de los colores de todos sus clientes. Lo que
   canone comparte entre repositorios es el mecanismo, no la paleta.
2. Los tokens tienen dos niveles: `palette` guarda los colores y `color` asigna cada rol con un
   alias. Claro y oscuro son los contextos `light` y `dark` del modificador `theme` del resolver.
3. Los roles se nombran como los de color de `ColorScheme` de Flutter sin los obsoletos, y cada
   modo los asigna todos.
4. `scripts/tokens.py`, canónico en `plantilla/`, genera en cada cliente su esquema claro y su
   esquema oscuro ya armados, y falla ante todo lo que esté fuera del subconjunto de DTCG que lee.
5. Lo generado se commitea, y `verificar.py` falla si no está al día con `brand/tokens/`.
6. El contraste se comprueba una sola vez, sobre `brand/tokens/`, y reemplaza la prueba de cada
   cliente. El texto pide 4.5:1 aunque sea grande.
7. *(propuesta)* Los pares que se comprueban: `onSurface` y `onSurfaceVariant` contra cada
   superficie; cada `on…` contra su rol; `onXFixed` y `onXFixedVariant` contra `xFixed` y
   `xFixedDim`; `inversePrimary` contra `inverseSurface`, y `outline` contra cada superficie, con
   3:1.
8. *(propuesta)* Qt sigue el modo del sistema con la señal `colorSchemeChanged`, y la paleta de
   Fusion asigna cada `QPalette.ColorRole` a un rol; el texto deshabilitado es `onSurface` al 38 %.
9. *(propuesta)* Los nombres de archivo: `colors.resolver.json` y, en los clientes, `colors.dart`,
   `Colors.kt`, `colors.py` y `colors.ts`.

## Consecuencias

- Cambiar un color de la marca toca un token y una corrida del generador.
- Un cliente compila sin Python: el generador corre solo al cambiar `brand/tokens/`.
- Todo repositorio con clientes falla en `verificar.py` hasta tener `brand/tokens/` y
  `scripts/tokens.py`.
- El generador es código propio que se mantiene en canone. Lee solo color sRGB opaco, alias a
  `palette` y un modificador `theme`; ampliar el subconjunto es cambiar el script.
- `tests/test_theme.py` de Flet y de Qt pasa a exigir los colores solo en `colors.py`.

## Descartado

- **Una copia de la paleta por cliente:** una diferencia entre clientes no se detecta, y cada
  cliente necesita su prueba de contraste.
- **Style Dictionary:** no trae salida para Python, la de Compose y la de Flutter son constantes
  sueltas y no un esquema, y su documentación da el soporte de DTCG 2025.10 como en progreso. Habría
  que escribir todas las salidas igual, en JavaScript, y sumar Node a todo producto.
- **Un JSON propio:** canone tendría que definir, documentar y mantener otro formato.
- **Los modos como grupos propios dentro de un archivo:** el resolver de DTCG ya define los modos.
- **El evento `ApplicationPaletteChange` en Qt:** la app lo provoca al aplicar su paleta.
  Comprobado con PySide6 6.12 en Windows: `setPalette()` lo emite, y `colorSchemeChanged` llega
  al cambiar el esquema.
- **`tokens/` en la raíz, `packages/tokens/` o renombrar `brand/`:** `brand/` ya guarda la
  identidad del producto ([ADR-0017](0017-la-marca-vive-en-brand.md)), y `packages/` es código
  que se instala.
