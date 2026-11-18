# ADR-0182 · Flutter traduce los errores, reintenta y autentica en un solo `http.Client`

- **Estado:** Aceptada. El usuario pidió aplicar lo recomendado en la revisión de `flutter.md`
  (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/flutter.md`](../plataformas/flutter.md),
  [`plataformas/autenticacion.md`](../plataformas/autenticacion.md), «Código de autorización»,
  y [`stack.md`](../stack.md)

## Contexto

La revisión de `flutter.md` del 2026-11-18 encontró contratos de `transversal.md` y de
`autenticacion.md` que la página no resolvía, y convenciones que no cumplían las dos condiciones de
`plataformas/README.md`.

- Leído en swagger_parser 2.3.0, `dart_package_http_builder.dart`: ante una respuesta que no es
  2xx, el cliente generado cancela el cuerpo y lanza `ClientException('HTTP <status>')`, sin el
  `type` ni el `traceId` del problema.
- Comprobado con Dart 3.13.4: `DateTime.now().toIso8601String()` da `2026-11-18T05:20:27.594917`,
  sin desfase, y `HttpClient().userAgent` vale `Dart/3.13 (dart:io)`.
- Leído en http 1.6.0, `retry.dart`: `RetryClient` reintenta por defecto solo un 503, ningún fallo
  de red y sin jitter, y `whenError` no recibe la petición.
- Leído en Flutter 3.47.9, `LocalizationPlugin.java`: Flutter toma los idiomas de la configuración
  de la app, que es donde Android pone el idioma por app.
- Leído en flutter_secure_storage 11.2.0: sus preferencias son `FlutterSecureStorage.xml` y
  `FlutterSecureKeyStorage.xml`.

## Decisión

1. **La app tiene un solo `http.Client`**, una subclase de `BaseClient` en un provider con
   `keepAlive: true`. Pone el `User-Agent` de pieza, el token de acceso y `Accept-Language`,
   refresca la sesión ante un 401 con un solo refresco en curso, y convierte una respuesta que no
   es 2xx en la excepción tipada del sobre.
2. **Los reintentos van por `RetryClient`**, que recibe solo las peticiones idempotentes, ante un
   502, un 503, un 504 o una `ClientException`, con espera exponencial y jitter.
3. **Un `DateTime` que va al servidor está en UTC.**
4. **El WebSocket va por `WebSocket.connect` de `dart:io`.**
5. **El usuario elige el idioma en los ajustes del sistema para la app**: en Android, con un
   `locales_config.xml` escrito a mano, y en iOS, con las *Localizations* de Xcode.
6. **Una lista paginada guarda en su ViewModel los elementos y el `nextPageToken`.**
7. **El permiso de notificaciones se pide después de una acción del usuario**, con
   `requestPermission()`.
8. **En Android, el retorno del login llega por App Links**: el `intent-filter` de
   `RedirectUriReceiverActivity` con la URI `https` y `autoVerify`, y `assetlinks.json` con
   `delegate_permission/common.handle_all_urls`.
9. **La copia de seguridad de Android excluye las preferencias de flutter_secure_storage**, con
   `data_extraction_rules.xml` y `backup_rules.xml`.
10. **Salen como fuentes *Internationalizing Flutter apps*, que es un tutorial y no toma
    posición, y los README de flutter_secure_storage y de shared_preferences**, que no llegan a
    tres convenciones. Lo que se queda de ellos pasa a convención propia.
11. **Salen las convenciones que tenían una sola forma correcta o repetían otra página**: la lista
    de paquetes de `pubspec.yaml`, `package:http`, el JSON de freezed, el backend de DataStore,
    `ensureInitialized()`, `keychain-access-groups`, el `pubspec.yaml` y los delegates de idiomas,
    maplibre_gl, `Uuid().v4()`, el push con firebase_messaging y el rechazo de los campos
    desconocidos. En `stack.md`, el «Para» de lo que la página ya no nombra pasa a «—».

## Consecuencias

- Nada de esto corrió en una app real. Lo que queda sin decidir, como el login en iOS y los canales
  de notificación, está en [pendientes/firma-y-publicacion.md](../pendientes/firma-y-publicacion.md).
- El idioma por app de Android solo existe desde la API 33: antes, la app sigue el idioma del
  sistema.

## Descartado

- **web_socket_channel:** `dart:io` ya trae `WebSocket`, con cabeceras en el handshake.
- **Generar `locales_config.xml` con `generateLocaleConfig`:** AGP lo arma con las carpetas
  `res/values-<idioma>/`, y los textos de la app están en los ARB.
- **`allowBackup="false"`:** la app perdería también la copia de las demás preferencias.
