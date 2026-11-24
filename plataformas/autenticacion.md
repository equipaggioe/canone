# Autenticación

Cómo se registra una cuenta, cómo entra y cómo mantiene su sesión: lo que hace el servidor y lo que cumplen con él sus clientes. Lo propio de cada cliente va en su página.

## Código de autorización

Estándares: [RFC 6749](../fuentes/rfc/rfc6749.txt), [RFC 7636](../fuentes/rfc/rfc7636.txt), [RFC 8252](../fuentes/rfc/rfc8252.txt) y [RFC 9700](../fuentes/rfc/rfc9700.txt).

- Una app usa la passkey con la API de su sistema: una de Android, con Credential Manager, y una de Flutter o de Flet en el teléfono, en Windows o en macOS, con el plugin `passkey` de la plantilla, que llama a Credential Manager en Android, a AuthenticationServices en iOS y en macOS y a la API de WebAuthn en Windows. Una app de Linux o de Qt la usa en el navegador del sistema, que le devuelve un código de autorización.
- Una app que corre en el navegador hace el flujo por el servidor, en su misma pestaña: abre un endpoint del servidor que crea el `state` y el `code_verifier` y redirige a la petición de autorización, y la URI de retorno es otro endpoint del servidor, que canjea el código, deja la cookie de sesión de la web y vuelve a la app con un 303.
- En ese flujo, el endpoint que lo inicia guarda el `state` y el `code_verifier` en Valkey, bajo un id que deja en una cookie `__Host-` `Secure`, `HttpOnly` y `SameSite=Strict`, y el endpoint de retorno los toma una sola vez y borra la cookie.
- El código vive en Valkey, con la cuenta.
- Una app de escritorio recibe el retorno solo en `http://127.0.0.1:{puerto}/<ruta>`, y no en `[::1]`: toda máquina de escritorio tiene loopback IPv4.
- El servidor sirve la página de autorización en `GET /api/auth/authorize`, con su estilo y su script en la misma página y el texto traducido con su catálogo. La petición espera en Valkey 10 minutos la passkey, que la página manda a `POST /api/auth/authorize`; el servidor responde la URI de retorno con el código, y la página va a ella.
- Los clientes son la constante `CLIENTS` de `services/clients.py`, cada uno con su `client_id` y su URI de retorno. La web es el cliente `web`, con una URI de retorno por superficie de `domain`: `https://<superficie>/api/auth/web/return`.
- El flujo de la web empieza en `GET /api/auth/web/start`, su cookie es `__Host-flow`, y al volver la app va a `/` de su superficie.
- Un `client_id` o una `redirect_uri` repetidos muestran el error en el navegador y no redirigen: no se sabe a dónde volver.
- El endpoint de autorización autentica al usuario en cada petición, aunque el navegador tenga abierta una sesión de la web ([RFC 8252 §8.6](../fuentes/rfc/rfc8252.txt)).
- La petición de autorización lleva `code_challenge` con `code_challenge_method` `S256`. Sin él, o con `plain`, responde `invalid_request` ([RFC 7636 §4.2](../fuentes/rfc/rfc7636.txt) y [§4.4.1](../fuentes/rfc/rfc7636.txt)).
- El código son 256 bits aleatorios, vence a los 10 minutos, queda ligado al `client_id` y a la URI de retorno, y vale una sola vez. Al canjearlo queda marcado como usado, con el id de la sesión que creó, y presentarlo de nuevo responde `invalid_grant` y borra esa sesión ([RFC 6749 §4.1.2](../fuentes/rfc/rfc6749.txt) y [§10.10](../fuentes/rfc/rfc6749.txt)).
- Los endpoints no usan `scope`: una petición que lo trae responde `invalid_scope`, y el token da el acceso entero de la cuenta ([RFC 6749 §3.3](../fuentes/rfc/rfc6749.txt), [§4.1.2.1](../fuentes/rfc/rfc6749.txt) y [§5.2](../fuentes/rfc/rfc6749.txt)).
- El endpoint de autorización acepta `GET`, y el de token, solo `POST` en `application/x-www-form-urlencoded` ([RFC 6749 §3.1](../fuentes/rfc/rfc6749.txt), [§3.2](../fuentes/rfc/rfc6749.txt) y [§4.1.3](../fuentes/rfc/rfc6749.txt)).
- `response_type` es `code`, y otro valor responde `unsupported_response_type` ([RFC 6749 §3.1.1](../fuentes/rfc/rfc6749.txt) y [§4.1.2.1](../fuentes/rfc/rfc6749.txt)).
- El canje responde un 200 en JSON con `access_token`, `token_type` `Bearer`, `expires_in` con lo que dura el token de acceso y `refresh_token`, y con `Cache-Control: no-store` y `Pragma: no-cache` ([RFC 6749 §5.1](../fuentes/rfc/rfc6749.txt)).
- Una app de escritorio abre el puerto en la interfaz de loopback al empezar la petición y lo cierra al recibir la respuesta ([RFC 8252 §8.3](../fuentes/rfc/rfc8252.txt)).
- La app abre la petición de autorización en el navegador del sistema, y nunca en un web-view ([RFC 8252 §5](../fuentes/rfc/rfc8252.txt), [§6](../fuentes/rfc/rfc8252.txt) y [§8.12](../fuentes/rfc/rfc8252.txt)).
- La página de autorización no carga recursos ni enlaces de otros sitios ([RFC 9700 §4.2.4](../fuentes/rfc/rfc9700.txt)).
- Quien inicia el flujo crea el `code_verifier` con 32 bytes aleatorios en base64url ([RFC 7636 §4.1](../fuentes/rfc/rfc7636.txt) y [§7.1](../fuentes/rfc/rfc7636.txt)).
- La app manda un `state` aleatorio y rechaza la respuesta que no llega a la URI de retorno o con el `state` de su petición ([RFC 8252 §8.9](../fuentes/rfc/rfc8252.txt) y [§8.10](../fuentes/rfc/rfc8252.txt)).
- La app es un cliente público: está registrada en el servidor con su `client_id` y su URI de retorno completa, y no tiene secreto ([RFC 8252 §8.4](../fuentes/rfc/rfc8252.txt) y [§8.5](../fuentes/rfc/rfc8252.txt)).
- El servidor compara la URI de retorno con la registrada como cadena exacta, salvo el puerto de una URI de loopback, que acepta cualquiera ([RFC 8252 §7.3](../fuentes/rfc/rfc8252.txt) y [§8.4](../fuentes/rfc/rfc8252.txt)).
- Una petición de autorización sin `client_id`, o con un `client_id` o una URI de retorno que no son los registrados, muestra el error en el navegador y no redirige ([RFC 6749 §3.1.2.4](../fuentes/rfc/rfc6749.txt) y [§4.1.2.1](../fuentes/rfc/rfc6749.txt)).
- Los dos endpoints toman un parámetro sin valor como ausente e ignoran el que no conocen. Uno repetido, o uno obligatorio que falta, responde `invalid_request`, nunca 422 ([RFC 6749 §3.1](../fuentes/rfc/rfc6749.txt), [§3.2](../fuentes/rfc/rfc6749.txt), [§4.1.2.1](../fuentes/rfc/rfc6749.txt) y [§5.2](../fuentes/rfc/rfc6749.txt)).
- El canje lleva `grant_type=authorization_code`, el `code`, el `client_id` del código y, si la petición de autorización llevó `redirect_uri`, la misma. Responde `invalid_grant` si el `client_id` o la URI de retorno no coinciden ([RFC 6749 §4.1.3](../fuentes/rfc/rfc6749.txt) y [§5.2](../fuentes/rfc/rfc6749.txt)).
- El canje lleva el `code_verifier`, y responde `invalid_grant` si su SHA-256 en base64url no es el `code_challenge` ([RFC 7636 §4.5](../fuentes/rfc/rfc7636.txt) y [§4.6](../fuentes/rfc/rfc7636.txt)).
- Un error del endpoint de token es un 400 en JSON con `error`, uno de los códigos de su lista ([RFC 6749 §5.2](../fuentes/rfc/rfc6749.txt)).
- Una respuesta que redirige después de recibir una credencial usa 303, nunca 307 ([RFC 9700 §4.12](../fuentes/rfc/rfc9700.txt)).
- Ni el servidor ni la web redirigen a una URL que llega en un parámetro y no está registrada ([RFC 9700 §2.1](../fuentes/rfc/rfc9700.txt) y [§4.11.1](../fuentes/rfc/rfc9700.txt)).

Plantilla: de [plantilla/server/](../plantilla/server/), `pages.py`, `translations.py`, `schemas/authorization.py`, `routers/authorization.py`, `services/authorization.py`, `services/clients.py` y `tests/test_authorization.py`.

## Código por SMS

Estándar: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt).

- El número viaja y se guarda con `+`, el código de país y solo dígitos.
- El servidor valida el número con `phonenumbers`.
- Si un cliente es una app de Android, su hash va en la penúltima línea del SMS.
- El host de la línea del código es el de la web donde se escribe el código: el `Host` de la petición que pide el código, que tiene que ser una superficie de `domain`. Otro responde 400.
- El hash de cada app de Android es `sms_hashes` de `Settings`, por la pieza de su `User-Agent`: cambia con la llave que firma la app.
- La web donde se escribe el código sirve `/.well-known/apple-app-site-association` como archivo estático, desde `static/.well-known/apple-app-site-association`, y una app de iOS declara ese host entre sus dominios asociados. [Apple](https://developer.apple.com/documentation/security/enabling-autofill-for-domain-bound-sms-codes)
- Cada número recibe un SMS por minuto, hasta 5 por hora y hasta 10 por día, y cada IP pide hasta 10 por hora.
- El código para entrar sigue las reglas del de [Recuperación](#recuperación).
- Cada fallo del código para entrar cuenta entre los fallos consecutivos del teléfono, y un código nuevo no los reinicia ([NIST SP 800-63B-4 §3.1.3.2](../fuentes/nist/sp800-63b-4.txt)).

## Contraseñas

Estándares: de ASVS 5.0, los capítulos [V6 *Authentication*](../fuentes/owasp/ASVS_V6_Authentication.md) y [V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md).

- La contraseña la elige el titular.
- El login con contraseña identifica la cuenta con su correo o con su teléfono, uno solo.
- La lista de bloqueo es un archivo del servidor.
- Una contraseña se guarda con `PasswordHash.recommended()` de pwdlib: Argon2id con 64 MiB, 3 pasadas y 4 carriles.
- Al medir el largo de una contraseña, cada punto de código cuenta como un carácter.
- La contraseña se normaliza a NFC antes del hash y al verificarla: el mismo texto escrito en otro dispositivo puede llegar en otra forma Unicode.
- El cliente muestra una guía para elegir una contraseña fuerte, que avisa que un carácter fuera de ASCII puede escribirse distinto en otro dispositivo. Al rechazar una de la lista de bloqueo, dice por qué y repite la guía.
- El servidor obliga a cambiar una contraseña cuando hay evidencia de que se comprometió.
- Toda contraseña tiene al menos 8 caracteres ([ASVS 5.0 §6.2.1](../fuentes/owasp/ASVS_V6_Authentication.md)).
- El campo de la contraseña la oculta y ofrece mostrarla entera mientras se escribe ([ASVS 5.0 §6.2.6](../fuentes/owasp/ASVS_V6_Authentication.md)).
- Cambiar la contraseña cierra las demás sesiones, y restablecerla, todas: quien la cambia porque la cree robada no deja abierta la sesión del ladrón ([ASVS 5.0 §7.4.3](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- Una contraseña admite cualquier carácter, sin reglas de composición ([ASVS 5.0 §6.2.5](../fuentes/owasp/ASVS_V6_Authentication.md)).
- El servidor admite contraseñas de al menos 64 caracteres ([ASVS 5.0 §6.2.9](../fuentes/owasp/ASVS_V6_Authentication.md)).
- Crear o cambiar una contraseña la compara contra la lista de bloqueo, que tiene al menos las 3000 contraseñas más comunes de 8 caracteres o más, contraseñas filtradas y las palabras propias del producto, como su nombre ([ASVS 5.0 §6.1.2](../fuentes/owasp/ASVS_V6_Authentication.md), [§6.2.4](../fuentes/owasp/ASVS_V6_Authentication.md), [§6.2.11](../fuentes/owasp/ASVS_V6_Authentication.md) y [§6.2.12](../fuentes/owasp/ASVS_V6_Authentication.md)).
- El servidor verifica la contraseña tal como llega, salvo la normalización a NFC, sin truncarla ni cambiar sus mayúsculas ([ASVS 5.0 §6.2.8](../fuentes/owasp/ASVS_V6_Authentication.md)).
- El campo de la contraseña admite pegar, el autocompletado del navegador y los gestores de contraseñas ([ASVS 5.0 §6.2.7](../fuentes/owasp/ASVS_V6_Authentication.md)).
- No hay cambio periódico de la contraseña, ni pistas, ni preguntas de seguridad ([ASVS 5.0 §6.2.10](../fuentes/owasp/ASVS_V6_Authentication.md) y [§6.4.2](../fuentes/owasp/ASVS_V6_Authentication.md)).

## Cuentas

Estándares: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt) y el capítulo [V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md) de ASVS 5.0.

- El correo y el teléfono identifican la cuenta: cada uno pertenece a una sola, y el registro responde 409 si la cuenta ya existe.
- El servidor pasa el correo a minúsculas al recibirlo, y así lo guarda, lo compara y le envía.
- Una cuenta no tiene nombre de usuario.
- Una IP que recibe 10 respuestas 409 del registro en 15 minutos queda bloqueada 30 minutos.
- El registro pide el código en `POST /api/auth/register/code`, que ya responde 409 si la cuenta existe, y las opciones de la passkey en `POST /api/auth/register/options`, con un user handle nuevo.
- El registro lleva el código y el primer autenticador, una passkey o una contraseña, en la misma petición, y abre la sesión por `POST /api/auth/register/cookie` o `/token`, como un login. Una cuenta con teléfono puede registrarse sin autenticador: entra con el código por SMS.
- El registro verifica la passkey antes que el código: una ceremonia que falla no gasta un intento del código.
- El correo se cambia pidiendo el código para el nuevo en `POST /api/account/email/code` y presentándolo en `PUT /api/account/email`, y el teléfono, en `POST /api/account/phone/code` y `PUT /api/account/phone`. Un correo o un teléfono que tiene otra cuenta responde 409.
- Volver a autenticarse es un paso aparte, con la sesión abierta: `POST /api/auth/reauth/options` lista en `allowCredentials` las passkeys de la cuenta, y `POST /api/auth/reauth/passkey` y `/reauth/password` verifican una credencial de la cuenta de la sesión. Renuevan la misma fila, escriben su `authenticated_at` y responden como se presenta la sesión: los tokens nuevos de una app, o la cookie nueva de la web.
- Una operación que pide volver a autenticarse lo acepta durante 5 minutos desde `authenticated_at`; después responde 403 de tipo `reauthentication-required`.
- La cuenta de administración tiene `role` `admin`.
- El registro con el código de instalación no acepta contraseña. Un código de instalación equivocado, o uno que llega cuando ya hay una cuenta de administración, responde 403, y dos registros con el código se esperan con un candado de PostgreSQL: solo uno queda como la primera.
- Una cuenta de administración que entra con contraseña recibe 401, sin que se verifique ni se cuente un fallo: no revela que es de administración. Con una passkey sin el flag UV recibe 403 de tipo `user-verification-required`, sin contar un fallo: la firma vale, y quien la presenta tiene la passkey. Lo mismo al volver a autenticarse.
- El aviso dice a quién escribir con `contact` de `Settings`, y va en el idioma de la cuenta.
- Registrarse no avisa: la passkey se vincula a una cuenta que acaba de nacer.
- El correo y el teléfono se cambian desde una sesión abierta, con un código enviado al nuevo, y el viejo recibe un aviso.
- El titular ve en la app cada intento fallido y cada autenticador deshabilitado.
- Un autenticador deshabilitado cierra solo el login con él: las sesiones abiertas siguen.
- Un login con un autenticador deshabilitado responde 403, de tipo `authenticator-disabled`, sin verificar la credencial.
- Los fallos consecutivos y la hora del siguiente intento viven en la base.
- El servidor acepta en toda cuenta los métodos para entrar, y cada repositorio elige cuáles ofrece cada pieza, de los disponibles en su plataforma.
- La pantalla para entrar ofrece primero la passkey, si el dispositivo la tiene, y luego el código por SMS y la contraseña, entre los que elige el usuario.
- La app guarda en el dispositivo el último método con que entró, y lo ofrece primero la próxima vez.
- Mientras no hay una cuenta de administración, el registro acepta el código de instalación, `setup_code` de `Settings`, y la cuenta que se registra con él es de administración. Con la primera, el registro deja de aceptarlo.
- Una cuenta de administración entra solo con una passkey que verificó al usuario, con el flag UV en los datos del autenticador, y la que se registra con el código de instalación vincula una al registrarse ([NIST SP 800-63B-4 §2.2.1](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta entra con una contraseña, una passkey o un código por SMS ([NIST SP 800-63B-4 §2.1.1](../fuentes/nist/sp800-63b-4.txt)).
- Las direcciones de aviso son el correo, el teléfono y el push a las apps con sesión abierta ([NIST SP 800-63B-4 §4.6](../fuentes/nist/sp800-63b-4.txt)).
- Desde el quinto fallo consecutivo, el siguiente intento espera 30 segundos, que se duplican con cada fallo hasta una hora, y un intento antes de tiempo responde 429 ([NIST SP 800-63B-4 §3.2.2](../fuentes/nist/sp800-63b-4.txt)).
- Cada autenticador guarda cuándo se vinculó y cuándo cambió, y cada uno de esos eventos va al registro de eventos con su IP y su user agent ([NIST SP 800-63B-4 §4.1](../fuentes/nist/sp800-63b-4.txt)).
- Un inicio de sesión exitoso pone en cero los fallos de los autenticadores que usó ([NIST SP 800-63B-4 §3.2.2](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta se registra con un correo o con un teléfono, verificado con un código como el de [Recuperación](#recuperación) ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta puede tener un correo, un teléfono, varias passkeys y una contraseña ([NIST SP 800-63B-4 §4.1.2.1](../fuentes/nist/sp800-63b-4.txt) y [§4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Agregar o borrar una passkey, agregar o cambiar la contraseña y cambiar el correo o el teléfono piden volver a autenticarse en ese momento ([ASVS 5.0 §7.5.1](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- Vincular, cambiar o borrar un autenticador, y recuperar la cuenta, avisa a todas las direcciones de aviso. El aviso dice qué hacer, y a quién escribir, si el titular no lo hizo ([NIST SP 800-63B-4 §4.1.2.1](../fuentes/nist/sp800-63b-4.txt), [§4.2.3](../fuentes/nist/sp800-63b-4.txt), [§4.5](../fuentes/nist/sp800-63b-4.txt) y [§4.6](../fuentes/nist/sp800-63b-4.txt)).
- Un autenticador se deshabilita a los 100 fallos consecutivos. Si los fallos involucran dos autenticadores, se deshabilitan los dos ([NIST SP 800-63B-4 §3.2.2](../fuentes/nist/sp800-63b-4.txt)).
- El titular vuelve a habilitarlo desde una sesión abierta o, si es la contraseña, restableciéndola ([NIST SP 800-63B-4 §3.2.2](../fuentes/nist/sp800-63b-4.txt)).
- El titular invalida en el acto un autenticador perdido o robado, borrando la passkey o cambiando el teléfono, y la app le explica cómo protegerlos ([NIST SP 800-63B-4 §3.2.1](../fuentes/nist/sp800-63b-4.txt) y [§4.3](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta que se borra o se deshabilita pierde en el momento sus autenticadores ([NIST SP 800-63B-4 §4.5](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta que se borra o se deshabilita pierde en el momento sus sesiones ([ASVS 5.0 §7.4.2](../fuentes/owasp/ASVS_V7_Session_Management.md)).

| Pieza | Passkey | Contraseña | Código por SMS |
| :--- | :--- | :--- | :--- |
| La web | Sí | Sí | Sí, con WebOTP |
| Una app de Flutter o de Flet, en la web | Sí, en la misma pestaña | Sí | Sí, con WebOTP |
| Una app de Android | Sí | Sí | Sí, se completa solo |
| Una app de Flutter o de Flet, en el teléfono | Sí | Sí | Sí, se completa solo |
| Una app de Flutter o de Flet, en Windows o en macOS | Sí | Sí | Sí |
| Una app de Flutter o de Flet en Linux, o de Qt | Sí, por el navegador del sistema | Sí | Sí |

Plantilla: de [plantilla/server/](../plantilla/server/), `models/account/throttled.py`, `schemas/account.py`, `routers/account.py`, `services/authenticators.py`, `services/registration.py`, `services/account.py`, `services/codes.py`, `services/limits.py`, `services/messages.py`, `services/notices.py`, `tests/test_registration.py` y `tests/test_account.py`.

## Passkeys

Estándares: [*Web Authentication Level 3*](../fuentes/w3c/webauthn-3.html) de W3C y [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt).

- El servidor verifica las passkeys con `verify_registration_response` y `verify_authentication_response` de `webauthn`, de Duo, con `supported_pub_key_algs` igual a `pubKeyCredParams`. La biblioteca no mira el largo del credential ID, `crossOrigin`, `topOrigin`, las extensiones, la atestación que se acepta, que BE sea el guardado ni el user handle, y compara el `signCount` antes que la firma: el servidor comprueba lo que ella no mira, y le pasa el `signCount` en 0 para compararlo él después de la firma, así una aserción falsa no denuncia una passkey clonada. [webauthn 3.0.1](https://raw.githubusercontent.com/duo-labs/py_webauthn/v3.0.1/webauthn/registration/verify_registration_response.py), [webauthn 3.0.1](https://raw.githubusercontent.com/duo-labs/py_webauthn/v3.0.1/webauthn/authentication/verify_authentication_response.py)
- El servidor no pide extensiones.
- El cliente le manda al servidor la respuesta de `create()` o de `get()` entera, con `clientExtensionResults` y `transports`.
- La landing sirve `https://<dominio>/.well-known/assetlinks.json` como archivo estático, desde `static/.well-known/assetlinks.json`.
- El dominio es `domain` de `Settings`: cada máquina tiene el suyo.
- La lista de origins es `https://<dominio>`, `https://app.<dominio>` y `https://panel.<dominio>`, y los `android:apk-key-hash:…` de `app_origins` de `Settings`, los de las llaves que firman las apps de ese despliegue.
- El login con passkey pide antes sus opciones en `POST /api/auth/passkey/options`, y el servidor busca el challenge por el que trae `clientDataJSON`.
- Las passkeys de la cuenta se ven en `GET /api/account/passkeys`, se vinculan por `PUT /api/account/passkeys/{id}` después de pedir las opciones en `POST /api/account/passkeys/options`, y se borran por `DELETE /api/account/passkeys/{id}`.
- El challenge de un registro guarda el user handle para el que se pidió: una cuenta nueva toma ese handle, y vincular una passkey exige el de la cuenta.
- Una app de iOS o de macOS declara `webcredentials:<dominio>` en `com.apple.developer.associated-domains`, y la landing sirve `https://<dominio>/.well-known/apple-app-site-association` con el app ID de cada app de iOS y de macOS en `webcredentials`, como archivo estático desde `static/.well-known/apple-app-site-association`.
- En Windows, la app escribe el `clientDataJSON` que firma la API del sistema, con el origin `https://<dominio>`, como un navegador en ese dominio.
- El RP ID es `<dominio>` ([WebAuthn §5.4.2](../fuentes/w3c/webauthn-3.html)).
- Toda passkey es descubrible, con `residentKey` `required` y `requireResidentKey` `true` ([WebAuthn §5.4.4](../fuentes/w3c/webauthn-3.html)).
- `userVerification` es `preferred` ([WebAuthn §5.4.4](../fuentes/w3c/webauthn-3.html) y [§5.5](../fuentes/w3c/webauthn-3.html)).
- `attestation` es `none` ([WebAuthn §5.4.7](../fuentes/w3c/webauthn-3.html)).
- El registro acepta la atestación `none` y la propia, `packed` sin `x5c`, que el navegador entrega aunque se pida `none`. Otra hace fallar el registro ([WebAuthn §5.4.7](../fuentes/w3c/webauthn-3.html) y [§7.1](../fuentes/w3c/webauthn-3.html)).
- Un `clientExtensionResults` que no está vacío hace fallar el registro o el login ([WebAuthn §7.1](../fuentes/w3c/webauthn-3.html), [§7.2](../fuentes/w3c/webauthn-3.html) y [§9.4](../fuentes/w3c/webauthn-3.html)).
- En el registro, el `authData` acepta solo la extensión `credProtect`, con un valor de 1 a 3: Chrome se la pide a la llave por su cuenta al crear una passkey descubrible, y la llave la devuelve. En el login no acepta ninguna. Otra extensión hace fallar la ceremonia y va al registro de eventos con su nombre ([WebAuthn §7.1](../fuentes/w3c/webauthn-3.html), [§7.2](../fuentes/w3c/webauthn-3.html) y [§9.5](../fuentes/w3c/webauthn-3.html)). [Chromium 157.0.8103.79](https://raw.githubusercontent.com/chromium/chromium/157.0.8103.79/content/browser/webauth/authenticator_common_impl.cc), [CTAP 2.1 §12.1](https://fidoalliance.org/specs/fido-v2.1-ps-20210615/fido-client-to-authenticator-protocol-v2.1-ps-errata-20220621.html)
- `rp.name` es el RP ID; `user.name`, el correo o el teléfono de la cuenta, y `user.displayName` va vacío ([WebAuthn §5.4.1](../fuentes/w3c/webauthn-3.html) y [§5.4.3](../fuentes/w3c/webauthn-3.html)).
- `pubKeyCredParams` lleva EdDSA (-8), ES256 (-7) y RS256 (-257), en ese orden ([WebAuthn §5.4](../fuentes/w3c/webauthn-3.html)).
- El user handle son 64 bytes aleatorios que guarda la cuenta, sin datos personales ([WebAuthn §5.4.3](../fuentes/w3c/webauthn-3.html) y [§14.6.1](../fuentes/w3c/webauthn-3.html)).
- El login deja `allowCredentials` vacío. Al volver a autenticarse, `allowCredentials` lista las passkeys de la cuenta, con sus `transports` ([WebAuthn §5.5](../fuentes/w3c/webauthn-3.html)).
- El challenge son 16 bytes aleatorios que genera el servidor, vive en Valkey 10 minutos y se borra al usarlo ([WebAuthn §13.4.3](../fuentes/w3c/webauthn-3.html)).
- Una ceremonia con `crossOrigin` verdadero o con `topOrigin` se rechaza ([WebAuthn §7.1](../fuentes/w3c/webauthn-3.html) y [§7.2](../fuentes/w3c/webauthn-3.html)).
- Si el `signCount` de la aserción o el guardado no es cero y el nuevo no es mayor, el login falla y el titular recibe un aviso: la passkey puede estar clonada ([WebAuthn §6.1.1](../fuentes/w3c/webauthn-3.html) y [§7.2](../fuentes/w3c/webauthn-3.html)).
- El servidor guarda el `signCount` y el `backupState` nuevos después de las demás comprobaciones del login, y `uvInitialized` queda como se registró ([WebAuthn §7.2](../fuentes/w3c/webauthn-3.html)).
- Un credential ID de más de 1023 bytes, o que ya es de otra passkey, hace fallar el registro ([WebAuthn §7.1](../fuentes/w3c/webauthn-3.html)).
- `excludeCredentials` lista las passkeys de la cuenta: dos passkeys de una cuenta no quedan en el mismo autenticador ([WebAuthn §5.4](../fuentes/w3c/webauthn-3.html) y [§13.4.6](../fuentes/w3c/webauthn-3.html)).
- El servidor compara `origin` exacto contra una lista fija: el de cada superficie web y el de cada app que usa la API de su sistema ([WebAuthn §13.4.8](../fuentes/w3c/webauthn-3.html) y [§13.4.9](../fuentes/w3c/webauthn-3.html)).
- Si el `backupState` de una passkey pasa de 1 a 0, la app le pide al titular revisar sus otros autenticadores y, si no tiene otro, agregar uno ([WebAuthn §6.1.3](../fuentes/w3c/webauthn-3.html)).
- Cada passkey guarda su credential ID, su clave pública, `signCount`, `uvInitialized`, `transports`, `backupEligible`, `backupState`, su nombre, su creación y su último uso ([WebAuthn §6.1.3](../fuentes/w3c/webauthn-3.html) y [§7.1](../fuentes/w3c/webauthn-3.html)).
- El titular ve sus passkeys, con su nombre y su último uso, y borra la que quiera: así revoca la de un dispositivo perdido ([NIST SP 800-63B-4 §3.2.1](../fuentes/nist/sp800-63b-4.txt)).

Plantilla: de [plantilla/server/](../plantilla/server/), `models/account/passkey.py`, `services/passkeys.py`, `services/attestation.py` y `tests/test_passkeys.py`; [plantilla/packages/passkey/](../plantilla/packages/passkey/), con el plugin `passkey` de Flutter y la extensión `flet_passkey` de Flet.

## Recuperación

Estándar: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt).

- La solicitud del código responde 404 si la cuenta no existe, y una IP que recibe 10 en 15 minutos queda bloqueada 30 minutos.
- Cada correo recibe un código por minuto, y hasta 5 por hora. Los SMS siguen los límites de [Código por SMS](#código-por-sms).
- Un código se invalida al tercer intento fallido.
- Con el código, una cuenta con contraseña la restablece, y una sin contraseña vincula una passkey o una contraseña.
- El código vive en Valkey, y uno nuevo reemplaza al anterior.
- El código vale una sola vez.
- Un código equivocado o vencido responde 400 de tipo `invalid-code`.
- Una cuenta con passkey que se recupera con el código del correo lo aplica 24 horas después, sin cerrar las sesiones, y el titular la cancela desde la app. El código del teléfono se aplica en el momento.
- Una cuenta de administración no se recupera con el código: la recupera otro administrador.
- A los 100 fallos consecutivos de la recuperación, la cuenta deja de recuperarse con el código, y la recupera un administrador. Un inicio de sesión exitoso la vuelve a habilitar.
- Un administrador recupera una cuenta que no es de administración cambiando su correo o su teléfono por uno que tiene el titular, que sigue con el código.
- El código vence a los 10 minutos, también el que va al correo ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Quien no puede entrar ni recibir el código recupera la cuenta con un administrador ([NIST SP 800-63B-4 §4.2.1](../fuentes/nist/sp800-63b-4.txt)).
- El código tiene 6 dígitos ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta se recupera con un código que recibe, a su elección, en el correo o en el teléfono que registró ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt) y [§4.2.2.1](../fuentes/nist/sp800-63b-4.txt)).
- Cada fallo cuenta entre los fallos consecutivos de la recuperación de la cuenta, tenga o no contraseña, con las esperas y el límite de [Cuentas](#cuentas) ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).

## Sesión

Estándares: de ASVS 5.0, los capítulos [V3 *Web Frontend Security*](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md) y [V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md); [RFC 6749](../fuentes/rfc/rfc6749.txt); [RFC 9700](../fuentes/rfc/rfc9700.txt), y [RFC 9110](../fuentes/rfc/rfc9110.txt).

- La web y una app que corre en el navegador presentan su sesión con una cookie, y una app instalada, con un token de acceso que renueva con un token de refresco. En el navegador, ningún token queda al alcance de un script.
- La web y las apps comparten la tabla de sesiones: cambia solo el token que presenta cada una.
- Una sesión no tiene vencimiento total: pedir entrar de nuevo cada mes aleja al usuario de una app de uso diario, y el refresco rotado descubre un token robado cuando el dueño vuelve a refrescar.
- La sesión vence tras 30 días sin uso.
- La cookie de la web dura 30 días de `Max-Age`, que se renuevan con el último uso.
- El último uso se actualiza al refrescar, en una app, y a lo sumo cada 15 minutos, en la web.
- Una tarea periódica borra las sesiones vencidas.
- En una app instalada, el token de acceso vive solo en memoria, y el de refresco, en el almacenamiento seguro del sistema.
- Una app instalada hace un solo refresco a la vez, y las peticiones que reciben un 401 mientras tanto lo esperan.
- Ante un 401, una app instalada refresca la sesión una sola vez y reintenta una sola vez.
- Una app que entra con contraseña, con código por SMS o con la passkey de su sistema recibe la misma respuesta que el canje del código.
- La fila de una sesión de una app guarda el SHA-256 del secreto vigente y el del anterior. El anterior vale mientras el vigente no se usó: una respuesta perdida cerraría la sesión del dueño y le avisaría de un robo.
- Presentar el anterior reemplaza el vigente, y el anterior no cambia. Si el vigente pasara a ser el anterior, un dueño y un ladrón que refrescan por turnos nunca presentarían un reúso.
- Un token de refresco con la firma inválida o de una sesión que no existe responde `invalid_grant`, sin aviso.
- Un 401 a la cookie de la web no lleva `WWW-Authenticate`: la cookie no es un esquema de autenticación de HTTP.
- La fila de la sesión guarda el SHA-256 del token de la web.
- El token de refresco es el id de su sesión y un secreto aleatorio de 256 bits, firmados con HMAC.
- Iniciar sesión o volver a autenticarse crea o renueva la fila de sesión, con su creación y su último uso.
- La API, bajo `/api`, y las apps que corren en el navegador se sirven en el mismo origen que la web, sin `Access-Control-Allow-Origin`.
- Cada método para entrar tiene dos rutas: `/api/auth/<método>/cookie`, que deja la cookie de la web, y `/api/auth/<método>/token`, que responde los tokens de una app. El endpoint de token es `POST /api/auth/token`, y cerrar sesión, `POST /api/auth/logout`, con la cookie o con el token de acceso.
- La clave del HMAC del token de refresco son 256 bits aleatorios, `refresh_key` de `Settings`.
- El `Origin` del servidor es `https://` seguido del `Host` de la petición: vale igual en cada superficie.
- Cerrar sesión borra la fila ([RFC 9700 §4.14.2](../fuentes/rfc/rfc9700.txt)).
- El token de la web es un valor aleatorio de 256 bits ([ASVS 5.0 §7.2.3](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- La cookie de la web es `__Host-session`, `Secure`, `HttpOnly` y `SameSite=Strict`, con `Path=/`: ningún script la lee, ninguna petición de otro sitio la lleva y ningún subdominio la reemplaza ([ASVS 5.0 §3.3.1](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md), [§3.3.2](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md), [§3.3.3](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md) y [§3.3.4](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md)).
- Una petición con la cookie y un método que no es seguro responde 403 si su `Origin` falta o no es el del servidor ([ASVS 5.0 §3.5.1](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md)).
- El secreto del token de refresco rota en cada uso ([RFC 9700 §2.2.2](../fuentes/rfc/rfc9700.txt) y [§4.14.2](../fuentes/rfc/rfc9700.txt)).
- Cualquier otro secreto de la sesión es un reúso: borra la sesión, y el titular lo ve en la app. Un token robado se descubre cuando el dueño vuelve a refrescar ([RFC 9700 §4.14.2](../fuentes/rfc/rfc9700.txt)).
- Iniciar sesión o volver a autenticarse emite tokens nuevos y deja sin efecto los que el cliente traía ([ASVS 5.0 §7.2.4](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- El titular ve sus sesiones abiertas y, después de volver a autenticarse, cierra la que quiera o todas ([ASVS 5.0 §7.5.2](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- El refresco va al endpoint de token con `grant_type=refresh_token` y el `refresh_token`, y responde como el canje del código, con el `refresh_token` nuevo ([RFC 6749 §5.1](../fuentes/rfc/rfc6749.txt) y [§6](../fuentes/rfc/rfc6749.txt)).
- Una operación que cambia algo no usa `GET`, `HEAD` ni `OPTIONS` ([ASVS 5.0 §3.5.3](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md)).
- Un 401 a un token en `Authorization` lleva `WWW-Authenticate: Bearer` ([RFC 9110 §11.6.1](../fuentes/rfc/rfc9110.txt) y [§15.5.2](../fuentes/rfc/rfc9110.txt)).
- Ningún token viaja en la URL ([RFC 9700 §4.3.2](../fuentes/rfc/rfc9700.txt)).
- Ni los logs ni `event_log` guardan un token ([RFC 9700 §4.9.3](../fuentes/rfc/rfc9700.txt)).

Plantilla: de [plantilla/server/](../plantilla/server/), `models/account/`, la migración `<revisión>_accounts.py`, `schemas/auth.py`, `services/sessions.py`, `services/passwords.py`, `routers/auth.py`, `client`, `check_origin` y `signed_in` de `dependencies.py`, y `tests/test_sessions.py`.

## Token de acceso

Estándar: el capítulo [V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md) de ASVS 5.0.

- El token de acceso de una app es opaco y vence en 15 minutos. La fila de su sesión guarda su SHA-256 y su vencimiento.
- Refrescar la sesión reemplaza el token de acceso: el anterior deja de valer.
- El token de acceso no vale como cookie de la web, ni el token de la web como token de acceso.
- El token de acceso es un valor aleatorio de 256 bits ([ASVS 5.0 §7.2.3](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- Cerrar o borrar una sesión deja sin efecto en el momento su token de acceso: el servidor busca la sesión en cada petición ([ASVS 5.0 §7.4.1](../fuentes/owasp/ASVS_V7_Session_Management.md)).

## WebSocket

Estándar: el [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

- La web se autentica con la cookie de sesión del handshake, y una app, con `Authorization: Bearer` en el handshake, como en REST.
- Un handshake con la cookie exige un `Origin` igual al de la web, y uno con `Authorization` no lo revisa.
- Una sesión que no vale o un token vencido cierran la conexión con 4401, del rango de códigos de cierre privados. En el handshake, el servidor acepta la conexión para cerrarla: el navegador no le muestra a la web el código de un rechazo, que ve como un cierre 1006, igual que una caída de la red. [RFC 6455 §7.4.2](https://www.rfc-editor.org/rfc/rfc6455.txt), [WHATWG WebSockets](https://raw.githubusercontent.com/whatwg/websockets/7f25d7dc8c2598ebca795ce4af68909d913a3888/index.bs)
- Ante un 4401, una app refresca la sesión una sola vez y reconecta, y la web vuelve al inicio de sesión.
- El servidor no revalida cada cierto tiempo la sesión de una conexión abierta: el cierre llega con el borrado de la sesión, no en la siguiente revisión.
- Al refrescar la sesión, una app manda el token nuevo por la misma conexión ([WebSocket Security, *Session Management*](../fuentes/owasp/WebSocket_Security.md)).
- Cerrar o borrar una sesión cierra en el momento sus conexiones, y una sesión que vence también las cierra ([WebSocket Security, *Session Management*](../fuentes/owasp/WebSocket_Security.md)).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| La cookie de la web es `__Host-session`, `Secure`, `HttpOnly` y `SameSite=Strict`, con `Path=/` y 30 días de `Max-Age` | `test_cookie_is_host_secure_httponly_strict` |
| El token de la web es un valor aleatorio de 256 bits, y la fila guarda su SHA-256 | `test_web_token_is_random_and_hashed` |
| Un 401 a la cookie de la web no lleva `WWW-Authenticate` | `test_cookie_without_session_is_401_without_challenge` |
| La web actualiza el último uso, y renueva el `Max-Age` de la cookie, a lo sumo cada 15 minutos | `test_web_writes_last_use_every_15_minutes` |
| La sesión vence tras 30 días sin uso | `test_session_expires_after_30_days_without_use` |
| La tarea periódica borra las sesiones vencidas | `test_purge_deletes_sessions_unused_for_30_days` y `test_purge_task_deletes_expired_sessions` |
| Una petición con la cookie y un método que no es seguro responde 403 si su `Origin` falta o no es `https://` y el `Host` | `test_unsafe_request_with_cookie_needs_the_origin` |
| Una app que entra con contraseña recibe la respuesta del canje del código, con `Cache-Control: no-store` y `Pragma: no-cache` | `test_app_signs_in_as_the_token_endpoint` |
| El token de refresco es el id de su sesión y un secreto aleatorio de 256 bits, firmados con HMAC con `refresh_key` | `test_refresh_token_is_the_session_and_a_secret` |
| El token de acceso es un valor aleatorio de 256 bits que vence en 15 minutos, la fila guarda su SHA-256, y un 401 a un token en `Authorization` lleva `WWW-Authenticate: Bearer` | `test_access_token_lasts_15_minutes` |
| El token de acceso no vale como cookie, ni el token de la web como token de acceso | `test_tokens_are_not_interchangeable` |
| El refresco rota el secreto, reemplaza el token de acceso, actualiza el último uso y responde como el canje | `test_refresh_rotates_the_secret` |
| El secreto anterior vale mientras el vigente no se usó, reemplaza el vigente y no cambia | `test_previous_secret_replaces_the_current_one` |
| Un secreto que no es el vigente ni el anterior borra la sesión | `test_reused_secret_deletes_the_session` |
| Un token de refresco con la firma inválida o de una sesión que no existe responde `invalid_grant`, sin borrar nada | `test_forged_refresh_token_is_invalid_grant_without_notice` |
| El endpoint de token toma un parámetro sin valor como ausente, ignora el que no conoce, responde `invalid_request` a uno repetido o a uno obligatorio que falta y `invalid_scope` a `scope`, y cada error es un 400 en JSON con `error` | `test_token_endpoint_parameters` |
| El endpoint de token acepta solo `POST` en `application/x-www-form-urlencoded` | `test_token_endpoint_takes_only_a_form_post` |
| Cerrar sesión borra la fila y deja sin efecto el token de acceso | `test_logout_deletes_the_session` |
| Iniciar sesión deja sin efecto la cookie o el token de acceso que el cliente traía | `test_sign_in_discards_the_tokens_it_brings` |
| El login con contraseña identifica la cuenta con su correo o con su teléfono, uno solo | `test_login_takes_the_email_or_the_phone` |
| El login compara el correo en minúsculas | `test_login_lowers_the_email` |
| La contraseña se verifica en NFC, sin truncarla ni cambiar sus mayúsculas | `test_password_is_checked_in_nfc_as_it_comes` |
| Los fallos consecutivos viven en la base: una contraseña equivocada responde 401 y cuenta uno | `test_wrong_password_is_a_401_and_a_failure` |
| Desde el quinto fallo consecutivo, el siguiente intento espera 30 segundos, que se duplican con cada fallo hasta una hora, y un intento antes de tiempo responde 429 con `Retry-After` | `test_wait_doubles_from_the_fifth_failure_up_to_an_hour` y `test_attempt_before_the_wait_is_a_429` |
| Un inicio de sesión exitoso pone en cero los fallos de la contraseña | `test_success_resets_the_failures` |
| La contraseña se deshabilita a los 100 fallos consecutivos, un login con ella responde 403 de tipo `authenticator-disabled` sin verificarla, y las sesiones abiertas siguen | `test_hundredth_failure_disables_the_password` |
| Una passkey abre la sesión por sus dos rutas, la de la cookie y la de los tokens | `test_passkey_signs_in_the_web_and_the_app` |
| Las opciones del login llevan un challenge de 16 bytes que vive 10 minutos en Valkey, el RP ID igual a `domain`, `userVerification` `preferred`, `allowCredentials` vacío y ninguna extensión | `test_options_ask_a_challenge_of_16_bytes_for_10_minutes` |
| El challenge se borra al usarlo, y uno que el servidor no generó no vale | `test_challenge_is_used_once` |
| El servidor compara `origin` exacto con las superficies de `domain` y `app_origins` | `test_origin_is_a_web_surface_or_an_app` |
| El RP ID es `domain` | `test_rp_id_is_the_domain` |
| Una ceremonia con `crossOrigin` verdadero o con `topOrigin` se rechaza | `test_cross_origin_and_top_origin_are_refused` |
| Un `clientExtensionResults` que no está vacío hace fallar el login | `test_client_extension_results_must_be_empty` |
| En el login, el `authData` no acepta ninguna extensión, y la que llega va al registro de eventos con su nombre | `test_authenticator_extension_fails_and_is_named` |
| El servidor comprueba que BE sea el guardado | `test_backup_eligibility_must_be_the_stored_one` |
| El servidor comprueba que el user handle sea el de la cuenta de la passkey | `test_user_handle_must_be_the_account` |
| Una aserción que falla cuenta un fallo de su passkey, que queda | `test_bad_signature_is_a_failure_that_stays` |
| Si el `signCount` de la aserción o el guardado no es cero y el nuevo no es mayor, el login falla | `test_sign_count_that_does_not_grow_fails` |
| El login guarda el `signCount`, el `backupState` y el último uso después de las demás comprobaciones, y `uvInitialized` queda como se registró | `test_login_stores_sign_count_and_backup_state_after_the_checks` |
| Una passkey antes de su espera responde 429, y deshabilitada, 403 de tipo `authenticator-disabled`, y un login exitoso pone en cero sus fallos | `test_passkey_waits_and_disables_like_any_authenticator` |
| El servidor sirve la página de autorización solo a un cliente y una URI de retorno registrados, y si no, o si vienen repetidos, muestra el error sin redirigir | `test_unregistered_client_or_return_shows_the_error` y `test_repeated_client_or_return_shows_the_error` |
| Una URI de loopback acepta cualquier puerto, y solo en `127.0.0.1` | `test_loopback_return_takes_any_port` y `test_unregistered_client_or_return_shows_the_error` |
| `response_type` distinto de `code` responde `unsupported_response_type`, `scope` responde `invalid_scope`, y sin `code_challenge` `S256` responde `invalid_request`, de vuelta a la URI de retorno con el `state` | `test_authorization_errors_go_back_with_the_state` |
| El endpoint de autorización toma un parámetro sin valor como ausente, ignora el que no conoce y responde `invalid_request` a uno repetido | `test_authorization_parameters` |
| La página de autorización no carga recursos ni enlaces de otros sitios | `test_page_loads_nothing_from_other_sites` |
| La página toma su texto del catálogo del idioma pedido, o del español | `test_page_speaks_the_language_asked_or_the_base` |
| El endpoint de autorización pide la passkey aunque el navegador tenga una sesión de la web | `test_page_asks_the_passkey_with_a_web_session` |
| El código son 256 bits aleatorios que viven 10 minutos, vuelve con el `state`, y el canje responde los tokens con `Cache-Control: no-store` y `Pragma: no-cache` | `test_code_goes_back_with_the_state_and_gives_the_tokens` |
| El código queda ligado al `client_id`, a la URI de retorno y al `code_challenge`, y si no coinciden el canje responde `invalid_grant` | `test_code_is_bound_to_client_return_and_verifier` |
| El canje sin un parámetro obligatorio, también `redirect_uri` si la petición lo llevó, responde `invalid_request` | `test_exchange_without_a_parameter_is_invalid_request` |
| Un código presentado dos veces responde `invalid_grant` y borra la sesión que creó | `test_code_presented_twice_deletes_its_session` |
| El flujo de la web guarda el `state` y un `code_verifier` de 32 bytes en Valkey, bajo un id en una cookie `__Host-` `Secure`, `HttpOnly` y `SameSite=Strict`, y pide `S256` | `test_web_flow_keeps_state_and_verifier_behind_a_cookie` |
| El retorno de la web toma el flujo una sola vez, borra su cookie, deja la cookie de sesión y vuelve a la app con un 303 | `test_web_flow_returns_with_the_cookie_of_the_session` |
| El retorno de la web rechaza un `state` que no es el de su flujo | `test_web_return_with_another_state_fails` |
| El código para registrarse son 6 dígitos que viven 10 minutos en Valkey, por un correo con texto y HTML, y el correo pasa a minúsculas | `test_email_code_is_6_digits_for_10_minutes` |
| El SMS del código lleva el hash de la app de Android en la penúltima línea, y en la última el `Host` de la petición, que tiene que ser una superficie de `domain` | `test_sms_code_binds_the_host_and_the_android_hash` |
| El servidor valida el número con `phonenumbers` | `test_phone_is_validated_with_phonenumbers` |
| Un código se invalida al tercer intento fallido | `test_code_fails_on_the_third_attempt` |
| El código vale una sola vez, y uno nuevo reemplaza al anterior | `test_code_is_used_once_and_a_new_one_replaces_it` |
| Cada correo recibe un código por minuto y hasta 5 por hora, también el correo nuevo de una cuenta | `test_email_gets_one_code_a_minute_and_five_an_hour` y `test_email_change_codes_follow_the_limits` |
| Cada número recibe un SMS por minuto, hasta 5 por hora y hasta 10 por día, y cada IP pide hasta 10 por hora | `test_number_gets_one_sms_a_minute_five_an_hour_and_ten_a_day` y `test_ip_asks_ten_sms_an_hour` |
| El registro responde 409 si la cuenta existe, al pedir el código y al registrarse | `test_existing_account_is_a_409` |
| Una IP que recibe 10 respuestas 409 del registro en 15 minutos queda bloqueada 30 minutos | `test_ten_conflicts_block_the_ip_for_30_minutes` |
| Las opciones del registro llevan un challenge de 16 bytes que vive 10 minutos en Valkey, `rp` con el RP ID como nombre, `user.name` el correo, `user.displayName` vacío, un user handle de 64 bytes, EdDSA, ES256 y RS256 en ese orden, una passkey descubrible, `userVerification` `preferred`, `attestation` `none` y ninguna extensión | `test_creation_options_ask_a_discoverable_passkey` |
| El registro lleva el código y la passkey, abre la sesión por sus dos rutas y guarda la passkey con sus campos y su vínculo | `test_registration_links_the_passkey_and_opens_the_session` |
| El registro acepta la atestación `none` y la propia, `packed` sin `x5c`, y rechaza otra aunque la biblioteca la acepte | `test_registration_takes_none_and_self_attestation` |
| En el registro, el `authData` acepta solo `credProtect`, de 1 a 3, y otra extensión va al registro de eventos con su nombre | `test_registration_takes_only_cred_protect` |
| En el registro, un `clientExtensionResults` que no está vacío, `crossOrigin` verdadero u otro `origin` hacen fallar la ceremonia | `test_registration_client_must_be_clean` |
| Un credential ID de más de 1023 bytes, o que ya es de otra passkey, hace fallar el registro | `test_credential_id_longer_than_1023_bytes_or_taken_fails` |
| Un código equivocado responde 400 de tipo `invalid-code`, y una passkey que falla no gasta un intento del código | `test_wrong_code_fails_and_a_failed_passkey_keeps_the_code` |
| El código de instalación registra la cuenta de administración mientras no hay otra, y uno equivocado responde 403 | `test_setup_code_registers_the_first_admin_once` |
| La cuenta de administración que se registra con el código de instalación vincula una passkey con el flag UV | `test_admin_registers_a_passkey_that_verified_the_user` |
| Una cuenta de administración que entra con contraseña recibe 401, sin que se verifique ni se cuente un fallo | `test_admin_does_not_sign_in_with_a_password` |
| Una cuenta de administración que entra con una passkey sin el flag UV recibe 403 de tipo `user-verification-required`, sin contar un fallo | `test_admin_passkey_needs_the_uv_flag` |
| Si el `signCount` no crece, el titular recibe un aviso | `test_sign_count_that_does_not_grow_notifies_the_holder` |
| Al volver a autenticarse, `allowCredentials` lista las passkeys de la cuenta con sus `transports` | `test_reauth_options_list_the_passkeys_with_transports` |
| Volver a autenticarse renueva la misma fila con tokens nuevos y su `authenticated_at`, y los que el cliente traía dejan de valer | `test_reauth_renews_the_app_session_and_its_tokens` y `test_reauth_renews_the_web_session_in_its_cookie` |
| Una passkey de otra cuenta no vuelve a autenticar la sesión | `test_reauth_with_the_passkey_of_another_account_is_refused` |
| Agregar o borrar una passkey y cambiar el correo o el teléfono piden haber vuelto a autenticarse en los últimos 5 minutos, o responden 403 de tipo `reauthentication-required` | `test_changes_need_a_reauth_within_5_minutes` |
| Vincular una passkey es un `PUT` que responde 201 y, repetido, 200; `excludeCredentials` lista las passkeys de la cuenta; la passkey guarda cuándo se vinculó, su evento lleva la IP, y el correo y el teléfono reciben un aviso con qué hacer y a quién escribir | `test_link_is_idempotent_and_notifies_every_address` |
| Vincular una passkey con las opciones de otra cuenta falla | `test_link_refuses_the_options_of_another_account` |
| El titular ve sus passkeys, en páginas, con su nombre y su último uso, y borra la que quiera, con aviso; la de otra cuenta responde 404 | `test_passkeys_are_listed_and_deleted` |
| El correo se cambia con un código enviado al nuevo, y el viejo recibe un aviso | `test_email_changes_with_a_code_to_the_new_one` |
| El teléfono se cambia con un SMS al nuevo, y el viejo recibe un aviso | `test_phone_changes_with_an_sms_to_the_new_one` |
| Un correo o un teléfono que tiene otra cuenta responde 409 | `test_email_or_phone_of_another_account_is_a_409` |
| Una cuenta se registra con un teléfono, verificado con el código de su SMS | `test_registration_by_phone_verifies_the_phone` |
