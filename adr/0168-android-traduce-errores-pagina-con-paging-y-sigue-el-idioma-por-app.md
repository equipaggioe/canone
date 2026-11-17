# ADR-0168 · Android traduce los errores en la fuente de red, pagina con Paging 3 y sigue el idioma por app del sistema

- **Estado:** Aceptada. El usuario pidió implementar las decisiones pendientes de la revisión que
  se mantuvieran al reevaluarlas (2026-11-16), y quitar la nota «En desarrollo» de Android (2026-11-17)
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/android.md`](../plataformas/android.md), [`stack.md`](../stack.md) y
  `scripts/contar_enunciados.py`

## Contexto

Quedaron pendientes de la revisión del
[ADR-0167](0167-android-escribe-solo-lo-que-elige-y-cumple-los-contratos-de-red.md) dónde se
traducen los errores, cómo elige el usuario el idioma, cómo se pagina, el `versionCode` y una fila
de «Cumplimiento».

Leído: *Per-app language preferences* de Android pide `generateLocaleConfig` y
`unqualifiedResLocale` para que la app aparezca en los ajustes de idioma del sistema. En
`androidx.core` 1.19.1, `LocaleManagerCompat.getApplicationLocales()` lee el idioma por app del
sistema en la API 33 o mayor, y por debajo el que guarda AppCompat; sin AppCompat devuelve una
lista vacía.

Comprobado con AGP 9.5.1: `generateLocaleConfig = true` con `unqualifiedResLocale=es` genera un
`locale-config` con `defaultLocale="es"`, y un proyecto con `PagingSource<String, T>` y
`collectAsLazyPagingItems` compila con Paging 3.5.3, y `buildHealth` no pide otro artefacto de
Paging que `paging-common` y `paging-compose`.

Comprobado en una copia de `equipaggio/mobile` (AGP 9.4.1) con Gradle 9.9.1 y el JDK 25.0.5,
corriendo `lintDebug assembleDebug testDebugUnitTest bundleRelease`:

- Con 512 MiB de heap, el de Gradle por defecto, `bundleRelease` termina en
  `OutOfMemoryError: Java heap space`. Sin `bundleRelease`, el build pasa.
- Con 384 MiB de Metaspace, el de Gradle por defecto, el build pasa, pero Gradle descarta el daemon
  al terminar porque se agotó el Metaspace.
- Con `-Xmx4g -XX:MaxMetaspaceSize=2g`, pasa sin avisos.

Comprobado en el dispositivo administrado por Gradle con la imagen `aosp-atd` de la API 37: una
prueba de Compose pasa con `espresso-core` 3.7.0, y con el 3.5.0 que trae `ui-test` falla con
`NoSuchMethodException: android.hardware.input.InputManager.getInstance`. Sin `testedAbi`, AGP
9.5.1 avisa que su valor por defecto pasa de `x86_64` a `arm64-v8a` en AGP 10, y que la imagen no
corre pruebas para `arm64-v8a`.

## Decisión

1. **La fuente de datos de red traduce una `HttpException` a la excepción tipada del sobre de
   `transversal.md`.**
2. **El usuario elige el idioma en los ajustes del sistema:** `generateLocaleConfig = true` y
   `unqualifiedResLocale=es`. `Accept-Language` lleva el primer idioma por app o, si no hay, el
   primero del sistema, leídos con `LocaleManagerCompat`.
3. **Una lista con `nextPageToken` usa Paging 3**, con el `pageToken` como clave, y el ViewModel
   expone el `PagingData` fuera de `uiState`.
4. **«Reintentos» va después de «Push»**, en el orden alfabético de los temas.
5. **`contar_enunciados.py` deja de nombrar nueve archivos que ya no están en `fuentes/`.**
6. **El dispositivo de pruebas vuelve a fijar `testedAbi = "x86_64"`**, con el aviso de AGP como
   razón. Reemplaza esa parte del punto 13 del ADR-0167.
7. **La razón de `jvmargs` es lo comprobado:** el build de release se queda sin heap, y Gradle
   descarta el daemon al agotarse el Metaspace.
8. **`android.md` y su bloque de `stack.md` dejan de estar en desarrollo.** «Tema» conserva su
   nota.

## Consecuencias

- `stack.md` suma `androidx.core:core` y Paging.
- `verificar.py` exige las convenciones de `android.md` a los repositorios con una app de Android.
- En la API 32 o menor, el usuario no elige un idioma propio para la app: la app sigue el del
  sistema.

## Descartado

- **`versionCode` igual al `github.run_number`:** para que falle sin él, la variante de release lo
  exige, y `buildHealth` y cualquier tarea que configure la release fallan en CI. Con un valor por
  defecto, sería un fallback. Queda sin decidir.
- **Permitir en el README que una fila de «Cumplimiento» haga cumplir una convención de
  `stack.md`:** la página ya la escribe en «Proyecto» con su herramienta, y la fila se refiere a
  esa convención.
- **Un selector de idioma en la app con AppCompat:** suma AppCompat y `AppCompatActivity` solo
  para la API 32 o menor, y la fuente lo ofrece como opcional.
