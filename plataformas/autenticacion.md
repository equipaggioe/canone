# Autenticación

Cómo se registra una cuenta, cómo entra y cómo mantiene su sesión: lo que hace el servidor y lo que cumplen con él sus clientes. Lo propio de cada cliente va en su página.

## Código de autorización

Estándares: [RFC 6749](../fuentes/rfc/rfc6749.txt), [RFC 7636](../fuentes/rfc/rfc7636.txt), [RFC 8252](../fuentes/rfc/rfc8252.txt) y [RFC 9700](../fuentes/rfc/rfc9700.txt).

- Una app usa la passkey con la API de su sistema operativo cuando su framework la ofrece de forma oficial. Si no, la usa en el navegador del sistema, que le devuelve un código de autorización.
- Una app de Flet no usa passkeys: entra con contraseña o con código por SMS. Flet no tiene una API oficial de passkeys, y no está comprobado que `page.login()` abra el navegador del sistema y no un web-view.
- La URI de retorno de una app móvil es una URI `https` que reclama la app, y la de la app de escritorio, `http://127.0.0.1:{puerto}/<ruta>`, con el puerto que la app abre al pedir. El servidor no acepta otra: Windows y Linux no dejan que una app de Qt reclame una URI `https`. [Qt 6.12](https://doc.qt.io/qt-6.12/qoauthurischemereplyhandler.html)
- El código vive en Valkey, con la cuenta.
- La app abre la petición de autorización en el navegador del sistema, en una pestaña dentro de la app donde el sistema la ofrece, y nunca en un web-view ([RFC 8252 §5](../fuentes/rfc/rfc8252.txt), [§6](../fuentes/rfc/rfc8252.txt) y [§8.12](../fuentes/rfc/rfc8252.txt)).
- El endpoint de autorización autentica al usuario en cada petición, aunque el navegador tenga abierta una sesión de la web ([RFC 8252 §8.6](../fuentes/rfc/rfc8252.txt)).
- La petición de autorización lleva `code_challenge` con `code_challenge_method` `S256`. Sin él, o con `plain`, responde `invalid_request` ([RFC 7636 §4.2](../fuentes/rfc/rfc7636.txt) y [§4.4.1](../fuentes/rfc/rfc7636.txt)).
- El código son 256 bits aleatorios, vence a los 10 minutos y queda ligado al `client_id` y a la URI de retorno. Al canjearlo queda marcado como usado, con el id de la sesión que creó, y presentarlo de nuevo borra esa sesión ([RFC 6749 §4.1.2](../fuentes/rfc/rfc6749.txt) y [§10.10](../fuentes/rfc/rfc6749.txt)).
- El código guarda el `code_challenge` y el `code_challenge_method` de su petición ([RFC 7636 §4.4](../fuentes/rfc/rfc7636.txt)).
- Los endpoints no usan `scope`: una petición que lo trae responde `invalid_scope`, y el token da el acceso entero de la cuenta ([RFC 6749 §3.3](../fuentes/rfc/rfc6749.txt), [§4.1.2.1](../fuentes/rfc/rfc6749.txt) y [§5.2](../fuentes/rfc/rfc6749.txt)).
- La página de autorización no carga recursos ni enlaces de otros sitios ([RFC 9700 §4.2.4](../fuentes/rfc/rfc9700.txt)).
- La app crea el `code_verifier` ([RFC 7636 §4.1](../fuentes/rfc/rfc7636.txt) y [§7.1](../fuentes/rfc/rfc7636.txt)).
- La app manda un `state` aleatorio y rechaza la respuesta que no llega a la URI de retorno o con el `state` de su petición ([RFC 8252 §8.9](../fuentes/rfc/rfc8252.txt) y [§8.10](../fuentes/rfc/rfc8252.txt)).
- La app es un cliente público: está registrada en el servidor con su `client_id` y su URI de retorno completa, y no tiene secreto ([RFC 8252 §8.4](../fuentes/rfc/rfc8252.txt) y [§8.5](../fuentes/rfc/rfc8252.txt)).
- El servidor compara la URI de retorno con la registrada como cadena exacta, salvo el puerto de la de loopback ([RFC 8252 §7.3](../fuentes/rfc/rfc8252.txt) y [§8.4](../fuentes/rfc/rfc8252.txt)).
- Una petición de autorización sin `client_id`, o con un `client_id` o una URI de retorno que no son los registrados, muestra el error en el navegador y no redirige ([RFC 6749 §3.1.2.4](../fuentes/rfc/rfc6749.txt) y [§4.1.2.1](../fuentes/rfc/rfc6749.txt)).
- El endpoint de autorización acepta `GET`, y el de token, solo `POST` en `application/x-www-form-urlencoded` ([RFC 6749 §3.1](../fuentes/rfc/rfc6749.txt), [§3.2](../fuentes/rfc/rfc6749.txt) y [§4.1.3](../fuentes/rfc/rfc6749.txt)).
- Los dos endpoints toman un parámetro sin valor como ausente e ignoran el que no conocen, en vez de responder 422. Un parámetro repetido responde `invalid_request` ([RFC 6749 §3.1](../fuentes/rfc/rfc6749.txt), [§3.2](../fuentes/rfc/rfc6749.txt), [§4.1.2.1](../fuentes/rfc/rfc6749.txt) y [§5.2](../fuentes/rfc/rfc6749.txt)).
- `response_type` es `code`, y otro valor responde `unsupported_response_type` ([RFC 6749 §3.1.1](../fuentes/rfc/rfc6749.txt) y [§4.1.2.1](../fuentes/rfc/rfc6749.txt)).
- La respuesta lleva `code` y el `state` recibido en la query de la URI de retorno. Un error que no es de la URI de retorno ni del `client_id` vuelve igual, con `error` y el `state` ([RFC 6749 §4.1.2](../fuentes/rfc/rfc6749.txt) y [§4.1.2.1](../fuentes/rfc/rfc6749.txt)).
- El código vale una sola vez, y presentarlo de nuevo responde `invalid_grant` ([RFC 6749 §4.1.2](../fuentes/rfc/rfc6749.txt)).
- El canje lleva `grant_type=authorization_code`, el `code`, el `client_id` del código y, si la petición de autorización llevó `redirect_uri`, la misma. Responde `invalid_grant` si el `client_id` o la URI de retorno no coinciden ([RFC 6749 §4.1.3](../fuentes/rfc/rfc6749.txt) y [§5.2](../fuentes/rfc/rfc6749.txt)).
- El canje lleva el `code_verifier`, y responde `invalid_grant` si su SHA-256 en base64url no es el `code_challenge` ([RFC 7636 §4.5](../fuentes/rfc/rfc7636.txt) y [§4.6](../fuentes/rfc/rfc7636.txt)).
- El canje responde un 200 en JSON con `access_token`, `token_type` `Bearer`, `expires_in` 900 y `refresh_token`, y con `Cache-Control: no-store` y `Pragma: no-cache` ([RFC 6749 §5.1](../fuentes/rfc/rfc6749.txt)).
- Un error del endpoint de token es un 400 en JSON con `error`, uno de los códigos de su lista ([RFC 6749 §5.2](../fuentes/rfc/rfc6749.txt)).
- Una respuesta que redirige después de recibir una credencial usa 303, nunca 307 ([RFC 9700 §4.12](../fuentes/rfc/rfc9700.txt)).
- Ni el servidor ni la web redirigen a una URL que llega en un parámetro ([RFC 9700 §2.1](../fuentes/rfc/rfc9700.txt) y [§4.11.1](../fuentes/rfc/rfc9700.txt)).

## Código por SMS

Estándares: [*Origin-bound one-time codes delivered via SMS*](../fuentes/wicg/sms-one-time-codes.bs) de WICG y [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt).

- El número viaja y se guarda con `+`, el código de país y solo dígitos: escrito de otra forma, el mismo número crearía otra cuenta.
- El servidor valida el número con `phonenumbers`.
- Si un cliente es una app de Android, su hash va en la penúltima línea del SMS: el final de la última queda para la sintaxis futura del formato.
- Verificar el primer código de un número sin cuenta crea la cuenta.
- Un código nuevo reemplaza al anterior: solo vale el último.
- Cada número recibe un SMS por minuto, hasta 5 por hora y hasta 10 por día, y cada IP pide hasta 10 por hora.
- Un código se invalida al tercer intento fallido.
- El código vive en Valkey.
- El código tiene 6 dígitos ([NIST SP 800-63B-4 §3.1.3.2](../fuentes/nist/sp800-63b-4.txt)).
- El host de la última línea es el de la web donde se escribe el código ([SMS one-time codes, *Usage*](../fuentes/wicg/sms-one-time-codes.bs)).
- La última línea del SMS es `@<host> #<código>`, con un solo espacio en medio ([SMS one-time codes, *Parsing*](../fuentes/wicg/sms-one-time-codes.bs)).
- El SMS no termina en un salto de línea: su última línea es la del código ([SMS one-time codes, *Parsing*](../fuentes/wicg/sms-one-time-codes.bs)).
- Un código vence a los 10 minutos ([NIST SP 800-63B-4 §3.1.3.2](../fuentes/nist/sp800-63b-4.txt)).
- Un código vale una sola vez ([NIST SP 800-63B-4 §3.1.3.2](../fuentes/nist/sp800-63b-4.txt)).
- Cada fallo cuenta entre los fallos consecutivos del teléfono, y un código nuevo no los reinicia ([NIST SP 800-63B-4 §3.1.3.2](../fuentes/nist/sp800-63b-4.txt)).
- Un código por correo solo verifica la dirección o recupera la cuenta: el correo no sirve para entrar ([NIST SP 800-63B-4 §3.1.3.1](../fuentes/nist/sp800-63b-4.txt)).
- Al registrar un teléfono, el cliente avisa que el SMS es el autenticador más débil y ofrece agregar una passkey o una contraseña ([NIST SP 800-63B-4 §3.1.3.3](../fuentes/nist/sp800-63b-4.txt) y [§3.2.9](../fuentes/nist/sp800-63b-4.txt)).

## Contraseñas

Estándares: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt), el [*Password Storage Cheat Sheet*](../fuentes/owasp/Password_Storage.md) de OWASP y el capítulo [V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md) de ASVS 5.0.

- Toda contraseña tiene al menos 8 caracteres, aunque sea el único factor: una de 15 aleja al usuario.
- El login con contraseña responde el mismo error exista o no la cuenta.
- Cambiar la contraseña renueva los tokens de la sesión que hizo el cambio.
- La lista de bloqueo es un archivo del servidor.
- La contraseña la elige el titular ([NIST SP 800-63B-4 §3.1.1.1](../fuentes/nist/sp800-63b-4.txt)).
- El servidor no limita el largo de una contraseña por debajo de 64 caracteres ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Una contraseña admite todo carácter ASCII imprimible, el espacio y cualquier carácter Unicode, y cada punto de código cuenta como un carácter ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- La contraseña se normaliza a NFC antes del hash ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- La lista de bloqueo tiene las contraseñas comunes, esperadas o filtradas que un atacante probaría antes del límite de fallos ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Una contraseña se guarda con `PasswordHash.recommended()` de pwdlib: Argon2id con 64 MiB y 3 pasadas, por encima de los mínimos de OWASP ([Password Storage Cheat Sheet, *Argon2id*](../fuentes/owasp/Password_Storage.md)).
- El hash se guarda en el formato PHC, con el algoritmo y sus parámetros ([Password Storage Cheat Sheet, *Upgrading Legacy Hashes*](../fuentes/owasp/Password_Storage.md)).
- Cambiar la contraseña cierra las demás sesiones, y restablecerla, todas ([ASVS 5.0 §7.4.3](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- La guía para elegir la contraseña avisa que un carácter fuera de ASCII puede escribirse distinto en otro dispositivo ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- El campo de la contraseña admite pegar ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- El campo de la contraseña ofrece mostrarla mientras se escribe ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- No hay otras reglas de composición, ni cambio periódico, ni pistas, ni preguntas de seguridad ([NIST SP 800-63B-4 §3.1.1.1](../fuentes/nist/sp800-63b-4.txt) y [§3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- El servidor obliga a cambiar una contraseña cuando hay evidencia de que se comprometió ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- El servidor verifica la contraseña entera, sin truncarla ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Crear o cambiar una contraseña la compara entera contra la lista de bloqueo, y una que está en ella se rechaza diciendo por qué ([NIST SP 800-63B-4 §3.1.1.1](../fuentes/nist/sp800-63b-4.txt) y [§3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Cada hash lleva su propia sal aleatoria ([Password Storage Cheat Sheet, *Salting*](../fuentes/owasp/Password_Storage.md)).
- El cliente muestra una guía para elegir una contraseña fuerte, y la repite al rechazar una de la lista de bloqueo ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).
- El campo de la contraseña admite el autocompletado de los gestores de contraseñas ([NIST SP 800-63B-4 §3.1.1.2](../fuentes/nist/sp800-63b-4.txt)).

## Cuentas

Estándares: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt) y el capítulo [V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md) de ASVS 5.0.

- El correo y el teléfono identifican la cuenta: cada uno pertenece a una sola, y el registro responde 409 si la cuenta ya existe.
- Una cuenta no tiene nombre de usuario.
- Una IP que recibe 10 respuestas 409 del registro en 15 minutos queda bloqueada 30 minutos: quien prueba correos o teléfonos en serie busca cuentas existentes.
- El correo y el teléfono se cambian desde una sesión abierta, con un código enviado al nuevo, y el viejo recibe un aviso.
- El titular ve en la app cada intento fallido y cada autenticador deshabilitado.
- Un autenticador deshabilitado cierra solo el login con él: las sesiones abiertas siguen.
- Los fallos consecutivos y la hora del siguiente intento viven en la base: sin ventana de tiempo, perderlos le regala al atacante 100 intentos nuevos.
- Una cuenta de usuario entra con un solo factor: una contraseña, un código por SMS o una passkey ([NIST SP 800-63B-4 §2.1.1](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta de administración entra solo con passkeys que verifican al usuario: dos factores en un autenticador resistente al phishing ([NIST SP 800-63B-4 §2.2.1](../fuentes/nist/sp800-63b-4.txt) y [§2.2.2](../fuentes/nist/sp800-63b-4.txt)).
- Las direcciones de aviso son el correo, el teléfono y el push a las apps con sesión abierta: una cuenta con un solo medio también tiene dos ([NIST SP 800-63B-4 §4.6](../fuentes/nist/sp800-63b-4.txt)).
- Cada autenticador guarda cuándo se vinculó y cuándo cambió, y cada uno de esos eventos va al registro de eventos con su IP y su user agent ([NIST SP 800-63B-4 §4.1](../fuentes/nist/sp800-63b-4.txt)).
- Desde el quinto fallo consecutivo, el siguiente intento espera 30 segundos, que se duplican con cada fallo hasta una hora, y un intento antes de tiempo responde 429: llegar a los 100 fallos lleva unos cuatro días, y el titular lo ve antes ([NIST SP 800-63B-4 §3.2.2](../fuentes/nist/sp800-63b-4.txt)).
- Un inicio de sesión exitoso pone en cero los fallos de los autenticadores que usó ([NIST SP 800-63B-4 §3.2.2](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta se registra con un correo o con un teléfono, verificado con un código como el de [Recuperación](#recuperación) ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta puede tener un correo, un teléfono y varias passkeys, y una de usuario, también una contraseña ([NIST SP 800-63B-4 §4.1.2.1](../fuentes/nist/sp800-63b-4.txt) y [§4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Agregar o borrar una passkey, agregar o cambiar la contraseña y cambiar el correo o el teléfono piden volver a autenticarse en ese momento ([ASVS 5.0 §7.5.1](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- Vincular, cambiar o borrar un autenticador, y recuperar la cuenta, avisa a todas las direcciones de aviso. El aviso dice qué hacer, y a quién escribir, si el titular no lo hizo ([NIST SP 800-63B-4 §4.1.2.1](../fuentes/nist/sp800-63b-4.txt), [§4.2.3](../fuentes/nist/sp800-63b-4.txt), [§4.5](../fuentes/nist/sp800-63b-4.txt) y [§4.6](../fuentes/nist/sp800-63b-4.txt)).
- Un autenticador se deshabilita a los 100 fallos consecutivos. Si los fallos involucran dos autenticadores, se deshabilitan los dos ([NIST SP 800-63B-4 §3.2.2](../fuentes/nist/sp800-63b-4.txt)).
- El titular vuelve a habilitarlo desde una sesión abierta o, si es la contraseña, restableciéndola ([NIST SP 800-63B-4 §3.2.2](../fuentes/nist/sp800-63b-4.txt)).
- El titular invalida en el acto un autenticador perdido o robado, borrando la passkey o cambiando el teléfono, y la app le explica cómo protegerlos ([NIST SP 800-63B-4 §3.2.1](../fuentes/nist/sp800-63b-4.txt) y [§4.3](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta que se borra o se deshabilita pierde en el momento sus autenticadores ([NIST SP 800-63B-4 §4.5](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta que se borra o se deshabilita pierde en el momento sus sesiones ([ASVS 5.0 §7.4.2](../fuentes/owasp/ASVS_V7_Session_Management.md)).

## Passkeys

Estándares: [*Web Authentication Level 3*](../fuentes/w3c/webauthn-3.html) de W3C, [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt) y los [requisitos de Credential Manager](../fuentes/android/credential-manager-prerequisites.md) de Android.

- El servidor verifica las passkeys con `verify_registration_response` y `verify_authentication_response` de `webauthn`, de Duo, con `supported_pub_key_algs` igual a `pubKeyCredParams` y `require_user_verification` en una cuenta de administración. La biblioteca no mira el largo del credential ID, `crossOrigin`, `topOrigin`, las extensiones, la atestación que se acepta ni que BE sea el guardado: lo comprueba el servidor. [webauthn 3.0.1](https://raw.githubusercontent.com/duo-labs/py_webauthn/v3.0.1/webauthn/registration/verify_registration_response.py)
- El servidor no pide extensiones.
- El cliente le manda al servidor la respuesta de `create()` o de `get()` entera, con `clientExtensionResults` y `transports`.
- El challenge vive en Valkey 10 minutos.
- La landing sirve `https://<dominio>/.well-known/assetlinks.json` como archivo estático, desde `static/.well-known/assetlinks.json`.
- `assetlinks.json` declara para la app de Android la relación `delegate_permission/common.get_login_creds`, con el `namespace` `android_app`, su `package_name` y la huella SHA-256 del certificado con que Play la firma ([Prerequisites, *Create the Digital Asset Links JSON file*](../fuentes/android/credential-manager-prerequisites.md)).
- Esa URL responde 200, con `Content-Type: application/json` y sin redirecciones ([Prerequisites, *Host the Digital Asset Links JSON file*](../fuentes/android/credential-manager-prerequisites.md) y [*Configure Digital Asset Links for passwords*](../fuentes/android/credential-manager-prerequisites.md)).
- Si `<dominio>` sirve un `robots.txt`, este permite `/.well-known/` ([Prerequisites, *Allow retrieval of the Digital Asset Links file*](../fuentes/android/credential-manager-prerequisites.md)).
- El RP ID es `<dominio>`: una misma passkey sirve en `app.<dominio>` y en `panel.<dominio>` ([WebAuthn §5.4.2](../fuentes/w3c/webauthn-3.html)).
- Toda passkey es descubrible, con `residentKey` `required` y `requireResidentKey` `true`: el usuario entra sin escribir su correo ([WebAuthn §5.4.4](../fuentes/w3c/webauthn-3.html)).
- `userVerification` es `preferred` en una cuenta de usuario y `required` en una de administración ([WebAuthn §5.4.4](../fuentes/w3c/webauthn-3.html) y [§5.5](../fuentes/w3c/webauthn-3.html)).
- `attestation` es `none`: la mayoría de las passkeys de consumo no tienen atestación ([WebAuthn §5.4.7](../fuentes/w3c/webauthn-3.html)).
- El registro acepta la atestación `none` y la propia, `packed` sin `x5c`, que el navegador entrega aunque se pida `none`. Otra hace fallar el registro ([WebAuthn §5.4.7](../fuentes/w3c/webauthn-3.html) y [§7.1](../fuentes/w3c/webauthn-3.html)).
- Un `clientExtensionResults` que no está vacío hace fallar el registro o el login: solo lo llena una extensión que agregó el cliente, y eso es un error de su código ([WebAuthn §7.1](../fuentes/w3c/webauthn-3.html), [§7.2](../fuentes/w3c/webauthn-3.html) y [§9.4](../fuentes/w3c/webauthn-3.html)).
- En el registro, el `authData` acepta solo la extensión `credProtect`, con un valor de 1 a 3: Chrome se la pide a la llave por su cuenta al crear una passkey descubrible, y la llave la devuelve. En el login no acepta ninguna. Otra extensión hace fallar la ceremonia y va al registro de eventos con su nombre ([WebAuthn §7.1](../fuentes/w3c/webauthn-3.html), [§7.2](../fuentes/w3c/webauthn-3.html) y [§9.5](../fuentes/w3c/webauthn-3.html)). [Chrome](https://lists.w3.org/Archives/Public/public-webauthn-adoption/2023Mar/0000.html), [CTAP 2.1 §12.1](https://fidoalliance.org/specs/fido-v2.1-ps-20210615/fido-client-to-authenticator-protocol-v2.1-ps-errata-20220621.html)
- `rp.name` es el RP ID; `user.name`, el correo o el teléfono de la cuenta, y `user.displayName`, el nombre que elige el titular ([WebAuthn §5.4.1](../fuentes/w3c/webauthn-3.html) y [§5.4.3](../fuentes/w3c/webauthn-3.html)).
- `pubKeyCredParams` lleva EdDSA (-8), ES256 (-7) y RS256 (-257), en ese orden ([WebAuthn §5.4](../fuentes/w3c/webauthn-3.html)).
- `excludeCredentials` lista las passkeys de la cuenta: dos passkeys de una cuenta no quedan en el mismo autenticador ([WebAuthn §5.4](../fuentes/w3c/webauthn-3.html) y [§13.4.6](../fuentes/w3c/webauthn-3.html)).
- El user handle son 64 bytes aleatorios que guarda la cuenta, sin datos personales ([WebAuthn §5.4.3](../fuentes/w3c/webauthn-3.html) y [§14.6.1](../fuentes/w3c/webauthn-3.html)).
- El login deja `allowCredentials` vacío. Al volver a autenticarse, `allowCredentials` lista las passkeys de la cuenta, con sus `transports` ([WebAuthn §5.5](../fuentes/w3c/webauthn-3.html)).
- El challenge son 16 bytes aleatorios que genera el servidor, y se borra al usarlo ([WebAuthn §13.4.3](../fuentes/w3c/webauthn-3.html)).
- El servidor compara `origin` exacto contra una lista fija: el de cada superficie web y el de cada app que usa la API de su sistema ([WebAuthn §13.4.8](../fuentes/w3c/webauthn-3.html) y [§13.4.9](../fuentes/w3c/webauthn-3.html)).
- Una ceremonia con `crossOrigin` verdadero o con `topOrigin` se rechaza: ninguna superficie se carga dentro de otra ([WebAuthn §7.1](../fuentes/w3c/webauthn-3.html) y [§7.2](../fuentes/w3c/webauthn-3.html)).
- Un credential ID de más de 1023 bytes, o que ya es de otra passkey, hace fallar el registro ([WebAuthn §7.1](../fuentes/w3c/webauthn-3.html)).
- Si el `signCount` de la aserción o el guardado no es cero y el nuevo no es mayor, el login falla y el titular recibe un aviso: la passkey puede estar clonada ([WebAuthn §6.1.1](../fuentes/w3c/webauthn-3.html) y [§7.2](../fuentes/w3c/webauthn-3.html)).
- El servidor guarda el `signCount` y el `backupState` nuevos después de las demás comprobaciones del login, y `uvInitialized` queda como se registró ([WebAuthn §7.2](../fuentes/w3c/webauthn-3.html)).
- Si el `backupState` de una passkey pasa de 1 a 0, la app le pide al titular revisar sus otros autenticadores y, si no tiene otro, agregar uno ([WebAuthn §6.1.3](../fuentes/w3c/webauthn-3.html)).
- Al registrar una passkey, el servidor comprueba que `type` sea `webauthn.create`, el challenge, el `origin`, que `rpIdHash` sea el del RP ID, el bit UP, el bit UV si la cuenta lo exige, que BS no esté sin BE, que el `alg` de la clave esté en `pubKeyCredParams` y la atestación con su formato ([WebAuthn §7.1](../fuentes/w3c/webauthn-3.html)).
- Cada passkey guarda su credential ID, su clave pública, `signCount`, `uvInitialized`, `transports`, `backupEligible`, `backupState`, su nombre, su creación y su último uso ([WebAuthn §6.1.3](../fuentes/w3c/webauthn-3.html) y [§7.1](../fuentes/w3c/webauthn-3.html)).
- Al autenticar, el servidor busca la passkey por el user handle y el credential ID o, al volver a autenticarse, entre las de la cuenta. Comprueba que `type` sea `webauthn.get`, el challenge, el `origin`, que `rpIdHash` sea el del RP ID, el bit UP, el bit UV si la cuenta lo exige, que BS no esté sin BE, que BE sea el que se guardó y la firma con la clave guardada ([WebAuthn §7.2](../fuentes/w3c/webauthn-3.html)).
- El titular ve sus passkeys, con su nombre y su último uso, y borra la que quiera: así revoca la de un dispositivo perdido ([NIST SP 800-63B-4 §3.2.1](../fuentes/nist/sp800-63b-4.txt)).

## Recuperación

Estándar: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt).

- La solicitud del código responde 404 si la cuenta no existe, y una IP que recibe 10 en 15 minutos queda bloqueada 30 minutos: el registro ya revela si la cuenta existe.
- Cada correo y cada número reciben un código por minuto, y hasta 5 por hora.
- Un código se invalida al tercer intento fallido.
- Con el código, una cuenta con contraseña la restablece.
- El código vive en Valkey, y uno nuevo reemplaza al anterior.
- Una cuenta con passkey se recupera con el mismo código, que se aplica 24 horas después, sin cerrar las sesiones, y el titular la cancela desde la app: quien roba el correo no entra antes de que el dueño la vea.
- Una cuenta de usuario se recupera con un código que recibe, a su elección, en el correo o en el teléfono que registró ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt) y [§4.2.2.1](../fuentes/nist/sp800-63b-4.txt)).
- El código vence a los 10 minutos, también el que va al correo ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Una cuenta de administración la recupera otro administrador, nunca un código: quien roba el correo o el teléfono no se lleva la administración ([NIST SP 800-63B-4 §4.2.1](../fuentes/nist/sp800-63b-4.txt)).
- Quien perdió su número y no tiene otra forma de entrar recupera la cuenta con un administrador ([NIST SP 800-63B-4 §4.2.1](../fuentes/nist/sp800-63b-4.txt)).
- El código tiene 6 dígitos ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).
- Cada fallo cuenta entre los fallos consecutivos de la contraseña ([NIST SP 800-63B-4 §4.2.1.2](../fuentes/nist/sp800-63b-4.txt)).

## Sesión

Estándares: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt); de ASVS 5.0, los capítulos [V3 *Web Frontend Security*](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md) y [V7 *Session Management*](../fuentes/owasp/ASVS_V7_Session_Management.md); [RFC 6749](../fuentes/rfc/rfc6749.txt); [RFC 9700](../fuentes/rfc/rfc9700.txt); [RFC 9110](../fuentes/rfc/rfc9110.txt), y el [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md) de OWASP.

- La web presenta su sesión con una cookie, y una app, con un token de acceso que renueva con un token de refresco. En la web, ningún token queda al alcance de un script.
- La web y las apps comparten la tabla de sesiones: cambia solo el token que presenta cada una.
- Una sesión de usuario no tiene vencimiento total: pedir entrar de nuevo cada mes aleja al usuario de una app de uso diario, y el refresco rotado descubre un token robado cuando el dueño vuelve a refrescar.
- La sesión vence tras 30 días sin uso.
- La cookie de la web dura 30 días de `Max-Age`, que se renuevan con el último uso.
- El último uso se actualiza al refrescar, en una app, y a lo sumo cada 15 minutos, en la web: una escritura por petición cargaría la base sin mover el vencimiento.
- Una tarea periódica borra las sesiones vencidas.
- En una app, el token de acceso vive solo en memoria, y el de refresco, en el almacenamiento seguro del sistema: ningún almacenamiento guarda un token que da acceso directo a la API.
- Una app hace un solo refresco a la vez, y las peticiones que reciben un 401 mientras tanto lo esperan. Con la rotación, dos refrescos simultáneos presentan tokens ya rotados.
- Ante un 401, una app refresca la sesión una sola vez y reintenta una sola vez.
- Una app que entra con contraseña, con código por SMS o con la passkey de su sistema recibe la misma respuesta que el canje del código: así todas las apps leen una sola.
- La fila de una sesión de una app guarda el SHA-256 del secreto vigente y el del anterior. El anterior vale mientras el vigente no se usó: una respuesta perdida cerraría la sesión del dueño y le avisaría de un robo.
- Presentar el anterior reemplaza el vigente, y el anterior no cambia. Si el vigente pasara a ser el anterior, un dueño y un ladrón que refrescan por turnos nunca presentarían un reúso.
- Un token de refresco con la firma inválida o de una sesión que no existe responde `invalid_grant`, sin aviso.
- Un 401 a la cookie de la web no lleva `WWW-Authenticate`: la cookie no es un esquema de autenticación de HTTP.
- La fila de la sesión guarda el SHA-256 del token de la web: quien lee la base no se lleva ninguna sesión.
- El token de refresco es el id de su sesión y un secreto aleatorio de 256 bits, firmados con HMAC.
- Iniciar sesión o volver a autenticarse crea o renueva la fila de sesión, con su creación y su último uso.
- La API se sirve en el mismo origen que la web, bajo `/api`, sin `Access-Control-Allow-Origin`: la cookie de sesión es de primera parte ([HTTP Security Response Headers Cheat Sheet, *Access-Control-Allow-Origin*](../fuentes/owasp/HTTP_Headers.md)).
- Cerrar sesión borra la fila ([RFC 9700 §4.14.2](../fuentes/rfc/rfc9700.txt)).
- Una sesión de una cuenta de administración vence a las 24 horas de iniciarse o tras 1 hora sin uso, y volver a autenticarse reinicia los dos plazos ([NIST SP 800-63B-4 §2.2.3](../fuentes/nist/sp800-63b-4.txt) y [§5.2](../fuentes/nist/sp800-63b-4.txt)).
- El token de la web es un valor aleatorio de 256 bits ([ASVS 5.0 §7.2.3](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- La cookie de la web es `__Host-session`, `Secure`, `HttpOnly` y `SameSite=Strict`, con `Path=/`: ningún script la lee, ninguna petición de otro sitio la lleva y ningún subdominio la reemplaza ([ASVS 5.0 §3.3.1](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md), [§3.3.2](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md), [§3.3.3](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md) y [§3.3.4](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md)).
- Una petición con la cookie y un método que no es seguro responde 403 si su `Origin` falta o no es el del servidor: no le pide nada a la web ([ASVS 5.0 §3.5.2](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md)).
- El secreto del token de refresco rota en cada uso ([RFC 9700 §2.2.2](../fuentes/rfc/rfc9700.txt) y [§4.14.2](../fuentes/rfc/rfc9700.txt)).
- Cualquier otro secreto de la sesión es un reúso: borra la sesión, y el titular lo ve en la app. Un token robado se descubre cuando el dueño vuelve a refrescar ([RFC 9700 §4.14.2](../fuentes/rfc/rfc9700.txt)).
- Iniciar sesión o volver a autenticarse emite tokens nuevos y deja sin efecto los que el cliente traía ([ASVS 5.0 §7.2.4](../fuentes/owasp/ASVS_V7_Session_Management.md)).
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
- El servidor rechaza el JWT entero si no es un JWS compacto, si su cabecera no es esa, si la firma no vale o si `exp` ya pasó, e ignora una claim que no conoce.
- La lista de sesiones cerradas vive en Valkey, y cada id queda en ella 15 minutos, lo que dura el último token de acceso de su sesión.
- El servidor rechaza el JWT de una sesión de una app que se cerró o se borró: su id va a una lista de sesiones cerradas ([ASVS 5.0 §7.4.1](../fuentes/owasp/ASVS_V7_Session_Management.md)).

## WebSocket

Estándar: el [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

- La web se autentica con la cookie de sesión del handshake, y una app, con `Authorization: Bearer` en el handshake, como en REST.
- Una sesión que no vale o un token vencido cierran la conexión con 4401, del rango de códigos de cierre privados: un código propio separa la sesión de cualquier otro cierre. En el handshake, el servidor acepta la conexión para cerrarla: el navegador no le muestra a la web el código de un rechazo, que ve como un cierre 1006, igual que una caída de la red. [RFC 6455 §7.4.2](https://www.rfc-editor.org/rfc/rfc6455.txt), [WHATWG WebSockets](https://raw.githubusercontent.com/whatwg/websockets/7f25d7dc8c2598ebca795ce4af68909d913a3888/index.bs)
- Ante un 4401, una app refresca la sesión una sola vez y reconecta, y la web vuelve al inicio de sesión.
- El servidor no revalida cada cierto tiempo la sesión de una conexión abierta: el cierre llega con el borrado de la sesión, no en la siguiente revisión.
- Al refrescar la sesión, una app manda el token nuevo por la misma conexión ([WebSocket Security, *Session Management*](../fuentes/owasp/WebSocket_Security.md)).
- Cerrar o borrar una sesión cierra en el momento sus conexiones, y una sesión que vence también las cierra ([WebSocket Security, *Session Management*](../fuentes/owasp/WebSocket_Security.md)).
