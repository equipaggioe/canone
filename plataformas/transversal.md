# Transversal

Lo que tienen que cumplir juntas varias piezas. Lo que hace una sola pieza va en su página.

## Accesibilidad

Estándar: [WCAG 2.2](../fuentes/w3c/wcag22.html) de W3C.

- Todos los clientes cumplen el nivel AA, también las apps: una sola vara para todos los clientes.
- Cada objetivo táctil mide al menos 48 × 48: dp en las apps y px de CSS en la web. Endurece los 24
  px del criterio 2.5.8: la web también se usa en el teléfono.
- Los colores de `brand/tokens/` cumplen los criterios 1.4.3 y 1.4.11 en los dos modos: cada rol
  de texto contra los fondos en que va, y `outline` contra cada superficie.
- El texto grande también pide 4.5:1. Endurece el criterio 1.4.3, que le pide 3:1: un rol no sabe
  el tamaño del texto que lleva.

## Archivos

- Un archivo se sube como `multipart/form-data`, en su propia petición, nunca en base64 dentro de
  un JSON: base64 agranda el archivo un tercio y el servidor lee el JSON entero en memoria.

## Código por SMS

Estándar: [*Origin-bound one-time codes delivered via SMS*](../fuentes/wicg/sms-one-time-codes.bs)
de WICG.

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

Estándares: [RFC 9457](../fuentes/rfc/rfc9457.txt), [RFC 6901](../fuentes/rfc/rfc6901.txt) y la
sección 15 *Status Codes* de [RFC 9110](../fuentes/rfc/rfc9110.txt), salvo 15.5.1, 15.5.2, 15.5.4 y
15.5.5, que rigen en «Versión mínima de cliente», «Sesión» y
[fastapi.md](fastapi.md#permisos).

- `type` es `about:blank` o una URI `https://<dominio>/api/problems/<nombre>`, con el mismo dominio
  en todos los entornos: un mismo error tiene un solo `type`.
- Todo error que genera el servidor es problem+json, salvo los del endpoint de token de
  [Passkeys](#passkeys), que siguen RFC 6749.
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

Estándares: [RFC 3339](../fuentes/rfc/rfc3339.txt) y la sección 4.3 *Time and Date Handling* de
[I-JSON](../fuentes/rfc/rfc7493.txt), RFC 7493.

## Idiomas

Estándares: las secciones 2 *The Language Tag* y 4 *Formation and Processing of Language Tags*
de [RFC 5646](../fuentes/rfc/rfc5646.txt) y la sección 12.5.4 de
[RFC 9110](../fuentes/rfc/rfc9110.txt), *Accept-Language*.

- Todo producto se diseña multilingüe.
- El idioma base es `es`.
- La base guarda códigos, nunca textos traducidos, y cada cliente los traduce con su catálogo.
- El cliente muestra el texto de su catálogo para el `type` de un error, en vez de `detail`.
- El cliente manda en `Accept-Language` el idioma que eligió el usuario.

## Llamadas de voz y video

Estándar: la sección *RTCIceServer Dictionary* de [WebRTC](../fuentes/w3c/webrtc.html) de W3C.

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

Estándar: la sección 2.2 *Numbers* de [I-JSON](../fuentes/rfc/rfc7493.txt), RFC 7493.

- Un monto viaja como `{"amount": "10.50", "currency": "USD"}`: el monto en una cadena decimal, sin
  exponente, y la moneda en su código de la
  [lista de monedas](https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml) de ISO 4217.
- Un monto no se formatea sin su moneda.
- Cada cliente lo conserva como cadena o como el decimal de su lenguaje, nunca como `double`, y no
  calcula con él: los totales, impuestos y descuentos llegan calculados del servidor. Así ningún
  cliente necesita una biblioteca decimal.

## OpenAPI y clientes

Estándar: de [I-JSON](../fuentes/rfc/rfc7493.txt), RFC 7493, las secciones 2.1 *Encoding and
Characters*, 2.3 *Object Constraints*, 3 *Software Behavior*, 4.1 *Top-Level Constructs*, 4.2
*Must-Ignore Policy* y 4.4 *Binary Data*.

- La API habla en camelCase.
- Cada cliente genera del `openapi.json` del servidor los modelos del cable, en la convención de su
  lenguaje, y ninguno los escribe a mano: copiado a mano en varios lenguajes, el contrato diverge
  sin que nadie lo note.
- Los valores de un enum van en snake_case.
- El servidor responde 422 a un campo o un parámetro que no conoce. Contradice la *Must-Ignore
  Policy*, que pide ignorarlo: el cliente y el servidor salen del mismo contrato, y un campo
  desconocido es un error del cliente que tiene que verse.

## Paginación

Estándar: la [AIP-158](../fuentes/google-aip/aip-0158.md) de Google, *Pagination*.

- La respuesta es `{"items": [...], "nextPageToken": "..."}`, y el campo `nextPageToken` siempre
  está.
- `pageSize` vale 50 por defecto y 100 como máximo.
- Una lista que muestra números de página acepta `skip` y devuelve `totalSize`. Las demás no.
- Con `skip`, un `pageSize` mayor que 100 responde 422. Contradice AIP-158, que lo recorta: el
  cliente calcula `skip` con el tamaño que pidió, y un recorte se saltaría filas.
- Un `pageToken` ilegible o con otros parámetros que los de su petición responde 422 de tipo
  `validation`, con `parameter: "pageToken"`.

## Pagos

- El cliente cobra con el componente que la pasarela integra en él: la hoja de pago nativa en las
  apps y el formulario incrustado en la web, porque salir de la app para pagar se ve poco
  profesional. Si la pasarela no tiene uno para ese cliente, manda a su página.

## Passkeys

Estándares: las secciones 5.4 *Options for Credential Creation* y 5.5 *Options for Assertion
Generation* de [*Web Authentication Level 3*](../fuentes/w3c/webauthn-3.html) de W3C; de
[RFC 6749](../fuentes/rfc/rfc6749.txt), las secciones 2 *Client Registration*, 3 *Protocol
Endpoints*, 4.1 *Authorization Code Grant* y 5 *Issuing an Access Token*;
[RFC 7636](../fuentes/rfc/rfc7636.txt); [RFC 8252](../fuentes/rfc/rfc8252.txt), y
[RFC 9700](../fuentes/rfc/rfc9700.txt), salvo 2.2, 4.10 y 4.14, que rigen en
[fastapi.md](fastapi.md#sesión).

- Una app usa la passkey con la API de su sistema operativo cuando su framework la ofrece de forma
  oficial. Si no, la usa en el navegador del sistema, que le devuelve un código de autorización
  según RFC 8252.
- La app canjea el código en el endpoint de token con el formato de RFC 6749: la petición en
  `application/x-www-form-urlencoded`, y la respuesta y sus errores con los campos de su sección 5.
  Así la app usa AppAuth, que ya comprueba el `state` y la URI de retorno.
- El servidor solo acepta la URI `https` reclamada de la app. Contradice RFC 8252, que pide aceptar
  también un esquema propio y la interfaz de loopback: el único cliente nativo es la app del
  producto.
- El servidor no publica los metadatos de RFC 8414. Contradice RFC 9700, que los recomienda: el
  único cliente es la app del producto, que ya conoce sus rutas.
- Las secciones 9 *Native Applications* y 10 *Security Considerations* de RFC 6749 quedan sin
  efecto: las reemplazan RFC 8252 y RFC 9700.

## Push

Estándares: las secciones *Push subscription*, *Declarative push message*, *PushSubscriptionOptions
Interface*, *PushSubscription interface* y *PushEncryptionKeyName enumeration* de la
[*Push API*](../fuentes/w3c/push-api.html) de W3C, la sección 5.3 *Push Message Urgency* de
[RFC 8030](../fuentes/rfc/rfc8030.txt), y la sección 2 *Application Server Self-Identification*
de [RFC 8292](../fuentes/rfc/rfc8292.txt).

- Android y Flutter reciben push por FCM.
- Un mensaje de FCM lleva `notification` y, en `data`, la ruta que abre al tocarlo, salvo el de una
  llamada entrante.
- Un Web Push es un mensaje declarativo, con la ruta que abre en `navigate`.
- Una llamada entrante llega por un mensaje de FCM solo de datos y de prioridad alta.
- Un push vence cuando caduca lo que avisa; el de una llamada entrante, cuando deja de sonar.
- En la web, el push de una llamada entrante lleva `Urgency: high`.
- El FID y la suscripción web pertenecen a la sesión: se borran cuando la sesión se cierra o
  vence.
- La web recibe push con la Push API, sin el SDK de FCM: la CSP queda en `'self'`.

## Reintentos

Estándar: las secciones 9.2 *Common Method Properties* y 9.3 *Method Definitions* de
[RFC 9110](../fuentes/rfc/rfc9110.txt).

- Un recurso que el usuario crea desde un cliente se crea por `PUT /<recurso>/{id}`, con un uuid v4
  que genera el cliente. Si la respuesta se pierde, la petición repetida cae sobre la misma fila en
  vez de crear otra.
- El cliente reintenta solo una petición idempotente ante un fallo de red, un 502, un 503 o un 504,
  hasta 3 veces, con espera exponencial y jitter: un reinicio del servidor no le muestra un error al
  usuario.

## Sesión

Estándares: la sección *Access-Control-Allow-Origin* del
[*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md) de OWASP, y las
secciones 3.3 *Connections, Clients, and Servers*, 11 *HTTP Authentication* y 15.5.2 *401
Unauthorized* de [RFC 9110](../fuentes/rfc/rfc9110.txt).

- La API se sirve en el mismo origen que la web, bajo `/api`. No hace falta CORS, y la cookie de
  sesión es de primera parte.
- La web presenta su sesión con una cookie, y una app, con un token de acceso que renueva con un
  token de refresco. En la web, ningún token queda al alcance de un script.
- En una app, el token de acceso vive solo en memoria, y el de refresco, en el almacenamiento seguro
  del sistema: ningún almacenamiento guarda un token que da acceso directo a la API.
- Una app hace un solo refresco a la vez, y las peticiones que reciben un 401 mientras tanto lo
  esperan. Con la rotación, dos refrescos simultáneos presentan tokens ya rotados.
- Ante un 401, una app refresca la sesión una sola vez y reintenta una sola vez.
- Un 401 a un token en `Authorization` lleva `WWW-Authenticate: Bearer`, y uno a la cookie de la web
  no lleva desafío. Contradice RFC 9110, que lo pide en todo 401: la cookie no es un esquema de
  autenticación de HTTP.

## Tema

> **En desarrollo** (anotado el 2026-10-17): ningún producto la usa todavía, y `verificar.py` no la
> comprueba. Esta sección, el «Tema» de cada cliente, el
> [ADR-0062](../adr/0062-los-colores-de-un-producto-salen-de-brand-tokens-en-dtcg-y-un-generador-arma-el-esquema-de-cada-cliente.md),
> `scripts/tokens.py` y `brand/tokens/` de la plantilla se revisan y se desarrollan como cualquier
> otra parte de canone.

Estándares: de DTCG 2025.10, el [formato](../fuentes/dtcg/format.html), el
[módulo de color](../fuentes/dtcg/color.html) y el [resolver](../fuentes/dtcg/resolver.html),
enteros.

- Los colores de un producto van en `brand/tokens/`: `colors.resolver.json` y los `.tokens.json`
  que cita. Son la única fuente de los colores de todos sus clientes.
- `colors.resolver.json` tiene un solo modificador, `theme`, con los contextos `light` y `dark`.
- Los tokens tienen dos niveles: el grupo `palette` guarda los colores, en sRGB y opacos, y el
  grupo `color` asigna cada rol a un color de `palette` con un alias. Cambiar un color de la marca
  toca un solo token.
- Los roles son las 46 propiedades de color no obsoletas del `ColorScheme` de Flutter, y cada modo
  las asigna todas. Compose, Flutter y Flet arman su esquema con esos roles, y uno sin asignar
  tomaría en silencio el color por defecto del framework.
- `scripts/tokens.py` genera en cada cliente su esquema claro y su esquema oscuro, ya armados.
  Implementa del formato las secciones 5.1 *Name and value*, 5.2.1 *Description*, 5.2.2 *Type*, 6.1
  *Group Structure*, 7.1.1 *Curly Brace Syntax*, 7.2.2 *Chained References* y 7.2.3 *Circular
  References*; del módulo de color, 4.1 *Format* y 4.2.1 *sRGB*, y del resolver, 4.1 *Root level
  properties*, 4.2 *Reference objects*, 6.1 *Input validation*, 6.2 *Ordering* y 6.3 *Aliases*.
  Falla ante lo demás, que queda sin efecto porque un producto solo usa colores sRGB opacos en dos
  modos, y ante un color que no cumpla el contraste de [Accesibilidad](#accesibilidad).
- Lo generado se commitea: un cliente compila sin correr el generador.
- Cada cliente sigue el modo claro u oscuro del sistema.

Plantilla: `scripts/tokens.py` es canónico y se copia sin editar; `brand/tokens/` es un punto de
partida.

## Versión mínima de cliente

Estándar: las secciones 10.1.5 *User-Agent* y 15.5.1 *400 Bad Request* de
[RFC 9110](../fuentes/rfc/rfc9110.txt).

- Cada cliente instalable manda `User-Agent: <pieza>/<versión>`. La versión
  son tres enteros, `MAJOR.MINOR.PATCH`, y se compara número por número.
- Una versión menor que la mínima de su pieza recibe un 400 de tipo
  `https://<dominio>/api/problems/client-outdated`, y el cliente pide actualizar la app. Lo mismo
  recibe una petición con un token de app sin un `User-Agent` de pieza: el olvido falla en
  desarrollo.
- Las dos cosas van desde la primera versión que se publica: a una app instalada sin ellas nunca
  se le puede obligar a actualizar.

## WebSocket

Estándar: del [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de
OWASP, las secciones *Always Use WSS* y *Session Management*, sin su párrafo de `SameSite`, que
rige en [fastapi.md](fastapi.md#sesión).

- La web se autentica con la cookie de sesión del handshake, y una app, con
  `Authorization: Bearer` en el handshake, como en REST.
- Una sesión que no vale o un token vencido cierran la conexión con 4401, del rango privado de
  los [códigos de cierre](https://www.rfc-editor.org/rfc/rfc6455.txt) de RFC 6455, en su sección 7.4: un código
  propio separa la sesión de cualquier otro cierre. En el handshake, el
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
