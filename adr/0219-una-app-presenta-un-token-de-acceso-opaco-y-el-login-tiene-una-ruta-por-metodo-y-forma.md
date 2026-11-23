# ADR-0219 · Una app presenta un token de acceso opaco, y el login tiene una ruta por método y forma

- **Estado:** Aceptada; los puntos 6 a 9 son propuesta
- **Fecha:** 2026-11-22
- **Alcance:** `plataformas/autenticacion.md`, `fastapi.md`, `stack.md`, `scripts/verificar.py` y
  `plantilla/server/`; el servidor y sus clientes

## Contexto

Al escribir la sesión en `plantilla/server/`, «Token de acceso» pedía un JWT con solo `sid` y
`exp`, validado con PyJWT, y una lista de sesiones cerradas en Valkey durante 15 minutos
([ADR-0060](0060-la-web-presenta-la-sesion-con-una-cookie-opaca-y-una-app-con-un-jwt-y-un-refresco-rotado.md),
punto 3). Sin la cuenta en el token, cada petición tenía que leer la fila de la sesión para saber de
quién era, y con esa lectura la validación sin estado y la lista no servían de nada. Casi toda ruta
lee la cuenta para sus permisos.

RFC 6749 §1.4 admite un token que es un identificador y uno que lleva su autorización firmada, y
ASVS 5.0 §7.2.2 acepta los dos. §7.4.1 dice que, con un token autocontenido, cerrar una sesión
necesita una medida aparte, como una lista de tokens terminados.

## Decisión

1. El token de acceso de una app es opaco: 256 bits aleatorios que vencen en 15 minutos, con su
   SHA-256 y su vencimiento en la fila de su sesión. Cada petición busca la sesión con su cuenta.
   Reemplaza el punto 3 del ADR-0060, y del [ADR-0133](0133-la-autenticacion-tiene-su-pagina-y-el-servidor-comprueba-aparte-lo-que-sus-bibliotecas-no-miran.md),
   lo del JWT de los puntos 3 y 7.
2. Refrescar reemplaza el token de acceso, y el token de acceso y el de la web no valen uno por el
   otro.
3. Cada método para entrar tiene dos rutas, `/api/auth/<método>/cookie` y
   `/api/auth/<método>/token`. El endpoint de token es `/api/auth/token`, y cerrar sesión,
   `/api/auth/logout`.
4. El login con contraseña identifica la cuenta con su correo o con su teléfono, uno solo.
5. Un login con un autenticador deshabilitado responde 403, de tipo `authenticator-disabled`, sin
   verificar la credencial.
6. *(propuesta)* El `Origin` del servidor es `https://` y el `Host` de la petición, y la comprobación
   es una dependencia del router de `/api`.
7. *(propuesta)* La clave del HMAC del token de refresco es `refresh_key` de `Settings`.
8. *(propuesta)* Un error que tiene que dejar escrito un cambio, como el fallo de una contraseña o el
   borrado de una sesión por reúso, se responde sin lanzarlo.
9. *(propuesta)* La purga diaria borra también las sesiones vencidas.

## Consecuencias

- Cerrar o borrar una sesión corta su token de acceso en el acto, sin un segundo almacén.
- Salen PyJWT, la clave del JWT, la comparación de su cabecera y la lista de Valkey.
- Cada petición de una app lee la base, como ya lo hacía la de la web.
- Con el token de acceso, el refresco recién hecho deja sin efecto el anterior: una petición en curso
  con el anterior recibe un 401 y la app refresca.
- El login suma dos rutas por método, cada una con un solo esquema en el OpenAPI.

## Descartado

- **JWT con `sid`, leyendo la fila en cada petición.** Tiene el costo del token opaco y además la
  clave y las comprobaciones del JWT, sin ganar nada.
- **JWT con `sub` y `sid`, y la lista de Valkey.** Evita leer la base en una ruta que no necesita la
  cuenta, a cambio de un segundo almacén; si su escritura falla después del commit, el token de una
  sesión cerrada vale hasta 15 minutos.
- **Una ruta por forma, con el método en el cuerpo.** El cuerpo es una unión con discriminador, que
  los cuatro generadores de clientes tienen que manejar, y los pasos previos del SMS y de la passkey
  siguen siendo rutas aparte.
- **401 al autenticador deshabilitado.** El titular no sabe por qué no entra. 423 es de WebDAV y
  trata de recursos bloqueados.
