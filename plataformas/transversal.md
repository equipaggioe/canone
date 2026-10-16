# Transversal

Lo que tienen que cumplir juntas varias piezas. Lo que hace una sola pieza va en su página.

## Accesibilidad

Estándar: [WCAG 2.2](../fuentes/w3c/wcag22.html) de W3C.

- Todos los clientes cumplen el nivel AA, también las apps. Es la vara que nombra la guía de
  Flutter, y una sola para todos los clientes.
- Cada objetivo táctil mide al menos 48 × 48: dp en las apps y px de CSS en la web. Endurece los 24
  px del criterio 2.5.8, porque la web también se usa en el teléfono, y es la medida que Android
  recomienda.
- El módulo de tokens de diseño cumple los criterios 1.4.3 y 1.4.11 en el tema claro y en el
  oscuro, y una prueba de cada cliente calcula el contraste de cada par de color de texto y de
  fondo. El contraste no se elige a ojo.

## Archivos

Estándar: [RFC 7578](../fuentes/rfc/rfc7578.txt).

- Un archivo se sube en su propia petición, nunca en base64 dentro de un JSON: base64 agranda el
  archivo un tercio y el servidor lee el JSON entero en memoria.

## Código por SMS

Estándares: la sección *Message format* de
[*Origin-bound one-time codes delivered via SMS*](../fuentes/wicg/sms-one-time-codes.bs) de WICG
y la sección *Construct a verification message* de
[*Perform SMS Verification on a Server*](../fuentes/android/sms-retriever-verify.md) de Google.

- El código tiene 6 dígitos.
- El número viaja y se guarda con `+`, el código de país y solo dígitos: escrito de otra forma, el
  mismo número crearía otra cuenta.
- Si un cliente es una app de Android, su hash va en la penúltima línea del SMS: el formato de
  WICG reserva el final de la última para sintaxis futura.

## Errores

Estándares: [RFC 9457](../fuentes/rfc/rfc9457.txt) y [RFC 6901](../fuentes/rfc/rfc6901.txt).

- `type` es `about:blank` o una URI `https://<dominio>/api/problems/<nombre>`, con el mismo dominio
  en todos los entornos: un mismo error tiene un solo `type`.
- Todo error que genera el servidor es problem+json.
- El cliente toma una respuesta de error sin problem+json, o con un `type` que su catálogo no
  conoce, como de tipo `about:blank`, con su `status`, y su catálogo tiene un texto por `status`
  para ese tipo.
- Todo problem+json lleva `status`, y ninguno lleva `instance`: `traceId` ya identifica la
  ocurrencia.
- Un error de validación es de tipo `https://<dominio>/api/problems/validation`, con la extensión
  `errors`: una lista de `{detail, pointer}`, o de `{detail, parameter}` para un parámetro que no
  viene en el cuerpo.
- `pointer` usa la representación de cadena de RFC 6901. La de fragmento suma la codificación de URI.
- Cada cliente traduce el sobre a un error tipado con los mismos campos.

## Fechas

Estándar: [RFC 3339](../fuentes/rfc/rfc3339.txt).

## Idiomas

Estándares: [RFC 5646](../fuentes/rfc/rfc5646.txt) y la sección 12.5.4 de
[RFC 9110](../fuentes/rfc/rfc9110.txt), *Accept-Language*.

- Todo producto se diseña multilingüe.
- El idioma base es `es`.
- La base guarda códigos, nunca textos traducidos, y cada cliente los traduce con su catálogo.
- El cliente muestra el texto de su catálogo para el `type` de un error, en vez de `detail`.
- El cliente manda en `Accept-Language` el idioma que eligió el usuario. El servidor lo guarda con
  el token de push de cada dispositivo, y en el usuario el último elegido, para el correo.

## Llamadas de voz y video

Estándares: [RFC 9429](../fuentes/rfc/rfc9429.txt), JSEP, y la sección *RTCIceServer Dictionary*
de [WebRTC](../fuentes/w3c/webrtc.html) de W3C.

- La señalización va por el WebSocket de la app.
- coturn usa credenciales temporales (`use-auth-secret`), que el servidor entrega por la API.
- El cliente pide una credencial al iniciar o al atender cada llamada, y antes de cada reinicio de
  ICE: con una credencial vencida, coturn no abre un relay nuevo.
- Mientras suena, el servidor guarda la llamada con su oferta, y quien la recibe la pide por REST al
  conectarse o al despertar por el push. El resto de la señalización no se guarda.
- Cualquiera de los dos puede mandar una oferta. Si dos se cruzan, el que atiende descarta la suya
  con *rollback* y acepta la del que llama.

## Mapas

Estándares: la [política de uso de teselas](../fuentes/osm/tile-usage-policy.md), la
[política de uso de Nominatim](../fuentes/osm/nominatim-usage-policy.md) y la
[guía de atribución](../fuentes/osm/attribution-guidelines.md) de OpenStreetMap.

- Las teselas son raster, con URL `{z}/{x}/{y}`.
- Mientras el uso quepa en la política, las teselas son las de `tile.openstreetmap.org`.
- La URL de las teselas y su atribución las entrega el servidor en su configuración pública.
  Endurece la recomendación de la política: cambiar de proveedor no exige publicar otra versión de
  las apps.
- Los clientes buscan direcciones en el servidor, que consulta a Nominatim. El límite de la
  política es por aplicación, y solo el servidor ve el total.

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

Estándares: [*Web Authentication Level 3*](../fuentes/w3c/webauthn-3.bs) de W3C, la sección
4.1 *Authorization Code Grant* de [RFC 6749](../fuentes/rfc/rfc6749.txt),
[RFC 7636](../fuentes/rfc/rfc7636.txt), [RFC 8252](../fuentes/rfc/rfc8252.txt) y la sección
2.1 *Protecting Redirect-Based Flows* de [RFC 9700](../fuentes/rfc/rfc9700.txt).

- Una app usa la passkey con la API de su sistema operativo cuando su framework la ofrece de forma
  oficial. Si no, la usa en el navegador del sistema, que le devuelve un código de autorización
  según RFC 8252.

## Push

Estándares: [*Firebase Cloud Messaging message types*](../fuentes/firebase/set-message-type.md),
[*Best practices for FCM registration management*](../fuentes/firebase/manage-tokens.md),
[*Set and manage Android message priority*](../fuentes/firebase/android-message-priority.md), las
secciones *Push subscription*, *PushSubscriptionOptions Interface*, *PushSubscription interface* y
*PushEncryptionKeyName enumeration* de la [*Push API*](../fuentes/w3c/push-api.html) de W3C y
[RFC 8292](../fuentes/rfc/rfc8292.txt).

- Android y Flutter reciben push por FCM.
- Un mensaje de FCM lleva `notification` y, en `data`, la ruta que abre al tocarlo, salvo el de una
  llamada entrante.
- Una llamada entrante llega por un mensaje de FCM solo de datos y de prioridad alta.
- Un push vence cuando caduca lo que avisa; el de una llamada entrante, cuando deja de sonar. En la
  web, el de una llamada lleva `Urgency: high`.
- El token de push y la suscripción web pertenecen a la sesión: se borran cuando la sesión se
  cierra o vence.
- La web recibe push con la Push API, sin el SDK de FCM: la CSP queda en `'self'`.

## Sesión

Estándares: [*Session Management Cheat Sheet*](../fuentes/owasp/Session_Management.md),
[*Cross-Site Request Forgery Prevention Cheat Sheet*](../fuentes/owasp/Cross-Site_Request_Forgery_Prevention.md)
y [*HTML5 Security Cheat Sheet*](../fuentes/owasp/HTML5_Security.md) de OWASP, y
[RFC 6265](../fuentes/rfc/rfc6265.txt).

- La API se sirve en el mismo origen que la web, bajo `/api`. No hace falta CORS, y la cookie de
  sesión es de primera parte.
- El token de acceso vive solo en memoria, y el de refresco, en el almacenamiento seguro del
  cliente.
- En la web, el token de refresco va en una cookie `HttpOnly`, `Secure`, `SameSite=Strict`, con el
  `Path` del endpoint de refresco.
- Ante un 401, el cliente refresca la sesión una sola vez y reintenta una sola vez. Nunca un bucle
  silencioso.

## Tema

- Los tokens de diseño van en un solo módulo por cliente, sin colores ni tamaños literales fuera de
  él. Si el producto tiene superficie web, es la misma paleta y el archivo dice de cuál es espejo.

## Versión mínima de cliente

- Cada cliente instalable manda `User-Agent: <pieza>/<versión>` desde su primera versión publicada,
  como fija [fastapi.md](fastapi.md). Ante `client-outdated`, pide actualizar la app.

## WebSocket

Estándares: [RFC 6455](../fuentes/rfc/rfc6455.txt) y
[*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

- El cliente se autentica mandando el token de acceso en el primer mensaje. Si no llega en 5
  segundos, el servidor cierra con 1008. De las dos formas que da OWASP, el mensaje no deja el
  token en los registros de acceso.
- Al refrescar la sesión, el cliente manda el token nuevo por la misma conexión. Cuando vence el
  que tiene, el servidor cierra con 1008.
- Los mensajes son JSON `{type, data}`, en camelCase como la API.
- Al perder la conexión, el cliente reconecta con espera exponencial y jitter, y vuelve a pedir el
  estado por REST. Lo que se envió mientras estaba desconectado no se repite.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Contraste de los tokens | Una prueba por cliente sobre el módulo de tokens |
| Todo error del servidor en problem+json | `test_unknown_route_is_a_problem` y `test_validation_error_points_to_the_field`, del servidor |
| RFC 9457: la URI de cada tipo sirve su documentación | `test_problem_types_are_documented`, del servidor |
