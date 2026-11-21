# ADR-0207 · `autenticacion.md` deja lo que tiene una sola forma, el titular cierra sus sesiones, y el flujo del navegador se liga a una cookie

- **Estado:** Aceptada. El usuario pidió aplicar los veredictos de la revisión y confirmó uno por uno los puntos 4, 5, 9, 10 y 11 (2026-11-20)
- **Fecha:** 2026-11-20
- **Alcance:** [plataformas/autenticacion.md](../plataformas/autenticacion.md), «WebSocket» de [plataformas/fastapi.md](../plataformas/fastapi.md) y `fuentes/`

## Contexto

Se revisó `autenticacion.md` con los cinco pasos de [plataformas/README.md](../plataformas/README.md#revisión). Lo comprobado, con sus versiones:

- pwdlib 0.4.2 con argon2-cffi 25.1.0: `PasswordHash.recommended()` guarda `$argon2id$v=19$m=65536,t=3,p=4$…`, en formato PHC y con una sal distinta en cada hash, y no normaliza: «café» en NFD no verifica contra su hash en NFC.
- FastAPI 0.163.1 con Starlette 1.10.0: ignora un parámetro desconocido; toma un parámetro de query vacío como `""` y uno de formulario vacío como ausente; de uno repetido se queda con el último, y uno obligatorio que falta responde 422.
- Chrome 157.0.8103.79, sin interfaz: un handshake de WebSocket rechazado con 403 llega a la página como cierre 1006, y uno aceptado y cerrado con 4401 llega como 4401. Una cookie `__Host-` `SameSite=Strict` que deja el endpoint que inicia el flujo llega al endpoint de retorno tras un 302, un `POST` y un 303 en el mismo origen. Con una llave virtual CTAP 2.1 y con un autenticador de plataforma virtual, `getClientExtensionResults()` devuelve `{}` en el registro y en el login, y el `authData` no trae extensiones. Sin confirmar si la llave virtual admite `credProtect`.
- El código de Chromium (`main`, leído el 2026-11-20): `ProtectionPolicyToCredProtect`, en `content/browser/webauth/authenticator_common_impl.cc`, pide `credProtect` 3 cuando el sitio no lo pide, `residentKey` es `required` y `userVerification` es `preferred`, y `make_credential_request_handler.cc` lo manda solo si la llave lo admite.
- El rotado del refresco se simuló: con el anterior que no cambia, un ladrón y un dueño que refrescan por turnos presentan un reúso en el segundo turno; si el vigente pasara a ser el anterior, nunca. Desde el quinto fallo, llegar a 100 lleva 320 610 s, unos 3,7 días.
- La página de Apple sobre los códigos de un SMS dice que el autocompletado sugiere el código si su dominio es uno de los dominios asociados de la app, sin nombrar `webcredentials`.

Las razones que salen de la página, porque las convenciones no se apartan de una fuente ni la endurecen:

- El número con `+`, el código de país y solo dígitos: escrito de otra forma, el mismo número crearía otra cuenta.
- El bloqueo de la IP tras 10 respuestas 409: quien prueba correos o teléfonos en serie busca cuentas existentes.
- Los fallos consecutivos en la base: sin ventana de tiempo, perderlos le regala al atacante 100 intentos nuevos.
- El usuario elige entre el código por SMS y la contraseña: él sabe si el dispositivo recibe SMS.
- El RP ID `<dominio>`: una misma passkey sirve en `app.<dominio>` y en `panel.<dominio>`.
- Toda passkey descubrible: el usuario entra sin escribir su correo.
- `attestation` `none`: la mayoría de las passkeys de consumo no tienen atestación.
- Un `clientExtensionResults` no vacío falla: solo lo llena una extensión que agregó el cliente, y eso es un error de su código.
- Se rechazan `crossOrigin` y `topOrigin`: ninguna superficie se carga dentro de otra.
- La espera de 24 horas con el código del correo: quien roba el correo no entra antes de que el dueño la vea; con el código del teléfono la cuenta ya entra.
- El último uso cada 15 minutos en la web: una escritura por petición cargaría la base sin mover el vencimiento.
- El token de acceso solo en memoria: ningún almacenamiento guarda un token que da acceso directo a la API.
- Un solo refresco a la vez: con la rotación, dos refrescos simultáneos presentan tokens ya rotados.
- La misma respuesta para todos los métodos: así todas las apps leen una sola.
- El SHA-256 del token de la web: quien lee la base no se lleva ninguna sesión.
- El mismo origen sin `Access-Control-Allow-Origin`: la cookie de sesión es de primera parte.
- El `Origin` solo en el handshake con la cookie: una app nativa no manda `Origin`, y el secuestro entre sitios solo existe con la credencial que el navegador agrega por su cuenta.

## Decisión

1. Salen las convenciones que tienen una sola forma: el código guarda su `code_challenge`, el formato de la respuesta de autorización, la sintaxis `@<host> #<código>` y el SMS sin salto final, los pasos de §7.1 y §7.2 de WebAuthn que `webauthn` ya cumple, el PHC y la sal de pwdlib, App Links con `handle_all_urls`, y la relación, el código 200 y el `robots.txt` de `assetlinks.json`.
2. Salen el login que responde el mismo error exista o no la cuenta, porque el registro y la recuperación ya lo revelan, y la renovación de los tokens al cambiar la contraseña, que ya hace la reautenticación. Reemplaza el punto 6 del [ADR-0045](0045-el-login-y-las-contrasenas-siguen-el-nivel-1-de-asvs.md) y, en los tokens, el punto 7 del [ADR-0044](0044-el-bloqueo-cuenta-en-una-ventana-y-el-titular-lo-ve-en-la-app.md).
3. El titular ve sus sesiones abiertas y, después de volver a autenticarse, cierra la que quiera o todas (ASVS 5.0 §7.5.2).
4. En el flujo de la app que corre en el navegador, el endpoint que lo inicia guarda el `state` y el `code_verifier` en Valkey, bajo un id que deja en una cookie `__Host-` `Secure`, `HttpOnly` y `SameSite=Strict`, y el endpoint de retorno los toma una sola vez y borra la cookie.
5. Una app de escritorio recibe el retorno solo en `127.0.0.1`, no en `[::1]`, y la convención lleva esa razón.
6. Quien inicia el flujo crea el `code_verifier` con 32 bytes aleatorios en base64url. `expires_in` es lo que dura el token de acceso. No se redirige a una URL que llega en un parámetro y no está registrada. `user.displayName` va vacío. El challenge de una passkey vive 10 minutos, con el origen §13.4.3.
7. El host del SMS, el `Access-Control-Allow-Origin` y el hash de las contraseñas pasan a convenciones propias. El *Password Storage Cheat Sheet* y *Origin-bound one-time codes delivered via SMS* dejan de ser fuentes y salen de `fuentes/`; los requisitos de Credential Manager salen de `autenticacion.md`.
8. El `Origin` de un `POST` con la cookie toma su origen de ASVS 5.0 §3.5.1. El `Origin` del handshake con la cookie pasa de `fastapi.md` a «WebSocket» de `autenticacion.md`.
9. Cerrar las demás sesiones al cambiar la contraseña lleva su razón: quien la cambia porque la cree robada no deja abierta la sesión del ladrón.
10. Con el código de recuperación, una cuenta sin contraseña vincula una passkey o una contraseña, y cada fallo cuenta entre los fallos consecutivos de la recuperación de la cuenta, tenga o no contraseña.
11. Los endpoints de OAuth responden `invalid_request`, nunca 422, a un parámetro repetido o a uno obligatorio que falta.
12. En cada sección, las elecciones y los endurecimientos van antes que las convenciones adoptadas.

## Consecuencias

- Una cuenta con solo passkeys puede cerrar la sesión de un teléfono robado.
- Una cuenta sin contraseña tiene límite acumulado de fallos en la recuperación.
- La página ya no tiene sección «Cumplimiento»: falta una plantilla de autenticación del servidor que la pruebe.
- `android.md` sigue citando los requisitos de Credential Manager en una sola convención.

## Descartado

- **Adoptar §7.3 de RFC 8252, escuchar en IPv4 y en IPv6:** toda máquina de escritorio tiene loopback IPv4, y las apps ya lo usan.
- **Dejar `webcredentials:` en la convención de iOS:** la página de Apple que la respalda no lo nombra.
