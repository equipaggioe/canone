# ADR-0187 · Flet fija `jni` y `jni_flutter` en el `pubspec.yaml` que genera

- **Estado:** Reemplazada por [ADR-0245](0245-flet-pasa-a-la-1-1-3-y-deja-de-fijar-jni.md)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/flet.md`](../plataformas/flet.md), «Proyecto»; [`stack.md`](../stack.md),
  «Flet»; `plantilla/flet/pyproject.toml` y `scripts/verificar.py`

## Contexto

Comprobado el 2026-11-18 en un Galaxy S10e con Android 12, con Flet 1.1.2 y Flutter 3.47.9:
`flet build apk` resolvió `path_provider_android` 2.3.1 con `jni` 1.2.0 y `jni_flutter` 1.1.0, y
la app no arrancó: mostró `ClassNotFoundException: Didn't find class "Landroid/content/Context;"`.
Con `jni` 1.1.2 y `jni_flutter` 1.0.4+1 en `[tool.flet.flutter.pubspec.dependency_overrides]`, la
misma app arrancó.

## Decisión

1. **El `pyproject.toml` de una app de Flet fija `jni` 1.1.2 y `jni_flutter` 1.0.4+1 en
   `[tool.flet.flutter.pubspec.dependency_overrides]`**, con las versiones de `stack.md`.
2. **`verificar.py` falla si una app de Flet no las fija.**

## Consecuencias

- Subir `jni` pide volver a probar la app en un teléfono.

## Descartado

- **Fijar `path_provider_android`:** no se probó si basta, y `jni` es el paquete que falla.
