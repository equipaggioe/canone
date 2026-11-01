# ADR-0111 · Android Lint no avisa versiones nuevas

- **Estado:** Aceptada
- **Fecha:** 2026-11-01
- **Alcance:** «Estilo» de [`plataformas/android.md`](../plataformas/android.md)

## Contexto

«Proyecto» de android.md fija Gradle 9.8.0, AGP 9.4.1 y Kotlin 2.4.20
([ADR-0088](0088-gradle-agp-y-kotlin-tienen-una-sola-version-en-android-y-flutter.md)), y `scripts/verificar.py`
falla con otras. «Estilo» pide `warningsAsErrors = true` en Android Lint, que trae tres chequeos
que avisan cuando hay una versión más nueva publicada. El 2026-11-01, en el CI de `equipaggio`,
Lint dio nueve errores por versiones nuevas (Gradle 9.8.2, AGP 9.5.0, Kotlin 2.4.21 y seis
bibliotecas). Con las versiones de canone falla Lint, y con las nuevas falla `verificar.py`. En
local pasaba, porque Lint usaba un índice de versiones guardado en `build/`.

## Decisión

1. El bloque `lint` de `app/build.gradle.kts` apaga `AndroidGradlePluginVersion`,
   `GradleDependency` y `NewerVersionAvailable`.
2. Los demás chequeos de Lint siguen como errores.

## Consecuencias

- El CI de una app no cambia de resultado porque se publique una versión: el mismo commit da el
  mismo resultado.
- Nadie avisa que una biblioteca del catálogo tiene una versión más nueva. Subirla es una decisión
  aparte, como subir Gradle, AGP y Kotlin en «Proyecto».

## Descartado

- **Subir las versiones fijas de «Proyecto» cada vez:** vuelve a fallar con la próxima versión
  publicada, en todos los repositorios a la vez.
- **Una línea base de Lint (`lint-baseline.xml`):** guarda los avisos del día en que se crea, y
  una versión publicada después vuelve a fallar.
