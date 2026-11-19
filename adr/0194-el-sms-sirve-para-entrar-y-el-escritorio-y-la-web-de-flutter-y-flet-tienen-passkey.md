# ADR-0194 · El SMS sirve para entrar, y el escritorio y la web de Flutter y Flet tienen passkey

- **Estado:** Aceptada. El usuario aprobó la tabla de métodos por pieza, pidió que el SMS sirva para
  entrar donde no se puede la passkey, sin avisos al usuario, y que una app en el navegador siga lo
  más coherente con las demás convenciones, que la recuperación por SMS no espere, que haya
  contraseña en todas las piezas y que el usuario elija en la pantalla el código por SMS o la
  contraseña (2026-11-19)
- **Fecha:** 2026-11-19
- **Alcance:** [`plataformas/autenticacion.md`](../plataformas/autenticacion.md), «Código de
  autorización», «Código por SMS», «Cuentas», «Recuperación» y «Sesión»;
  [`plataformas/flutter.md`](../plataformas/flutter.md), [`plataformas/flet.md`](../plataformas/flet.md)
  y [`plataformas/qt.md`](../plataformas/qt.md), «Código de autorización» y «Código por SMS»;
  [`stack.md`](../stack.md)

## Contexto

- No todos los teléfonos tienen passkeys, y en el teléfono el código por SMS se completa solo.
- RFC 8252 §7.3 da a una app de escritorio el retorno a la interfaz de loopback, con cualquier
  puerto. Ni Flutter, ni Flet, ni Qt tienen una API oficial de passkeys en escritorio.
- `autenticacion.md` ya pedía que en la web ningún token quedara al alcance de un script. Una app de
  Flutter o de Flet en el navegador que canjeara el código guardaría sus tokens en el navegador.
- flutter_appauth no tiene Windows ni Linux.
- Una tableta, o un iPhone, puede no tener SIM, y solo el usuario sabe con certeza si su
  dispositivo recibe SMS: iOS no dice si hay SIM.
- iOS ofrece sobre el teclado el código de un SMS con `@<host> #<código>` en un campo de tipo
  `oneTimeCode` solo si el host es uno de los dominios asociados de la app. `TextFieldPinAutoFill`,
  de sms_autofill, ya lleva `AutofillHints.oneTimeCode`. Leído, sin comprobar en un iPhone.
- Comprobado el 2026-11-19 en Windows 10, contra un servidor de prueba con la página de
  autorización, el endpoint de token y los dos endpoints de la app en el navegador:
  - Flet 1.1.2 en escritorio abre la petición en el navegador del sistema, recibe el retorno en
    `asyncio.start_server` sobre `127.0.0.1` con un puerto libre, y canjea el código.
  - `QOAuth2AuthorizationCodeFlow` de PySide6 6.12.0 manda `S256`, no manda `scope` ni secreto, y
    su `QOAuthHttpServerReplyHandler` pone `http://127.0.0.1:{puerto}/callback` en la URI de retorno.
  - `AuthorizationCodeGrant` de oauth2 2.0.5, como programa de Dart con un `HttpServer` en
    loopback, hace lo mismo. La app de Flutter de escritorio no se construyó: falta Visual Studio.
  - En Chrome, una app de `flutter build web` y una de `flet build web` servidas en el mismo origen
    van al endpoint del servidor en su misma pestaña, vuelven con la cookie `HttpOnly` y
    `SameSite=Strict`, que `document.cookie` no ve, y sus peticiones a `/api` la llevan. En
    Pyodide, httpx no acepta la URL relativa `/api/me`.

## Decisión

1. **Una cuenta entra con una contraseña, una passkey o un código por SMS.** Los fallos del código
   cuentan entre los fallos consecutivos del teléfono. La app no avisa del riesgo del SMS ni ofrece
   otro autenticador al registrar un teléfono.
2. **Una app de escritorio usa la passkey en el navegador del sistema y recibe el retorno en
   `http://127.0.0.1:{puerto}/<ruta>`**, y el servidor acepta cualquier puerto en esa URI.
3. **Una app que corre en el navegador hace el flujo por el servidor, en su misma pestaña**: un
   endpoint del servidor crea el `state` y el `code_verifier`, otro recibe el retorno, canjea el
   código y deja la cookie de sesión de la web, y vuelve a la app con un 303. La app presenta la
   sesión con esa cookie, como la web.
4. La tabla de «Cuentas» da a cada pieza passkey, contraseña y código por SMS.
5. **Una cuenta con passkey espera 24 horas solo si se recupera con el código del correo.** El del
   teléfono se aplica en el momento: con él la cuenta ya entra.
6. **En escritorio, Flutter hace el flujo con oauth2 y un `HttpServer` en loopback, Flet con
   `asyncio.start_server`, y Qt con `QOAuth2AuthorizationCodeFlow` y `QOAuthHttpServerReplyHandler`.**
7. **En la web, Flutter abre el endpoint con `window.location.assign()` y Flet con
   `launch_url(..., web_only_window_name="_self")`, y la app de la web de Flet es la de
   `flet build web`.** Las apps que corren en el navegador se sirven en el mismo origen que la web.
8. **La pantalla para entrar ofrece primero la passkey, si el dispositivo la tiene, y luego el
   código por SMS y la contraseña, entre los que elige el usuario.** La app guarda en el dispositivo
   el último método con que entró y lo ofrece primero la próxima vez. En iOS, la app declara el host
   del SMS en sus dominios asociados, y ese host sirve `apple-app-site-association` con la app en
   `webcredentials.apps`.

Reemplaza el punto 1 del
[ADR-0185](0185-una-cuenta-entra-con-passkey-o-contrasena-y-cada-repositorio-elige-cuales-ofrece.md)
en el código por SMS, y el punto 1 del
[ADR-0184](0184-la-uri-de-retorno-es-https-donde-se-puede-y-cada-pieza-elige-sus-plataformas.md) en
las apps de escritorio.

## Consecuencias

- El servidor tiene dos endpoints más para las apps que corren en el navegador.
- Flutter suma oauth2, url_launcher y package:web.
- Una app que corre en el navegador no refresca: ante un 401 vuelve a entrar, como la web.

## Descartado

- **El aviso de NIST SP 800-63B-4 §3.2.9 al registrar un teléfono:** molesta al usuario, y la app
  usa la passkey donde puede.
- **Una app en el navegador con tokens, como una app instalada:** dejaría los tokens al alcance de un
  script.
- **Quitar la contraseña donde el código se completa solo, y detectar la SIM:** una tableta o un
  iPhone sin SIM quedaría sin contraseña, e iOS no dice si hay SIM. La versión que detecta la SIM
  quedó en la rama `deteccion-sim`.
- **Pantallas propias de la app en el navegador contra la API:** Flet no puede llamar a WebAuthn
  desde Python, así que la passkey igual tendría que ir a una página del servidor.
