# Flutter

Cómo se construye una app en Flutter.

## Layout de `lib/`

Por funcionalidad, no por tipo de archivo:

```
lib/
  main.dart
  app.dart              widget raíz: arranque, bloqueo, navegación
  core/
    theme/              tokens y ThemeData
    network/            cliente autorizado, timeouts, backoff de reconexión
    storage/            preferencias, base cifrada, claves de almacenamiento
    platform/           lo que toca el sistema operativo
    widgets/            widgets compartidos entre features
  features/
    <feature>/          pantallas, controladores y estado de esa funcionalidad
```

El código compartido entre dos apps del mismo producto va en un paquete local con su propio
`pubspec.yaml`. El código que necesita canal nativo va en un plugin local bajo `plugins/`.

## Tema

Una clase con constructor privado y solo `static const`, y **ningún color literal fuera de ella**:

```dart
class AppPalette {
  AppPalette._();

  static const background = Color(0xFF060E1F);
  static const primary    = Color(0xFF2B8BF5);
  static const success    = Color(0xFF4CAF50);
  static const danger     = Color(0xFFF44336);
}
```

Tipografía con `google_fonts`. El tema se arma una vez en `ThemeData` y las pantallas leen del tema,
no de la paleta. Si el producto también tiene superficie web, la paleta es la misma que la de UnoCSS
y el archivo dice de cuál es espejo.

## Estado

`ChangeNotifier`, `ValueNotifier` y `StreamBuilder`, de Flutter. **Sin paquete de gestión de
estado**: agregar uno exige un ADR que diga qué resuelve que lo de Flutter no resuelva.

## Red

```
core/network/
  authorized_api_client.dart   adjunta el token y refresca la sesión
  timeout_client.dart          ningún request queda colgado
  reconnect_backoff.dart       reconexión del socket con espera creciente
  client_version.dart          entiende el 426 del servidor y manda a actualizar
```

Ante un 401 se refresca la sesión **una sola vez** y se reintenta una vez. Nunca un bucle de
reintentos silencioso.

## Almacenamiento

| Qué | Dónde |
|---|---|
| Claves y tokens | `flutter_secure_storage` |
| Datos sensibles locales | Base cifrada (`sqlcipher_flutter_libs`) |
| Preferencias de interfaz | `shared_preferences` |

Las claves de almacenamiento se declaran en un solo archivo (`core/storage/storage_keys.dart`), no
como cadenas sueltas repartidas por el código.

## Analizador

`analysis_options.yaml` sobre `package:flutter_lints`, con las reglas que atrapan bugs reales. Nunca
se apaga una regla para que el código existente pase: se arregla el código.

```yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  errors:
    unawaited_futures: error          # un future sin await es un bug de concurrencia
    dead_code: error
    unrelated_type_equality_checks: error
  exclude:
    - build/**
```

Y en el linter, agrupadas por lo que protegen:

| Grupo | Reglas |
|---|---|
| Asincronía y recursos | `unawaited_futures`, `cancel_subscriptions`, `close_sinks`, `unnecessary_await_in_return` |
| Tipado | `always_declare_return_types`, `avoid_dynamic_calls`, `prefer_typing_uninitialized_variables` |
| Inmutabilidad | `prefer_final_locals`, `prefer_final_in_for_each`, `avoid_setters_without_getters` |
| Estilo | `prefer_single_quotes`, `directives_ordering`, `sort_pub_dependencies`, `unnecessary_parenthesis`, `unnecessary_lambdas` |
| Higiene | `avoid_print`, `secure_pubspec_urls`, `throw_in_finally` |

`avoid_slow_async_io` queda fuera a propósito: está pensada para CLIs, y en Flutter el IO asíncrono
es lo correcto para no bloquear el frame.

## Mapas: trampas verificadas

Comprobadas. No se vuelven a investigar ni se proponen teorías nuevas sobre ellas.

| Trampa | Qué ocurre |
|---|---|
| La rueda del mouse no hace zoom en `flutter_map` | No tiene arreglo desde la app |
| Una capa encima no gana el arrastre | El mapa acepta el gesto a 18 px y el paneo normal a 36: hay que aceptar en el *pointer down* |
| Las teselas relanzan fallos de red | Un `HandshakeException` que parece del backend propio puede venir de las teselas de OSM; nace en un `ImageProvider` y ningún try/catch la atrapa |

## CI

```yaml
- run: flutter analyze
- run: flutter test
```
