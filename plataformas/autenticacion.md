# Autenticación

Cómo se registra una cuenta, cómo entra y cómo mantiene su sesión: lo que hace el servidor y lo que cumplen con él sus clientes. Lo propio de cada cliente va en su página.

## Código de autorización

Estándares: [RFC 6749](../fuentes/rfc/rfc6749.txt), [RFC 7636](../fuentes/rfc/rfc7636.txt), [RFC 8252](../fuentes/rfc/rfc8252.txt) y [RFC 9700](../fuentes/rfc/rfc9700.txt).

- Una app que ofrece la passkey la usa con la API de su sistema operativo cuando su framework la ofrece de forma oficial. Si no, la usa en el navegador del sistema, que le devuelve un código de autorización.
- Una app que corre en el navegador hace el flujo por el servidor, en su misma pestaña: abre un endpoint del servidor que crea el `state` y el `code_verifier` y redirige a la petición de autorización, y la URI de retorno es otro endpoint del servidor, que canjea el código, deja la cookie de sesión de la web y vuelve a la app con un 303.
- En ese flujo, el endpoint que lo inicia guarda el `state` y el `code_verifier` en Valkey, bajo un id que deja en una cookie `__Host-` `Secure`, `HttpOnly` y `SameSite=Strict`, y el endpoint de retorno los toma una sola vez y borra la cookie.
- El código vive en Valkey, con la cuenta.
- Una app de escritorio recibe el retorno solo en `http://127.0.0.1:{puerto}/<ruta>`, y no en `[::1]`: toda máquina de escritorio tiene loopback IPv4.
- El endpoint de autorización autentica al usuario en cada petición, aunque el navegador tenga abierta una sesión de la web ([RFC 8252 §8.6](../fuentes/rfc/rfc8252.txt)).
- La petición de autorización lleva `code_challenge` con `code_challenge_method` `S256`. Sin él, o con `plain`, responde `invalid_request` ([RFC 7636 §4.2](../fuentes/rfc/rfc7636.txt) y [§4.4.1](../fuentes/rfc/rfc7636.txt)).
- El código son 256 bits aleatorios, vence a los 10 minutos, queda ligado al `client_id` y a la URI de retorno, y vale una sola vez. Al canjearlo queda marcado como usado, con el id de la sesión que creó, y presentarlo de nuevo responde `invalid_grant` y borra esa sesión ([RFC 6749 §4.1.2](../fuentes/rfc/rfc6749.txt) y [§10.10](../fuentes/rfc/rfc6749.txt)).
- Los endpoints no usan `scope`: una petición que lo trae responde `invalid_scope`, y el token da el acceso entero de la cuenta ([RFC 6749 §3.3](../fuentes/rfc/rfc6749.txt), [§4.1.2.1](../fuentes/rfc/rfc6749.txt) y [§5.2](../fuentes/rfc/rfc6749.txt)).
- El endpoint de autorización acepta `GET`, y el de token, solo `POST` en `application/x-www-form-urlencoded` ([RFC 6749 §3.1](../fuentes/rfc/rfc6749.txt), [§3.2](../fuentes/rfc/rfc6749.txt) y [§4.1.3](../fuentes/rfc/rfc6749.txt)).
- `response_type` es `code`, y otro valor responde `unsupported_response_type` ([RFC 6749 §3.1.1](../fuentes/rfc/rfc6749.txt) y [§4.1.2.1](../fuentes/rfc/rfc6749.txt)).
- El canje responde un 200 en JSON con `access_token`, `token_type` `Bearer`, `expires_in` con lo que dura el token de acceso y `refresh_token`, y con `Cache-Control: no-store` y `Pragma: no-cache` ([RFC 6749 §5.1](../fuentes/rfc/rfc6749.txt)).
- Una app del teléfono recibe el retorno en una URI `https` que reclama, donde su sistema y su biblioteca lo permiten, y si no, en un esquema propio con su dominio al revés, como `com.example.app:/oauth2redirect` ([RFC 8252 §7.1](../fuentes/rfc/rfc8252.txt) y [§7.2](../fuentes/rfc/rfc8252.txt)).
- Una app de escritorio abre el puerto en la interfaz de loopback al empezar la petición y lo cierra al recibir la respuesta ([RFC 8252 §8.3](../fuentes/rfc/rfc8252.txt)).
- La app abre la petición de autorización en el navegador del sistema, en una pestaña dentro de la app donde el sistema la ofrece, y nunca en un web-view ([RFC 8252 §5](../fuentes/rfc/rfc8252.txt), [§6](../fuentes/rfc/rfc8252.txt) y [§8.12](../fuentes/rfc/rfc8252.txt)).
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

## Código por SMS

Estándar: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt).

- El número viaja y se guarda con `+`, el código de país y solo dígitos.
- El servidor valida el número con `phonenumbers`.
- Si un cliente es una app de Android, su hash va en la penúltima línea del SMS.
- El host de la línea del código es el de la web donde se escribe el código.
- La web donde se escribe el código sirve `/.well-known/apple-app-site-association` como archivo estático, desde `static/.well-known/apple-app-site-association`, y una app de iOS declara ese host entre sus dominios asociados. [Apple](https://developer.apple.com/documentation/security/enabling-autofill-for-domain-bound-sms-codes)
- Cada número recibe un SMS por minuto, hasta 5 por hora y hasta 10 por día, y cada IP pide hasta 10 por hora.
- El código para entrar sigue las reglas del de [Recuperación](#recuperación).
- Cada fallo del código para entrar cuenta entre los fallos consecutivos del teléfono, y un código nuevo no los reinicia ([NIST SP 800-63B-4 §3.1.3.2](../fuentes/nist/sp800-63b-4.txt)).

## Contraseñas

Estándares: de ASVS 5.0, los capítulos [V6 *Authentication*](../fuentes/owasp/ASVS_V6_Authentication.md) y [V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md).

- La contraseña la elige el titular.
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
- El correo y el teléfono se cambian desde una sesión abierta, con un código enviado al nuevo, y el viejo recibe un aviso.
- El titular ve en la app cada intento fallido y cada autenticador deshabilitado.
- Un autenticador deshabilitado cierra solo el login con él: las sesiones abiertas siguen.
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
| Una app de Flutter, de Flet o de Qt, en escritorio | Sí, por el navegador del sistema | Sí | Sí |

## Passkeys

Estándares: [*Web Authentication Level 3*](../fuentes/w3c/webauthn-3.html) de W3C y [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt).

- El servidor verifica las passkeys con `verify_registration_response` y `verify_authentication_response` de `webauthn`, de Duo, con `supported_pub_key_algs` igual a `pubKeyCredParams`. La biblioteca no mira el largo del credential ID, `crossOrigin`, `topOrigin`, las extensiones, la atestación que se acepta ni que BE sea el guardado: lo comprueba el servidor. [webauthn 3.0.1](https://raw.githubusercontent.com/duo-labs/py_webauthn/v3.0.1/webauthn/registration/verify_registration_response.py)
- El servidor no pide extensiones.
- El cliente le manda al servidor la respuesta de `create()` o de `get()` entera, con `clientExtensionResults` y `transports`.
- La landing sirve `https://<dominio>/.well-known/assetlinks.json` como archivo estático, desde `static/.well-known/assetlinks.json`.
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

## Recuperación

Estándar: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt).

- La solicitud del código responde 404 si la cuenta no existe, y una IP que recibe 10 en 15 minutos queda bloqueada 30 minutos.
- Cada correo recibe un código por minuto, y hasta 5 por hora. Los SMS siguen los límites de [Código por SMS](#código-por-sms).
- Un código se invalida al tercer intento fallido.
- Con el código, una cuenta con contraseña la restablece, y una sin contraseña vincula una passkey o una contraseña.
- El código vive en Valkey, y uno nuevo reemplaza al anterior.
- El código vale una sola vez.
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

## Token de acceso

Estándar: el capítulo [V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md) de ASVS 5.0.

- El servidor firma y valida el JWT con PyJWT: `jwt.decode` recibe `algorithms=["HS256"]` y exige `exp` y `sid`. PyJWT acepta cualquier `typ` y parámetros como `kid` o `jku`, así que el servidor compara antes la cabecera entera. [PyJWT 2.15.1](https://raw.githubusercontent.com/jpadilla/pyjwt/2.15.1/jwt/api_jws.py)
- El token de acceso de una app es un JWT en la serialización compacta de JWS, firmado con HS256, que vence en 15 minutos. Lleva el id de su sesión en `sid` y el vencimiento en `exp`.
- La cabecera del JWT es `{"alg": "HS256", "typ": "at+jwt"}`.
- La clave del JWT son 256 bits aleatorios, nunca una contraseña, y solo firma con HS256.
- El servidor rechaza el JWT entero si no es un JWS compacto, si la firma no vale o si `exp` ya pasó, e ignora una claim que no conoce.
- La lista de sesiones cerradas vive en Valkey, y cada id queda en ella 15 minutos, lo que dura el último token de acceso de su sesión.
- El servidor rechaza el JWT de una sesión de una app que se cerró o se borró: su id va a una lista de sesiones cerradas ([ASVS 5.0 §7.4.1](../fuentes/owasp/ASVS_V7_Session_Management.md)).

## WebSocket

Estándar: el [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

- La web se autentica con la cookie de sesión del handshake, y una app, con `Authorization: Bearer` en el handshake, como en REST.
- Un handshake con la cookie exige un `Origin` igual al de la web, y uno con `Authorization` no lo revisa.
- Una sesión que no vale o un token vencido cierran la conexión con 4401, del rango de códigos de cierre privados. En el handshake, el servidor acepta la conexión para cerrarla: el navegador no le muestra a la web el código de un rechazo, que ve como un cierre 1006, igual que una caída de la red. [RFC 6455 §7.4.2](https://www.rfc-editor.org/rfc/rfc6455.txt), [WHATWG WebSockets](https://raw.githubusercontent.com/whatwg/websockets/7f25d7dc8c2598ebca795ce4af68909d913a3888/index.bs)
- Ante un 4401, una app refresca la sesión una sola vez y reconecta, y la web vuelve al inicio de sesión.
- El servidor no revalida cada cierto tiempo la sesión de una conexión abierta: el cierre llega con el borrado de la sesión, no en la siguiente revisión.
- Al refrescar la sesión, una app manda el token nuevo por la misma conexión ([WebSocket Security, *Session Management*](../fuentes/owasp/WebSocket_Security.md)).
- Cerrar o borrar una sesión cierra en el momento sus conexiones, y una sesión que vence también las cierra ([WebSocket Security, *Session Management*](../fuentes/owasp/WebSocket_Security.md)).
