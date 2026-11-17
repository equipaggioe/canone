# ADR-0170 · Cada app guarda su número de build en su manifiesto

- **Estado:** Aceptada. El usuario pidió una sola solución para Android, Flutter y Flet, y aplicar
  la recomendada (2026-11-17)
- **Fecha:** 2026-11-17
- **Alcance:** [`plataformas/transversal.md`](../plataformas/transversal.md), «Distribución»;
  [`plataformas/android.md`](../plataformas/android.md),
  [`plataformas/flutter.md`](../plataformas/flutter.md) y
  [`plataformas/flet.md`](../plataformas/flet.md), «Entrega»; `plantilla/flet/pyproject.toml`,
  `plantilla/.github/workflows/release.yml` y [`stack.md`](../stack.md)

## Contexto

Flet usaba el `github.run_number` del release como número de build, según el ADR-0166; Flutter, el
de `pubspec.yaml`, y Android no tenía regla.

Leído: *Version your app* de Android pone `versionCode` en `defaultConfig` y lo sube con cada
release. La guía de Flutter pone el número de build después del `+` de `version`, en
`pubspec.yaml`. *Publishing* de Flet acepta `[tool.flet].build_number` y `--build-number`. Las tres
herramientas aceptan el número también por la línea de comandos.

Comprobado con AGP 9.5.1: si la variante de release exige un `-PversionCode`, fallan sin él
`buildHealth` y toda tarea que configure la release, y no solo `bundleRelease`.

Comprobado con dependency-analysis 3.20.3: con `kotlinx-coroutines-android` declarado y un código
que importa `Dispatchers` y `Flow`, `buildHealth` falla, porque pide declarar
`kotlinx-coroutines-core` y pasar `-android` a `runtimeOnly`. Con solo `kotlinx-coroutines-core`,
pasa, y `-android` llega con las otras dependencias.

## Decisión

1. **El número de build de una app de Android, de Flutter o de Flet es un entero que vive en su
   manifiesto, junto a su versión, y sube con cada versión que se publica.**
2. Android lo guarda en el `versionCode` de `defaultConfig`; Flutter, después del `+` de `version`,
   y Flet, en `[tool.flet].build_number`. Reemplaza el punto 10 del ADR-0166.
3. `release.yml` deja de pasarle `--build-number` a `flet build`.
4. **El stack de Android nombra `kotlinx-coroutines-core`, y no `-android`.** Reemplaza el punto 8
   del ADR-0169.

## Consecuencias

- El build es el mismo en cualquier máquina, y el que olvida subir el número lo ve en el rechazo de
  Play.
- Una versión que se publica cambia dos valores del manifiesto: la versión y el número de build.

## Descartado

- **El `github.run_number` en las tres apps:** el CI le pasa el número a cada herramienta, y sin él
  cada una toma en silencio el del manifiesto. En Android, exigirlo rompe las tareas de CI que
  configuran la release.
- **Sacar el `versionCode` de `versionName`:** la guía de Android lo plantea como un contador que
  no tiene que parecerse a la versión, y ni Flutter ni Flet tienen esa forma.
