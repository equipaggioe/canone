# Transversal

Lo que tienen que cumplir juntas varias piezas. Lo que hace una sola pieza va en su página.

## Accesibilidad

Estándar: [WCAG 2.2](../estandares/w3c/wcag22.html) de W3C.

- Todos los clientes cumplen el nivel AA, también las apps. Es la vara que nombra la guía de
  Flutter, y una sola para todos los clientes.
- Cada objetivo táctil mide al menos 48 × 48: dp en las apps y px de CSS en la web. Endurece los 24
  px del criterio 2.5.8, porque la web también se usa en el teléfono, y es la medida que Android
  recomienda.
- El módulo de tokens de diseño cumple los criterios 1.4.3 y 1.4.11 en el tema claro y en el
  oscuro, y una prueba de cada cliente calcula el contraste de cada par de color de texto y de
  fondo. El contraste no se elige a ojo.

## Archivos

Estándar: [*File Upload Cheat Sheet*](../estandares/owasp/File_Upload.md) de OWASP.

- Un archivo se sube solo, como `multipart/form-data`. No pasa por base64 dentro de un JSON.

## Errores

- El sobre de error es RFC 9457, definido en [fastapi.md](fastapi.md). Cada cliente lo traduce a un
  error tipado con los mismos campos. `type` es el contrato; `detail` es texto para mostrar.

## Idiomas

Estándares: [RFC 5646](../estandares/rfc/rfc5646.txt) y [RFC 4647](../estandares/rfc/rfc4647.txt).

- Todo producto se diseña multilingüe.
- El idioma base es `es`.
- La base guarda códigos, nunca textos traducidos, y cada cliente los traduce con su catálogo. Un
  idioma nuevo no toca la base.
- El cliente muestra el texto de su catálogo para el `type` de un error, en vez de `detail`, que el
  servidor escribe solo en el idioma base.

## Llamadas de voz y video

Estándares: [WebRTC](../estandares/w3c/webrtc.html) de W3C,
[RFC 8489](../estandares/rfc/rfc8489.txt) (STUN) y [RFC 8656](../estandares/rfc/rfc8656.txt)
(TURN).

- La señalización va por el WebSocket de la app.
- coturn usa credenciales temporales (`use-auth-secret`), que el servidor entrega por la API. Los
  clientes no guardan una contraseña fija de TURN.

## Mapas

Estándares: la [política de uso de teselas](../estandares/osm/tile-usage-policy.md), la
[política de uso de Nominatim](../estandares/osm/nominatim-usage-policy.md) y la
[guía de atribución](../estandares/osm/attribution-guidelines.md) de OpenStreetMap.

- Las teselas son raster, con URL `{z}/{x}/{y}`. Las dibujan las bibliotecas de mapa de todos los
  clientes.
- Mientras el uso quepa en la política, las teselas son las de `tile.openstreetmap.org`.
- La URL de las teselas y su atribución las entrega el servidor en su configuración pública.
  Ningún cliente las escribe en su código. Endurece la recomendación de la política: cambiar de
  proveedor no exige publicar otra versión de las apps.
- Los clientes buscan direcciones en el servidor, que consulta a Nominatim. El límite de la
  política es por aplicación, y solo el servidor ve el total.

## Montos

- Un monto viaja como `{amount, currency}`, con el monto en cadena, como fija
  [fastapi.md](fastapi.md). Cada cliente lo conserva como cadena o como el decimal de su lenguaje,
  nunca como `double`, y no calcula con él: los totales, impuestos y descuentos llegan calculados del
  servidor. Así ningún cliente necesita una biblioteca decimal.

## Nombres en el cable

- La API habla en camelCase. Cada cliente usa la convención de su lenguaje (`snake_case` en
  Python, camelCase en Dart y TypeScript) y convierte en un solo punto: su cliente de la API.

## Pagos

Estándar: [*Secure Integration of Third-Party Payment Gateways Cheat Sheet*](../estandares/owasp/Third_Party_Payment_Gateway_Integration.md)
de OWASP.

- El proveedor es Stripe.
- El cobro se hace en Stripe Checkout, la página alojada por Stripe. Los datos de la tarjeta nunca
  pasan por nuestras páginas.
- Un pago cuenta como hecho solo cuando llega su webhook. El regreso del navegador no prueba nada.

## Push

Estándares: [*Firebase Cloud Messaging message types*](../estandares/firebase/set-message-type.md),
[*Best practices for FCM registration management*](../estandares/firebase/manage-tokens.md), la
[*Push API*](../estandares/w3c/push-api.html) de W3C y [RFC 8292](../estandares/rfc/rfc8292.txt).

- Android y Flutter reciben push por FCM.
- Cada mensaje de FCM lleva `notification`, que el sistema muestra con la app cerrada, y `data` con
  la ruta que abre al tocarlo.
- La web recibe push por el estándar, con VAPID. El navegador no carga un SDK de terceros y la CSP
  queda en `'self'`.

## Sesión

Estándares: [*Session Management Cheat Sheet*](../estandares/owasp/Session_Management.md),
[*Cross-Site Request Forgery Prevention Cheat Sheet*](../estandares/owasp/Cross-Site_Request_Forgery_Prevention.md)
y [*HTML5 Security Cheat Sheet*](../estandares/owasp/HTML5_Security.md) de OWASP, y
[RFC 6265](../estandares/rfc/rfc6265.txt).

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

Estándares: [RFC 6455](../estandares/rfc/rfc6455.txt) y
[*WebSocket Security Cheat Sheet*](../estandares/owasp/WebSocket_Security.md) de OWASP.

- El cliente se autentica mandando el token de acceso en el primer mensaje. Si no llega en 5
  segundos, el servidor cierra con 1008. De las dos formas que da OWASP, el mensaje no deja el
  token en los registros de acceso.
- Al refrescar la sesión, el cliente manda el token nuevo por la misma conexión. Cuando vence el
  que tiene, el servidor cierra con 1008.
- Los mensajes son JSON `{type, data}`, en camelCase como el resto del cable.
- Al perder la conexión, el cliente reconecta con espera exponencial y jitter, y vuelve a pedir el
  estado por REST. Lo que se envió mientras estaba desconectado no se repite.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Contraste de los tokens | Una prueba por cliente sobre el módulo de tokens |
