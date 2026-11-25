# ADR-0246 · Flutter pasa a la 3.50 con material_ui, y Flet sigue en la 3.47

- **Estado:** Aceptada
- **Fecha:** 2026-11-25
- **Alcance:** [`stack.md`](../stack.md), [`flutter.md`](../plataformas/flutter.md), `plantilla/flutter/`,
  `plantilla/scripts/tokens.py`, `plantilla/.github/workflows/` y `scripts/verificar.py`

## Contexto

El [ADR-0244](0244-una-version-se-queda-solo-con-una-razon-sobre-la-ultima.md) dejó Flutter en la
3.47.9 porque la 3.50 declara obsoleto `package:flutter/material.dart`. material_ui es la misma
biblioteca, del equipo de Flutter, separada del SDK.

Comprobado el 2026-11-25 con Flutter 3.50.1, Dart 3.14.0 y material_ui 1.11.1:

- Los paquetes de `stack.md` resuelven, build_runner y swagger_parser generan, y una app con
  Riverpod, `gen-l10n` y el `colors.dart` de `tokens.py` pasa `dart analyze --fatal-infos` con el
  `analysis_options.yaml` de la plantilla, y `dart format`.
- `gen-l10n` importa los delegados de flutter_localizations, que son obsoletos: sin excluir
  `lib/l10n/app_localizations*.dart`, el analizador falla.
- Con `AppLocalizations.localizationsDelegates`, un widget que pide `MaterialLocalizations` en español
  falla. Con `AppLocalizations.delegate` y `GlobalMaterialLocalizations.delegates` de material_ui,
  `cancelButtonLabel` da «Cancelar».
- Una subclase de `MinimumTextContrastGuideline` y `androidTapTargetGuideline` funcionan igual.
- `flutter analyze` ya corre riverpod_lint.
- El APK de depuración construye con el JDK 25.0.5, Gradle 9.9.2, AGP 9.5.2 y Kotlin 2.4.21.

Flet 1.1.3 pide Flutter 3.47 (leído en su `.fvmrc`, 3.47.9).

## Decisión

1. **Flutter es la 3.50.1 y Dart, la 3.14.0**, y entra material_ui 1.11.1. Reemplaza el punto 3 del
   ADR-0244.
2. **Los widgets y el tema de Material son los de material_ui**, también en lo que genera `tokens.py`.
3. **`localizationsDelegates` lleva los de material_ui**, y no la lista de `gen-l10n`.
4. **El analizador no revisa lo que genera `gen-l10n`.**
5. **Flet tiene su fila de Flutter**, y `verificar.py` pide en los workflows el Flutter de cada tipo
   de pieza.
6. `flutter.md` deja de decir que `flutter analyze` no corre los plugins.

## Consecuencias

- Una app cambia sus imports con `dart fix --apply --code=migrate_design_widgets`.
- flutter_localizations sigue declarado: lo importa lo que genera `gen-l10n`.
- Un repositorio con Flutter y con Flet instala dos versiones de Flutter.
- Sin confirmar: iOS, el escritorio, la web y un teléfono con Flutter 3.50.1.

## Descartado

- **cupertino_ui:** ninguna página usa sus widgets.
- **Apagar `deprecated_member_use`:** esconde también lo demás que Flutter retira.
