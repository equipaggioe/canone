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

## Accesibilidad

Estándares: de Flutter, [*Accessibility*](../estandares/flutter/accessibility.md),
[*UI design and styling*](../estandares/flutter/accessibility-ui-design.md),
[*Assistive technologies*](../estandares/flutter/accessibility-assistive.md) y
[*Accessibility testing*](../estandares/flutter/accessibility-testing.md).

Contrato: [transversal.md](transversal.md#accesibilidad).

- Cada pantalla tiene una prueba de widget con las cuatro guías: `androidTapTargetGuideline`,
  `iOSTapTargetGuideline`, `labeledTapTargetGuideline` y `textContrastGuideline`.

## Almacenamiento

Estándares: [shared_preferences](../estandares/pub/shared_preferences/README.md) y
[flutter_secure_storage](../estandares/pub/flutter_secure_storage/README.md).

- Las preferencias usan `SharedPreferencesAsync`. Sin caché, cada lectura trae el valor actual.
- El token de refresco que pide [transversal.md](transversal.md#sesión) va en
  flutter_secure_storage.

## Código por SMS

Estándar: la sección *Usage* de [sms_autofill](../estandares/pub/sms_autofill/README.md).

Contrato: [transversal.md](transversal.md#código-por-sms).

- El campo del código es `TextFieldPinAutoFill`: lleva una `InputDecoration`, y se ve como los
  demás campos del tema.

## Idiomas

Estándar: [*Internationalizing Flutter apps*](../estandares/flutter/internationalization.md).

Contrato: [transversal.md](transversal.md#idiomas).

## Mapas

Estándar: [flutter_map](../estandares/pub/flutter_map/README.md).

Contrato: [transversal.md](transversal.md#mapas).

## Pagos

Contrato: [transversal.md](transversal.md#pagos).

- Con Stripe, la hoja de pago es `PaymentSheet` de `flutter_stripe`.

## Tema

Estándar: [*Use themes to share colors and font styles*](../estandares/flutter/themes.md) de
Flutter.

- El tema claro y el oscuro salen de `ui/core/themes/`, y `themeMode` es `ThemeMode.system`.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Objetivos, etiquetas y contraste | Las guías de `flutter_test` en cada pantalla |
