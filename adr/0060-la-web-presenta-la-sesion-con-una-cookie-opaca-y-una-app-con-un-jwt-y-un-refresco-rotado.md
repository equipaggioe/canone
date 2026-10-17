# ADR-0060 · La web presenta la sesión con una cookie opaca, y una app con un JWT y un refresco rotado

- **Estado:** Aceptada, salvo los puntos 8, 9 y 10, que siguen en propuesta
- **Fecha:** 2026-10-16
- **Alcance:** las secciones «Sesión» de
  [plataformas/transversal.md](../plataformas/transversal.md#sesión) y de
  [plataformas/fastapi.md](../plataformas/fastapi.md#sesión), y «WebSocket» de
  [plataformas/transversal.md](../plataformas/transversal.md#websocket); el servidor y sus clientes

## Contexto

Todos los clientes usaban un JWT de acceso y un token de refresco; en la web, el JWT vivía en el
JavaScript de la página y el refresco en una cookie. «Sesión» citaba enteros el *Session
Management*, el *Cross-Site Request Forgery Prevention*, el *HTML5 Security* y el *JSON Web Token
Cheat Sheet* de OWASP, y RFC 6265. Varias partes regulaban lo mismo, RFC 6265 no define
`SameSite`, y el *JSON Web Token Cheat Sheet* repetía a RFC 8725 con una fuente de orden mayor.

## Decisión

1. «Sesión» de `fastapi.md` cita RFC 7519, RFC 8725, la sección 4.14 de RFC 9700 y, en el nivel 1
   de ASVS 5.0, el capítulo V7 y las secciones V3.3 y V3.5. La de `transversal.md` no cita fuentes.
2. La web presenta su sesión con una cookie opaca; una app, con un JWT de acceso de 15 minutos y un
   token de refresco que rota. Las dos son filas de la misma tabla.
3. El JWT lleva el id de su sesión en `sid`, y el id de una sesión de una app que se cierra queda
   15 minutos en una lista de Valkey.
4. El token de refresco lleva el id de su sesión, firmado con HMAC. Un secreto que no es el vigente,
   ni el anterior mientras el vigente no se usó, es un reúso. Presentar el anterior reemplaza el
   vigente, y el anterior no cambia.
5. Un reúso borra la sesión, y el titular lo ve en la app. No cuenta como intento fallido.
   Reemplaza el punto 6 del
   [ADR-0044](0044-el-bloqueo-cuenta-en-una-ventana-y-el-titular-lo-ve-en-la-app.md).
6. Una app hace un solo refresco a la vez.
7. La web autentica el WebSocket con la cookie del handshake.
8. *(propuesta)* El token de la web tiene 256 bits y la fila guarda su SHA-256. Va en la cookie
   `__Host-session`, `HttpOnly` y `SameSite=Strict`, con 30 días de `Max-Age` que se renuevan con
   el último uso.
9. *(propuesta)* El último uso de una sesión de la web se actualiza a lo sumo cada 15 minutos.
10. *(propuesta)* Una petición con la cookie y un método que no es seguro responde 403 si su
    `Origin` falta o no es el del servidor.

## Consecuencias

- En la web ningún token llega a JavaScript. Un XSS todavía puede hacer peticiones mientras la
  página está abierta, pero no se lleva la sesión.
- Toda petición consulta estado: la de la web busca su sesión, y la de una app revisa la lista de
  Valkey.
- El servidor valida dos formas de presentar una sesión, sobre una sola tabla.
- Un ladrón que presenta el refresco anterior antes de que el dueño use el vigente no se detecta
  en ese momento, sino en el refresco siguiente del dueño.
- El *HTML5 Security Cheat Sheet* ya no lo cita ninguna página.

## Descartado

- **JWT y refresco también en la web.** El JWT queda en JavaScript: un XSS lo roba y pide otros al
  refresco, que recibe la cookie solo. RFC 10017, *OAuth 2.0 for Browser-Based Applications*
  (BCP 212), recomienda con fuerza el patrón en que el navegador no recibe ningún token.
- **Sesión opaca también en las apps.** Sin rotación, un token robado sirve hasta que la sesión
  vence, y nadie lo detecta.
- **DPoP en las apps desde el principio.** Ata el token a una clave del dispositivo, a cambio de que
  cada cliente firme cada petición. Se agrega cuando el riesgo del producto lo pida.
- **Revisar la revocación del JWT solo en algunas operaciones.** V7.4.1 pide que una sesión
  terminada no se pueda usar más.
- **Reconocer solo el refresco anterior, sin el id de sesión en el token.** Un ladrón que rota dos
  veces deja al dueño con un token que no se reconoce, y el robo no se detecta.
- **Que presentar el anterior lo reemplace por el vigente.** Si el dueño y un ladrón refrescan por
  turnos, cada uno presenta siempre el anterior del otro, y el reúso no llega nunca.
- **Invalidar el refresco anterior en el acto, como RFC 9700.** Una respuesta perdida en el teléfono
  cerraría la sesión del dueño y le avisaría de un robo.
- **Contar el reúso como intento fallido.** Reusar un token no es adivinar una credencial: el
  bloqueo no frena al ladrón, que ya tiene sesión, y un falso positivo acerca al dueño al bloqueo.
- **La cookie con el prefijo `__Secure-` y un `Path` acotado.** `__Host-` impide además que un
  subdominio plante otra cookie con su nombre.
