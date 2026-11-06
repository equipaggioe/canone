# Flutter

> **En desarrollo; no se implementa:** [README.md](README.md#en-desarrollo).

Una app en Flutter.

## Proyecto

- Flutter 3.47.9, con Dart 3.13.7.
- shared_preferences 2.5.6, flutter_secure_storage 11.2.0, provider 6.1.5+1 y flutter_lints 6.0.0: `pubspec.yaml` los declara exactos o con `^`.
- Gradle, AGP y Kotlin son los de [android.md](android.md#proyecto), con su `gradle-wrapper.properties` en `android/gradle/wrapper/`. AGP y Kotlin se declaran en `android/settings.gradle.kts`.

## Estilo

Estándares: [*Effective Dart*](../fuentes/dart/effective-dart-index.md): [*Style*](../fuentes/dart/effective-dart-style.md), [*Documentation*](../fuentes/dart/effective-dart-documentation.md), [*Usage*](../fuentes/dart/effective-dart-usage.md) y [*Design*](../fuentes/dart/effective-dart-design.md).

- `dart format` usa líneas de 99.

## Analizador

- El analizador incluye la [lista de flutter_lints](https://raw.githubusercontent.com/flutter/packages/flutter_lints-v6.0.0/packages/flutter_lints/lib/flutter.yaml) y activa `strict-casts`, `strict-inference` y `strict-raw-types`, y CI corre `flutter analyze --fatal-infos`: los tipos se revisan como con Pyrefly en modo strict.

Plantilla: [plantilla/flutter/](../plantilla/flutter/): `analysis_options.yaml`, con el analizador y el ancho de `dart format`, que se copia sin editar, y `.gitignore`.

## Arquitectura

Estándares: [*Common architecture concepts*](../fuentes/flutter/app-architecture-concepts.md), [*Guide to app architecture*](../fuentes/flutter/app-architecture-guide.md) y [*Architecture recommendations and resources*](../fuentes/flutter/app-architecture-recommendations.md) de Flutter, con sus [recomendaciones](../fuentes/flutter/architecture-recommendations.yml).

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

- Las carpetas llevan el nombre del componente de arquitectura, como pide la recomendación de nombres.
- Los modelos se generan con freezed y json_serializable. freezed da igualdad, `copyWith` y JSON con menos código que built_value.
- HTTP va por `package:http`, dentro de un solo servicio del cliente de la API.

## Estado

Estándares: [*Simple app state management*](../fuentes/flutter/state-mgmt-simple.md) de Flutter y [provider](../fuentes/pub/provider/README.md).

- Los ViewModels son `ChangeNotifier`. Vienen con el SDK, y provider ya es la inyección de dependencias.

## Accesibilidad

Estándar: [*Accessibility*](../fuentes/flutter/accessibility.md) de Flutter.

Contrato: [transversal.md](transversal.md#accesibilidad).

- Cada pantalla tiene una prueba de widget con las cuatro guías: `androidTapTargetGuideline`, `iOSTapTargetGuideline`, `labeledTapTargetGuideline` y `textContrastGuideline`. [Flutter](https://raw.githubusercontent.com/flutter/website/afe82c4e59af75731eb83c2138a93837934f65b8/sites/docs/src/content/ui/accessibility/accessibility-testing.md)

## Almacenamiento

Estándares: [shared_preferences](../fuentes/pub/shared_preferences/README.md) y [flutter_secure_storage](../fuentes/pub/flutter_secure_storage/README.md).

- Las preferencias usan `SharedPreferencesAsync`. Sin caché, cada lectura trae el valor actual.
- El token de refresco que pide [transversal.md](transversal.md#sesión) va en flutter_secure_storage.

## Código por SMS

Contrato: [transversal.md](transversal.md#código-por-sms).

- El campo del código es `TextFieldPinAutoFill`: lleva una `InputDecoration`, y se ve como los demás campos del tema.

## Idiomas

Estándar: [*Internationalizing Flutter apps*](../fuentes/flutter/internationalization.md).

Contrato: [transversal.md](transversal.md#idiomas).

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

## Pagos

Contrato: [transversal.md](transversal.md#pagos).

- Con Stripe, la hoja de pago es `PaymentSheet` de `flutter_stripe`.

## Push

Contrato: [transversal.md](transversal.md#push).

## Tema

> **En desarrollo; no se implementa:** [transversal.md](transversal.md#tema).

Contrato: [transversal.md](transversal.md#tema).

- El tema claro y el oscuro usan `lightColorScheme` y `darkColorScheme`, generados en `ui/core/themes/colors.dart`, y `themeMode` es `ThemeMode.system`.
- Los tamaños van en `ui/core/themes/`, sin tamaños literales fuera de él.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Gradle, AGP y Kotlin | [scripts/verificar.py](../scripts/verificar.py) |
| Flutter en CI y los paquetes de «Proyecto» | [scripts/verificar.py](../scripts/verificar.py) |
| La lista de flutter_lints y los tipos estrictos | `flutter analyze --fatal-infos` en CI |
| Objetivos, etiquetas y contraste | Las guías de `flutter_test` en cada pantalla |
