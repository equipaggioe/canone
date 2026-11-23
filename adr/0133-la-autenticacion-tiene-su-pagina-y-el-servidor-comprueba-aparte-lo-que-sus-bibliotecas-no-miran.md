# ADR-0133 · La autenticación tiene su página, y el servidor comprueba aparte lo que sus bibliotecas no miran

- **Estado:** Aceptada; el punto 6 es propuesta. Los puntos 11 y 12, en el código por SMS, los reemplaza el [ADR-0185](0185-una-cuenta-entra-con-passkey-o-contrasena-y-cada-repositorio-elige-cuales-ofrece.md), y lo del JWT y PyJWT de los puntos 3 y 7, el [ADR-0219](0219-una-app-presenta-un-token-de-acceso-opaco-y-el-login-tiene-una-ruta-por-metodo-y-forma.md)
- **Fecha:** 2026-11-09
- **Alcance:** `plataformas/autenticacion.md`, `fastapi.md`, `transversal.md`, `flutter.md`, `qt.md`,
  `flet.md`, `plataformas/README.md` y `scripts/verificar.py`; el servidor y sus clientes

## Contexto

La autenticación estaba repartida entre «Autenticación», «Código por SMS», «Contraseñas»,
«Passkeys» y «Sesión» de `fastapi.md`, y «Contraseñas», «Passkeys» y «Sesión» de `transversal.md`,
con párrafos `Estándar:` que adoptaban partes de NIST SP 800-63B-4, OAuth, ASVS y WebAuthn sin
escribirlas. El [ADR-0129](0129-la-pagina-escribe-cada-convencion-que-rige-y-la-adoptada-lleva-su-origen.md)
pide reescribirlas, y empieza por esta página.

Se comprobó con un autenticador de software qué hacen `webauthn` 3.0.1 y PyJWT 2.15.1. `webauthn`
rechaza un `type`, un challenge, un `origin` o un `rpIdHash` que no son los esperados, la falta del
bit UP o del UV exigido, BS sin BE, un `alg` fuera de la lista, una firma inválida y un `signCount`
que no sube. Acepta un credential ID de 1024 bytes, `crossOrigin`, `topOrigin`, cualquier extensión
en el `authData` o en `clientExtensionResults`, la atestación `packed` propia y un BE distinto del
guardado. PyJWT, con `algorithms=["HS256"]` y `exp` y `sid` obligatorios, rechaza `none`, HS512,
una firma inválida, `exp` vencido y la falta de `exp` o de `sid`; acepta cualquier `typ` y
cabeceras con `kid` o `jku`.

AppAuth solo existe para Android, iOS y JavaScript. En Qt, `QOAuthUriSchemeReplyHandler` recibe una
URI `https` solo en Android, iOS y macOS, y `QOAuthHttpServerReplyHandler` recibe la vuelta por
loopback. Flet no tiene una API oficial de passkeys, y su `page.login()` abre en el teléfono «un
navegador dentro de la app», que puede ser un web-view.

## Decisión

1. La autenticación va en `plataformas/autenticacion.md`, que junta esas secciones. `fastapi.md` y
   `transversal.md` dejan solo el enlace, y lo propio de cada cliente sigue en su página.
2. El RP ID es `<dominio>`.
3. El servidor verifica las passkeys con `webauthn` y el JWT con PyJWT, y comprueba aparte lo que
   ellas no miran: el largo del credential ID, `crossOrigin`, `topOrigin`, las extensiones, la
   atestación que se acepta, que BE sea el guardado y la cabecera entera del JWT.
4. `rp.name` es el RP ID; `user.name`, el correo o el teléfono, y `user.displayName`, el que elige el
   titular. Un `signCount` que no sube hace fallar el login y avisa al titular.
5. El código de autorización vive en Valkey; el endpoint de autorización pide la passkey aunque el
   navegador tenga una sesión abierta; los endpoints no usan `scope`, y el refresco va al endpoint de
   token según RFC 6749 §6, con sus errores.
6. *(propuesta)* El servidor no pide extensiones. Un `clientExtensionResults` no vacío hace fallar
   la ceremonia; en el registro, el `authData` acepta solo `credProtect`, que Chrome pide por su
   cuenta, y en el login, ninguna. El registro acepta la atestación `none` y la propia.
7. `autenticacion.md` fija en «Proyecto» las versiones de pwdlib, phonenumbers, `webauthn` y PyJWT,
   `flutter.md` la de flutter_appauth, y `verificar.py` las comprueba.
8. En cada sección de una página van primero las convenciones propias, y después las adoptadas.
9. `verificar.py` encuentra el número de una sección también en un título de Markdown o en una
   celda, como los requisitos de ASVS.
10. La app de Flutter hace el código de autorización con flutter_appauth, y la de Qt, con
    QtNetworkAuth y una URI de retorno de loopback, `http://127.0.0.1:{puerto}/<ruta>`, que el
    servidor acepta con cualquier puerto.
11. Una app de Flet no usa passkeys: entra con contraseña o con código por SMS.
12. Una app que entra con contraseña, con código por SMS o con la passkey de su sistema recibe la
    misma respuesta que el canje del código.
13. Lo de una función que no se ofrece no se escribe: la página tampoco lleva la línea que lo dice.
    Reemplaza el punto 4 del ADR-0129 en esa línea.

Reemplaza también el punto 1 del [ADR-0054](0054-las-passkeys-son-un-contrato-de-transversal-y-una-app-usa-la-api-de-su-sistema.md)
y el punto 1 del [ADR-0060](0060-la-web-presenta-la-sesion-con-una-cookie-opaca-y-una-app-con-un-jwt-y-un-refresco-rotado.md).

## Consecuencias

- Una passkey sirve en `app.<dominio>` y en `panel.<dominio>`.
- El servidor acepta una URI de retorno `http`, solo en `127.0.0.1` y para la app de escritorio.
- Sin confirmar: que QtNetworkAuth mande y compruebe el `state`.
- Una app de Flet no tiene passkeys hasta que se pruebe `page.login()` en un APK.
- Un refresco inválido responde `invalid_grant`, un 400, y no 401.
- Un error del cliente que agrega una extensión falla a la vista. Si un navegador agrega por su
  cuenta otra extensión que `credProtect`, el registro falla hasta sumarla.
- Sin confirmar: que un navegador real no llene `clientExtensionResults` sin que se le pida, y que
  ninguna llave devuelva `credProtect` en el login. Se probó con un autenticador de software, no con
  un navegador ni una llave.

## Descartado

- **Ignorar las extensiones que no se pidieron:** oculta el error del cliente que agrega una.
- **Rechazar toda extensión que no se pidió:** haría fallar el registro con una llave en Chrome.
- **Solo la URI `https` reclamada:** una app de Qt no la puede reclamar en Windows ni en Linux.
- **`page.login()` de Flet para las passkeys:** puede abrir un web-view, que RFC 8252 prohíbe.
- **Exigir la atestación `none`:** el navegador deja pasar la propia aunque se pida `none`.
- **Escribir la verificación de WebAuthn y del JWT a mano:** CBOR, COSE y tres algoritmos de firma
  dan más código propio que comprobar, y las bibliotecas ya cubren la mayoría de los pasos.
- **Reemplazar los pasos de §7.1, §7.2 y RFC 7519 §7.2 por una convención que nombre la biblioteca:**
  ninguna de las dos los cubre enteros.
