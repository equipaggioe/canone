# Flutter

Una app en Flutter.

## Estilo

Estándares: [*Effective Dart*](../estandares/dart/effective-dart-index.md):
[*Style*](../estandares/dart/effective-dart-style.md),
[*Documentation*](../estandares/dart/effective-dart-documentation.md),
[*Usage*](../estandares/dart/effective-dart-usage.md) y
[*Design*](../estandares/dart/effective-dart-design.md).

- `dart format` usa líneas de 99.

## Analizador

Estándar: [flutter_lints](../estandares/pub/flutter_lints/README.md) y su
[configuración](../estandares/pub/flutter_lints/flutter.yaml).

- El analizador activa `strict-casts`, `strict-inference` y `strict-raw-types`, y CI corre
  `flutter analyze --fatal-infos`. Endurece flutter_lints: los tipos se revisan como con Pyrefly
  en modo strict.

Plantilla: [`plantilla/flutter/`](../plantilla/flutter/): `analysis_options.yaml`, con el
analizador y el ancho de `dart format`, que se copia sin editar, y `.gitignore`.

## Arquitectura

Estándares: [*Common architecture concepts*](../estandares/flutter/app-architecture-concepts.md),
[*Guide to app architecture*](../estandares/flutter/app-architecture-guide.md) y
[*Architecture recommendations and resources*](../estandares/flutter/app-architecture-recommendations.md)
de Flutter, con sus [recomendaciones](../estandares/flutter/architecture-recommendations.yml).

```text
<pieza>/
  pubspec.yaml
  pubspec.lock
  analysis_options.yaml
  lib/
    main.dart
    config/
    routing/
    data/
      repositories/
      services/       el cliente de la API
    domain/
      models/         los modelos con freezed
    ui/
      core/
        themes/       el tema claro y el oscuro
      <función>/
        view_models/
        widgets/
  test/
```

- Las carpetas llevan el nombre del componente de arquitectura, como pide la recomendación de
  nombres.
- Los modelos se generan con freezed y json_serializable. freezed da igualdad, `copyWith` y JSON
  con menos código que built_value.
- HTTP va por `package:http`, dentro de un solo servicio del cliente de la API.

## Estado

Estándares: [*Simple app state management*](../estandares/flutter/state-mgmt-simple.md) de Flutter
y [provider](../estandares/pub/provider/README.md).

- Los ViewModels son `ChangeNotifier`. Vienen con el SDK, y provider ya es la inyección de
  dependencias.

## Tema

Estándar: [*Use themes to share colors and font styles*](../estandares/flutter/themes.md) de
Flutter.

- El tema claro y el oscuro salen de `ui/core/themes/`, y `themeMode` es `ThemeMode.system`.

## Almacenamiento

Estándares: [shared_preferences](../estandares/pub/shared_preferences/README.md) y
[flutter_secure_storage](../estandares/pub/flutter_secure_storage/README.md).

- Las preferencias usan `SharedPreferencesAsync`. Sin caché, cada lectura trae el valor actual.
