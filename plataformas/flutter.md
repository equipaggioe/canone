# Flutter

Aplica a un repositorio con app en Flutter. Hoy: `navetta` (`mobile-driver`, `mobile-passenger`,
`mobile-shared`) y `vettore` (`app`).

Leído de esas cuatro. **`vettore/app` es la referencia**: es la única que habla con un servidor real,
tiene analizador configurado, plugins propios y almacenamiento cifrado. `navetta` todavía corre con
datos mock (`mobile-shared/lib/data/mock_data.dart`) y su `AuthService` acepta cualquier credencial.

## Layout de `lib/`

El de `vettore/app`, por funcionalidad:

```
lib/
  main.dart
  app.dart              el widget raíz: arranque, bloqueo, navegación
  core/
    theme/              tokens y ThemeData
    network/            cliente autorizado, timeouts, backoff de reconexión
    storage/            preferencias, base cifrada, claves de almacenamiento
    platform/           lo que toca el sistema operativo
    widgets/            widgets compartidos entre features
    crypto/  files/  calls/  diagnostics/
  features/
    <feature>/          pantallas, controladores y estado de esa funcionalidad
```

Una carpeta por funcionalidad, no por tipo de archivo. `navetta` usa `screens/` plano, que se
sostiene mientras la app tenga pocas pantallas pero no escala.

El código compartido entre dos apps del mismo producto va en un paquete local con su propio
`pubspec.yaml` (`navetta/mobile-shared`), y el código que necesita canal nativo va en un plugin
local bajo `plugins/` (`vettore_location_service`, `vettore_capture_service`).

## Tema

Una clase con constructor privado y solo `static const`, y **ningún color literal fuera de ella**:

```dart
class AppPalette {
  AppPalette._();

  static const background = Color(0xFF060E1F);
  static const primary = Color(0xFF2B8BF5);
  static const success = Color(0xFF4CAF50);
}
```

Es lo que hacen las dos apps (`AppPalette` en vettore, `NavettaTheme` en navetta). Tipografía con
`google_fonts`. El tema se arma una vez en `ThemeData` y las pantallas leen del tema, no de la
paleta.

Si el producto también tiene panel web, la paleta es la misma que la de UnoCSS. presenze ya lo
documenta así entre sus tres frontends.

## Estado

`ChangeNotifier` / `ValueNotifier` y `StreamBuilder`, de Flutter. **Sin paquete de gestión de
estado**: `vettore/app` no usa ninguno en 25 archivos con notificadores. `navetta` usa `provider`,
que es la divergencia: se puede mantener donde ya está, pero no se agrega a una app nueva sin un
ADR que diga qué resuelve.

## Red

`core/network/` de vettore es el modelo:

| Archivo | Qué resuelve |
|---|---|
| `authorized_api_client.dart` | Adjunta el token y refresca la sesión |
| `timeout_client.dart` | Ningún request queda colgado |
| `reconnect_backoff.dart` | Reconexión del socket con espera creciente |
| `client_version.dart` | La app entiende el `426` del servidor y manda a actualizar |

Los errores se leen por `errorCode` del sobre del servidor, nunca por `detail` — ver
[fastapi.md](fastapi.md).

## Almacenamiento

- `flutter_secure_storage` para claves y tokens.
- Base local cifrada (`sqlcipher_flutter_libs`) para lo que sea sensible.
- `shared_preferences` solo para preferencias de interfaz.
- Las claves de almacenamiento se declaran en un solo archivo (`core/storage/storage_keys.dart`), no
  como cadenas sueltas.

## Analizador

`analysis_options.yaml` sobre `package:flutter_lints`, con las reglas que atrapan bugs reales. El de
`vettore/app` es el canónico; el de `navetta` hace lo contrario —apaga `prefer_const_constructors`—
y hay que reemplazarlo.

Lo que sube a error, no a aviso:

```yaml
analyzer:
  errors:
    unawaited_futures: error      # un future sin await es un bug de concurrencia
    dead_code: error
    unrelated_type_equality_checks: error
```

Y las reglas del linter, agrupadas por lo que protegen: asincronía y recursos
(`cancel_subscriptions`, `close_sinks`), tipado (`always_declare_return_types`,
`avoid_dynamic_calls`), inmutabilidad (`prefer_final_locals`), estilo (`prefer_single_quotes`,
`directives_ordering`, `sort_pub_dependencies`) e higiene (`avoid_print`, `secure_pubspec_urls`,
`throw_in_finally`).

## Trampas verificadas

No se vuelven a investigar. Las tres son de `flutter_map`, que usan las dos apps:

| Trampa | Qué ocurre |
|---|---|
| La rueda del mouse no hace zoom | No tiene arreglo desde la app |
| Una capa encima no gana el arrastre | El mapa acepta el gesto a 18 px y el paneo normal a 36: hay que aceptar en el *pointer down* |
| Las teselas relanzan fallos de red | Un `HandshakeException` que parece del backend propio puede venir de las teselas de OSM; nace en un `ImageProvider` y ningún try/catch la atrapa |

## CI

```yaml
- run: flutter analyze
- run: flutter test
```

Hoy ninguna de las dos apps corre en CI.
