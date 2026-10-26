# ADR-0088 · Gradle, AGP y Kotlin tienen una sola versión en Android y en Flutter

- **Estado:** Aceptada
- **Fecha:** 2026-10-26
- **Alcance:** «Proyecto» de [`plataformas/android.md`](../plataformas/android.md) y
  [`plataformas/flutter.md`](../plataformas/flutter.md), `plantilla/android/gradle/wrapper/` y
  `scripts/verificar.py`

## Contexto

Cada app se quedaba con el Gradle, el AGP y el Kotlin que traía la plantilla el día en que se creó.
Las 13 apps Android y Flutter usaban cinco versiones de Gradle, de la 8.12 a la 9.8.0, y AGP de la
8.7.3 a la 9.4.1. Ninguna regla fijaba la versión, y nada fallaba al quedar atrás.

## Decisión

1. Las apps Android y las Flutter usan la misma versión de Gradle, AGP y Kotlin, y canone la fija
   en `android.md`.
2. Gradle corre con el wrapper y su distribución `-bin`.
3. *(propuesta)* `gradle-wrapper.properties` es canónico: el que genera `gradle wrapper`.
4. *(propuesta)* `verificar.py` compara el wrapper con el canónico y comprueba la versión de AGP y
   de Kotlin: en el catálogo de versiones de Android y en `android/settings.gradle.kts` de Flutter.

## Consecuencias

- Subir una versión cambia `android.md`, `PLUGINS` de `verificar.py` y el wrapper canónico, y se
  copia a todas las apps en la misma pasada. Una app que se queda atrás rompe `verificar.py`.
- Una app Flutter no puede pasar a un AGP que su versión de Flutter no acepta, así que la versión
  de Flutter limita la de todas.
- `flet build` genera su proyecto Android con las versiones de su propia plantilla, y queda fuera de
  esta regla.
- Comprobado con Flutter 3.47.5: `flutter build apk --debug` pasa en las doce apps Flutter con
  Gradle 9.8.0, AGP 9.4.1 y Kotlin 2.4.20. Las que venían de AGP 8 cambian `kotlinOptions` por
  `kotlin { compilerOptions }`.

## Descartado

- **La distribución `-all`:** solo agrega las fuentes y la documentación de Gradle.
- **La versión de cada app:** deja una versión por fecha de creación, como antes.
- **Escribir la versión solo en la página:** nada falla cuando una app se queda atrás.
