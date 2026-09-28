# Seguridad

Autenticación, sesión y defensa. Aplica al servidor y a cada cliente.

## Contraseñas

Estándares: [NIST SP 800-63B-4](../estandares/nist/sp800-63b-4.txt),
[*Password Storage Cheat Sheet*](../estandares/owasp/Password_Storage.md) de OWASP,
[RFC 9106](../estandares/rfc/rfc9106.txt) y
[*OAuth2 with Password (and hashing), Bearer with JWT tokens*](../estandares/fastapi/oauth2-jwt.md)
de FastAPI.

- Toda contraseña tiene al menos 15 caracteres, con o sin segundo factor. Endurece NIST, que admite
  8 con segundo factor: una sola regla, y el segundo factor se puede desactivar.
- La lista de bloqueo que pide NIST es una lista de contraseñas comunes guardada en el servidor. La
  contraseña no sale a otro servicio para compararla.

## Autenticación

Estándares: [*Authentication Cheat Sheet*](../estandares/owasp/Authentication.md),
[*Credential Stuffing Prevention Cheat Sheet*](../estandares/owasp/Credential_Stuffing_Prevention.md)
y [*Forgot Password Cheat Sheet*](../estandares/owasp/Forgot_Password.md) de OWASP.

- El enlace para restablecer la contraseña lleva un token aleatorio de un solo uso que vence en 30
  minutos, y la base guarda su SHA-256.

## Tokens

Estándares: [RFC 7519](../estandares/rfc/rfc7519.txt), [RFC 8725](../estandares/rfc/rfc8725.txt)
y [*JSON Web Token Cheat Sheet*](../estandares/owasp/JSON_Web_Token.md) de OWASP.

- El token de acceso es un JWT firmado con HS256 que vence en 15 minutos. Solo el servidor lo firma
  y lo verifica, así que basta una clave simétrica.
- El token de refresco es un valor aleatorio de 256 bits, y la base guarda su SHA-256 en la fila de
  sesión. Rota en cada uso, y usar uno ya rotado borra la sesión entera: un token robado se
  descubre cuando el dueño vuelve a refrescar.
- Cada dispositivo tiene una fila de sesión, con su creación y su último uso. La sesión vence tras
  30 días sin uso, y cerrar sesión borra la fila.

## Sesión

Estándares: [*Session Management Cheat Sheet*](../estandares/owasp/Session_Management.md) y
[*Cross-Site Request Forgery Prevention Cheat Sheet*](../estandares/owasp/Cross-Site_Request_Forgery_Prevention.md)
de OWASP, y [RFC 6265](../estandares/rfc/rfc6265.txt).

- La API se sirve en el mismo origen que la web, bajo `/api`. No hace falta CORS, y la cookie de
  sesión es de primera parte.

## Segundo factor

Estándares: [RFC 6238](../estandares/rfc/rfc6238.txt), [RFC 4226](../estandares/rfc/rfc4226.txt)
y [*Multifactor Authentication Cheat Sheet*](../estandares/owasp/Multifactor_Authentication.md) de
OWASP.

- El segundo factor es TOTP con SHA-1, 6 dígitos y pasos de 30 segundos. Son los valores que
  aceptan todas las apps de autenticación.
- El secreto TOTP se guarda cifrado con una clave de la configuración. Una copia de la base no basta
  para generar códigos.
- Al activarlo se entregan diez códigos de recuperación de un solo uso, guardados como hash. Perder
  el teléfono no deja la cuenta sin acceso.

## Qué guarda cada cliente

Estándares: [*HTML5 Security Cheat Sheet*](../estandares/owasp/HTML5_Security.md) de OWASP,
[flutter_secure_storage](../estandares/pub/flutter_secure_storage/README.md),
[`SecureStorage`](../estandares/flet/securestorage.md) de Flet y el
[Keystore de Android](../estandares/android/keystore.md).

- El token de acceso vive solo en memoria. El de refresco se guarda así:

| Cliente | Token de refresco |
|---|---|
| Web | Cookie `HttpOnly`, `Secure`, `SameSite=Strict`, con el `Path` del endpoint de refresco |
| Flutter | flutter_secure_storage |
| Android | DataStore cifrado con el Keystore, como fija [android.md](android.md) |
| Flet | `SecureStorage` |
| Qt | keyring de Python, que usa el almacén de credenciales del sistema |

## Límite de tasa

Estándares: [RFC 6585](../estandares/rfc/rfc6585.txt) y
[*Denial of Service Cheat Sheet*](../estandares/owasp/Denial_of_Service.md) de OWASP.

- Los contadores viven en Redis, compartidos por todos los procesos.
- Todo 429 lleva `Retry-After`. Endurece RFC 6585, que lo deja opcional: el cliente sabe cuándo
  reintentar.
- El login admite 10 intentos por minuto por IP.

## Permisos

Estándar: [*Authorization Cheat Sheet*](../estandares/owasp/Authorization.md) de OWASP.

- Cada ruta declara con una dependencia de FastAPI el permiso que exige. El permiso queda a la
  vista en la ruta.

## Cabeceras

Estándares: [*HTTP Security Response Headers Cheat Sheet*](../estandares/owasp/HTTP_Headers.md),
[*Content Security Policy Cheat Sheet*](../estandares/owasp/Content_Security_Policy.md) y
[*REST Security Cheat Sheet*](../estandares/owasp/REST_Security.md) de OWASP, y
[CSP Level 3](../estandares/w3c/csp3.bs) de W3C.

- Caddy pone las cabeceras con la directiva `header`, para la web y para la API.
- La CSP de la web la genera SvelteKit con `kit.csp` en modo `hash`, sobre `default-src 'self'`.
  El script de arranque de SvelteKit va en línea y necesita su hash.

## Secretos

Estándar: [*Secrets Management Cheat Sheet*](../estandares/owasp/Secrets_Management.md) de OWASP.

- Los secretos viven solo en el `EnvironmentFile` de [despliegue.md](despliegue.md).

## Registro de eventos

Estándar: [*Logging Cheat Sheet*](../estandares/owasp/Logging.md) de OWASP.
