# Transversal

Lo que tienen que cumplir juntas varias piezas. Lo que hace una sola pieza va en su página.

## Accesibilidad

Estándar: los criterios de éxito de nivel A y AA de [WCAG 2.2](../fuentes/w3c/wcag22.html) de W3C.

- Todos los clientes cumplen el nivel AA, también las apps. Es la vara que nombra la guía de
  Flutter, y una sola para todos los clientes.
- Cada objetivo táctil mide al menos 48 × 48: dp en las apps y px de CSS en la web. Endurece los 24
  px del criterio 2.5.8, porque la web también se usa en el teléfono, y es la medida que Android
  recomienda.
- Los colores de `brand/tokens/` cumplen los criterios 1.4.3 y 1.4.11 en los dos modos: cada rol
  de texto contra los fondos en que va, con 4.5:1, y `outline` contra cada superficie, con 3:1. El
  contraste no se elige a ojo.
- El texto grande también pide 4.5:1. Endurece el criterio 1.4.3, que le pide 3:1: un rol no sabe
  el tamaño del texto que lleva.

## Archivos

Estándar: [RFC 7578](../fuentes/rfc/rfc7578.txt).

- Un archivo se sube en su propia petición, nunca en base64 dentro de un JSON: base64 agranda el
  archivo un tercio y el servidor lee el JSON entero en memoria.

## Código por SMS

Estándar: la sección *Message format* de
[*Origin-bound one-time codes delivered via SMS*](../fuentes/wicg/sms-one-time-codes.bs) de WICG.

- El código tiene 6 dígitos.
- El número viaja y se guarda con `+`, el código de país y solo dígitos: escrito de otra forma, el
  mismo número crearía otra cuenta.
- Si un cliente es una app de Android, su hash va en la penúltima línea del SMS: el formato de
  WICG reserva el final de la última para sintaxis futura.

## Contraseñas

Estándar: de la sección 3.1.1.2 *Password Verifiers* de
[NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt), los párrafos sobre la guía para elegir una
contraseña, los gestores de contraseñas y mostrar la contraseña mientras se escribe.

## Errores

Estándares: [RFC 9457](../fuentes/rfc/rfc9457.txt) y [RFC 6901](../fuentes/rfc/rfc6901.txt).

- `type` es `about:blank` o una URI `https://<dominio>/api/problems/<nombre>`, con el mismo dominio
  en todos los entornos: un mismo error tiene un solo `type`.
- Todo error que genera el servidor es problem+json.
- El cliente toma una respuesta de error sin problem+json, o con un `type` que su catálogo no
  conoce, como de tipo `about:blank`, con su `status`, y su catálogo tiene un texto por `status`
  para ese tipo.
- Todo problem+json lleva `traceId`, el trace-id de la petición.
- Todo problem+json lleva `status`, y ninguno lleva `instance`: `traceId` ya identifica la
  ocurrencia.
- Ante un 5xx o un `type` que su catálogo no conoce, el cliente muestra el `traceId` junto al
  texto, para que el usuario lo copie.
- Un error de validación es de tipo `https://<dominio>/api/problems/validation`, con la extensión
  `errors`: una lista de `{detail, pointer}`, o de `{detail, parameter}` para un parámetro que no
  viene en el cuerpo.
- `pointer` usa la representación de cadena de RFC 6901. La de fragmento suma la codificación de URI.
- Cada cliente traduce el sobre a un error tipado con los mismos campos.

## Fechas

Estándar: [RFC 3339](../fuentes/rfc/rfc3339.txt).

## Idiomas

Estándares: las secciones 2.1 *Syntax* y 4.1 *Choice of Language Tag* de
[RFC 5646](../fuentes/rfc/rfc5646.txt) y la sección 12.5.4 de [RFC 9110](../fuentes/rfc/rfc9110.txt),
*Accept-Language*.

- Todo producto se diseña multilingüe.
- El idioma base es `es`.
- La base guarda códigos, nunca textos traducidos, y cada cliente los traduce con su catálogo.
- El cliente muestra el texto de su catálogo para el `type` de un error, en vez de `detail`.
- El cliente manda en `Accept-Language` el idioma que eligió el usuario. El servidor lo guarda con
  el FID de cada instalación de la app, y en el usuario el último elegido, para el correo.

## Llamadas de voz y video

Estándares: las secciones 4.1.10.2 *Rollback* y 5.7 *Processing a Rollback* de
[RFC 9429](../fuentes/rfc/rfc9429.txt), JSEP, y la sección *RTCIceServer Dictionary* de
[WebRTC](../fuentes/w3c/webrtc.html) de W3C.

- La señalización va por el WebSocket de la app.
- coturn usa credenciales temporales (`use-auth-secret`), que el servidor entrega por la API.
- El cliente pide una credencial al iniciar o al atender cada llamada, y antes de cada reinicio de
  ICE: con una credencial vencida, coturn no abre un relay nuevo.
- Mientras suena, el servidor guarda la llamada con su oferta, y quien la recibe la pide por REST al
  conectarse o al despertar por el push. El resto de la señalización no se guarda.
- Cualquiera de los dos puede mandar una oferta. Si dos se cruzan, el que atiende descarta la suya
  con *rollback* y acepta la del que llama.

## Mapas

Estándar: la [guía de atribución](../fuentes/osm/attribution-guidelines.md) de OpenStreetMap.

- Las teselas son raster, con URL `{z}/{x}/{y}`.
- Las teselas son las de `tile.openstreetmap.org`.
- La URL de las teselas y su atribución las entrega el servidor en su configuración pública:
  cambiar de proveedor no exige publicar otra versión de las apps.
- Los clientes buscan direcciones en el servidor, que consulta a Nominatim: su límite es por
  aplicación, y solo el servidor ve el total.

## Montos

Estándares: la sección 2.2 de [I-JSON](../fuentes/rfc/rfc7493.txt), RFC 7493, *Numbers*, y la
[lista de monedas](../fuentes/iso/iso-4217-list-one.xml) de ISO 4217.

- Un monto viaja como `{"amount": "10.50", "currency": "USD"}`: el monto en una cadena decimal, sin
  exponente, y la moneda en su código ISO 4217. Un monto no se formatea sin su moneda.
- Cada cliente lo conserva como cadena o como el decimal de su lenguaje, nunca como `double`, y no
  calcula con él: los totales, impuestos y descuentos llegan calculados del servidor. Así ningún
  cliente necesita una biblioteca decimal.

## OpenAPI y clientes

- La API habla en camelCase. Cada cliente genera del `openapi.json` del servidor los modelos del
  cable, en la convención de su lenguaje, y ninguno los escribe a mano. Copiado a mano en varios
  lenguajes, el contrato diverge sin que nadie lo note.
- Los valores de un enum van en snake_case.

## Paginación

Estándar: la [AIP-158](../fuentes/google-aip/aip-0158.md) de Google, *Pagination*.

- La respuesta es `{"items": [...], "nextPageToken": "..."}`, y la última página lleva
  `"nextPageToken": ""`. El campo siempre está.
- `pageSize` vale 50 por defecto y 100 como máximo.
- Una lista que muestra números de página acepta `skip` y devuelve `totalSize`. Las demás no.
- Con `skip`, un `pageSize` mayor que 100 responde 422. Contradice AIP-158, que lo recorta: el
  cliente calcula `skip` con el tamaño que pidió, y un recorte se saltaría filas.
- Un `pageToken` ilegible o con otros parámetros que los de su petición responde 422 de tipo
  `validation`, con `parameter: "pageToken"`.

## Pagos

Estándar: [*Secure Integration of Third-Party Payment Gateways Cheat Sheet*](../fuentes/owasp/Third_Party_Payment_Gateway_Integration.md)
de OWASP.

- El cliente cobra con el componente que la pasarela integra en él: la hoja de pago nativa en las
  apps y el formulario incrustado en la web. Si la pasarela no tiene uno para ese cliente, manda a
  su página. Contradice el paso 3 de OWASP: salir de la app para pagar se ve poco profesional.

## Passkeys

Estándares: las secciones 5.4 *Options for Credential Creation*, 5.5 *Options for Assertion
Generation* y 7 *WebAuthn Relying Party Operations* de
[*Web Authentication Level 3*](../fuentes/w3c/webauthn-3.html) de W3C, la sección
4.1 *Authorization Code Grant* de [RFC 6749](../fuentes/rfc/rfc6749.txt),
[RFC 7636](../fuentes/rfc/rfc7636.txt), [RFC 8252](../fuentes/rfc/rfc8252.txt) y la sección
2.1 *Protecting Redirect-Based Flows* de [RFC 9700](../fuentes/rfc/rfc9700.txt).

- Una app usa la passkey con la API de su sistema operativo cuando su framework la ofrece de forma
  oficial. Si no, la usa en el navegador del sistema, que le devuelve un código de autorización
  según RFC 8252.

## Push

Estándares: las secciones *Push subscription*, *Declarative push message*, *PushSubscriptionOptions
Interface*, *PushSubscription interface* y *PushEncryptionKeyName enumeration* de la
[*Push API*](../fuentes/w3c/push-api.html) de W3C y [RFC 8292](../fuentes/rfc/rfc8292.txt).

- Android y Flutter reciben push por FCM.
- Un mensaje de FCM lleva `notification` y, en `data`, la ruta que abre al tocarlo, salvo el de una
  llamada entrante.
- Un Web Push es un mensaje declarativo, con la ruta que abre en `navigate`.
- Una llamada entrante llega por un mensaje de FCM solo de datos y de prioridad alta.
- Un push vence cuando caduca lo que avisa; el de una llamada entrante, cuando deja de sonar. En la
  web, el de una llamada lleva `Urgency: high`.
- El FID y la suscripción web pertenecen a la sesión: se borran cuando la sesión se cierra o
  vence.
- La web recibe push con la Push API, sin el SDK de FCM: la CSP queda en `'self'`.

## Reintentos

Estándar: las secciones 9.2.2 *Idempotent Methods* y 9.3.4 *PUT* de
[RFC 9110](../fuentes/rfc/rfc9110.txt).

- Un recurso que el usuario crea desde un cliente se crea por `PUT /<recurso>/{id}`, con un uuid v4
  que genera el cliente. Si la respuesta se pierde, la petición repetida cae sobre la misma fila en
  vez de crear otra.
- El cliente reintenta solo una petición idempotente ante un fallo de red, un 502, un 503 o un 504,
  hasta 3 veces, con espera exponencial y jitter: un reinicio del servidor no le muestra un error al
  usuario.

## Sesión

- La API se sirve en el mismo origen que la web, bajo `/api`. No hace falta CORS, y la cookie de
  sesión es de primera parte.
- La web presenta su sesión con una cookie, y una app, con un token de acceso que renueva con un
  token de refresco. En la web, ningún token queda al alcance de un script.
- En una app, el token de acceso vive solo en memoria, y el de refresco, en el almacenamiento seguro
  del sistema: ningún almacenamiento guarda un token que da acceso directo a la API.
- Una app hace un solo refresco a la vez, y las peticiones que reciben un 401 mientras tanto lo
  esperan. Con la rotación, dos refrescos simultáneos presentan tokens ya rotados.
- Ante un 401, una app refresca la sesión una sola vez y reintenta una sola vez. Nunca un bucle
  silencioso.

## Tema

> **Por revisar** (anotado el 2026-10-17): no se aplica todavía. Esta sección, el «Tema» de cada
> cliente, el [ADR-0062](../adr/0062-los-colores-de-un-producto-salen-de-brand-tokens-en-dtcg-y-un-generador-arma-el-esquema-de-cada-cliente.md),
> `scripts/tokens.py` y `brand/tokens/` de la plantilla están en revisión. La comprobación de
> `verificar.py` está desactivada.

Estándares: de DTCG 2025.10, las secciones 5 *Design token*, 6.1 *Group Structure*, 7.1.1 *Curly
Brace Syntax*, 7.2 *Reference Resolution* y 8.1 *Color* del [formato](../fuentes/dtcg/format.html),
las secciones 4.1 *Format* y 4.2.1 *sRGB* del [módulo de color](../fuentes/dtcg/color.html), y las
secciones 4 *Syntax* y 6 *Resolution logic* del [resolver](../fuentes/dtcg/resolver.html).

- Los colores de un producto van en `brand/tokens/`: `colors.resolver.json` y los `.tokens.json`
  que cita. Son la única fuente de los colores de todos sus clientes.
- `colors.resolver.json` tiene un solo modificador, `theme`, con los contextos `light` y `dark`.
- Los tokens tienen dos niveles: el grupo `palette` guarda los colores, en sRGB y opacos, y el
  grupo `color` asigna cada rol a un color de `palette` con un alias. Cambiar un color de la marca
  toca un solo token.
- Los roles son las 46 propiedades de color no obsoletas del `ColorScheme` de Flutter, y cada modo
  las asigna todas. Compose, Flutter y Flet arman su esquema con esos roles, y uno sin asignar
  tomaría en silencio el color por defecto del framework.
- `scripts/tokens.py` genera en cada cliente su esquema claro y su esquema oscuro, ya armados. Falla
  ante lo que esté fuera de este subconjunto de DTCG o no cumpla el contraste de
  [Accesibilidad](#accesibilidad).
- Lo generado se commitea: un cliente compila sin correr el generador.
- Cada cliente sigue el modo claro u oscuro del sistema.
- Los tamaños van en el módulo de tema de cada cliente, sin tamaños literales fuera de él. Las
  unidades y las guías de cada plataforma son distintas.

Plantilla: `scripts/tokens.py` es canónico y se copia sin editar; `brand/tokens/` es un punto de
partida.

## Versión mínima de cliente

Estándar: las secciones 10.1.5 *User-Agent* y 15.5.1 *400 Bad Request* de
[RFC 9110](../fuentes/rfc/rfc9110.txt).

- Cada cliente instalable manda `User-Agent: <pieza>/<versión>`, como `mobile/1.4.0`. La versión
  son tres enteros, `MAJOR.MINOR.PATCH`, y se compara número por número.
- Una versión menor que la mínima de su pieza recibe un 400 de tipo
  `https://<dominio>/api/problems/client-outdated`, y el cliente pide actualizar la app. Lo mismo
  recibe una petición con un token de app sin un `User-Agent` de pieza: el olvido falla en
  desarrollo.
- Las dos cosas van desde la primera versión que se publica: a una app instalada sin ellas nunca
  se le puede obligar a actualizar.

## WebSocket

Estándares: la sección 7.4 *Status Codes* de [RFC 6455](../fuentes/rfc/rfc6455.txt) y, del
[*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP, las
secciones *Always Use WSS* y *Session Management*, sin su párrafo de `SameSite`.

- La web se autentica con la cookie de sesión del handshake, y una app, con
  `Authorization: Bearer` en el handshake, como en REST.
- Una sesión que no vale o un token vencido cierran la conexión con 4401, del rango privado de
  RFC 6455: un código propio separa la sesión de cualquier otro cierre. En el handshake, el
  servidor acepta la conexión para cerrarla: un rechazo con 401 Uvicorn lo registra como error, y
  uno con 403 no dice que el problema es la sesión.
- Ante un 4401, una app refresca la sesión una sola vez y reconecta, y la web vuelve al inicio de
  sesión.
- Al refrescar la sesión, una app manda el token nuevo por la misma conexión.
- Borrar una sesión cierra sus conexiones en el momento. Deja sin efecto la revalidación periódica
  de *Session Management*: el cierre llega con el borrado, no en la siguiente revisión.
- Los mensajes son JSON `{type, data}`, en camelCase como la API.
- Al perder la conexión, el cliente reconecta con espera exponencial y jitter, con hasta 30
  segundos entre intentos, y vuelve a pedir el estado por REST. Lo que se envió mientras estaba
  desconectado no se repite.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Contraste de `brand/tokens/` | `scripts/tokens.py`, que corre `verificar.py` |
| DTCG: el subconjunto de `brand/tokens/` | `scripts/tokens.py`, que corre `verificar.py` |
| Lo generado, al día con `brand/tokens/` | `verificar.py` |
| Todo error del servidor en problem+json | `test_unknown_route_is_a_problem` y `test_validation_error_points_to_the_field`, del servidor |
| RFC 9457: la URI de cada tipo sirve su documentación | `test_problem_types_are_documented`, del servidor |
| El `traceId` en todo problem+json | `test_unknown_route_is_a_problem`, del servidor |
