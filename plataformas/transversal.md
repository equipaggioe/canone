# Transversal

Lo que tienen que cumplir juntas varias piezas. Lo que hace una sola pieza va en su página.

## Accesibilidad

Estándar: [WCAG 2.2](../fuentes/w3c/wcag22.html) de W3C.

- Las convenciones de esta sección rigen en todos los clientes, también en las apps, donde cada pantalla cuenta como una página web: una sola vara para todos los clientes.
- Una llamada entre usuarios no lleva subtítulos en vivo: el criterio de los subtítulos en vivo apunta a las transmisiones, no a las llamadas entre personas. [WCAG 2.2](https://raw.githubusercontent.com/w3c/wcag/807a6c24c58526d017da5a32ea630ac31e850b71/understanding/20/captions-live.html)
- Cada rol de texto de `brand/tokens/` cumple el contraste del texto contra cada fondo en que va, y `outline`, el de los componentes contra cada superficie, en cada tema y en cada modo. `primary`, `error` y el rol que da nombre a cada custom color son roles de texto.
- Cada objetivo táctil mide al menos 48 × 48, salvo un enlace dentro de una frase: dp en las apps y px de CSS en la web, que también se usa en el teléfono ([WCAG 2.2 §2.5.8](../fuentes/w3c/wcag22.html)).
- El texto contrasta al menos 4.5:1 con su fondo, también el grande, salvo el de un componente inactivo, el decorativo, el que no se ve, el de una imagen con otro contenido importante y el de un logo: un rol de color no sabe el tamaño del texto que lleva ([WCAG 2.2 §1.4.3](../fuentes/w3c/wcag22.html) y [§1.4.6](../fuentes/w3c/wcag22.html)).
- Todo contenido que no es texto tiene una alternativa de texto con el mismo propósito; un control, un nombre que dice para qué sirve, y lo decorativo queda oculto a las tecnologías de apoyo ([WCAG 2.2 §1.1.1](../fuentes/w3c/wcag22.html)).
- La información, la estructura y las relaciones que muestra la presentación se pueden determinar por programa o están en el texto ([WCAG 2.2 §1.3.1](../fuentes/w3c/wcag22.html)).
- Cuando el orden del contenido cambia su sentido, el orden de lectura correcto se puede determinar por programa ([WCAG 2.2 §1.3.2](../fuentes/w3c/wcag22.html)).
- Una instrucción no depende solo de la forma, el color, el tamaño, la ubicación, la orientación o el sonido ([WCAG 2.2 §1.3.3](../fuentes/w3c/wcag22.html)).
- Una pantalla no se limita a la orientación vertical o a la horizontal, salvo que la orientación sea esencial ([WCAG 2.2 §1.3.4](../fuentes/w3c/wcag22.html)).
- El propósito de cada campo que pide un dato del usuario de la lista de propósitos de entrada de WCAG se puede determinar por programa ([WCAG 2.2 §1.3.5](../fuentes/w3c/wcag22.html)).
- El color no es el único medio de transmitir información, indicar una acción, pedir una respuesta ni distinguir un elemento ([WCAG 2.2 §1.4.1](../fuentes/w3c/wcag22.html)).
- Un sonido que empieza solo y dura más de 3 segundos, como el timbre de una llamada, se puede pausar o detener, o tiene un volumen propio, aparte del del sistema ([WCAG 2.2 §1.4.2](../fuentes/w3c/wcag22.html)).
- El texto crece hasta el 200 % sin tecnologías de apoyo y sin perder contenido ni funciones ([WCAG 2.2 §1.4.4](../fuentes/w3c/wcag22.html)).
- La información va en texto, no en imágenes de texto, salvo una imagen de texto que el usuario puede ajustar a lo que necesita, o una presentación del texto que sea esencial, como un logo ([WCAG 2.2 §1.4.5](../fuentes/w3c/wcag22.html)).
- El contenido se lee sin desplazarse en dos dimensiones con un ancho de 320 px de CSS, salvo lo que necesita dos dimensiones, como un mapa ([WCAG 2.2 §1.4.10](../fuentes/w3c/wcag22.html)).
- Lo que identifica un componente y su estado, y las partes de un gráfico que hacen falta para entenderlo, contrastan al menos 3:1 con lo que tienen al lado, salvo un componente inactivo o uno cuya apariencia fija el agente de usuario sin que el cliente la cambie ([WCAG 2.2 §1.4.11](../fuentes/w3c/wcag22.html)).
- En la web, llevar el interlineado a 1.5 veces el tamaño de la letra, el espacio después de un párrafo a 2 veces, el espacio entre letras a 0.12 veces y el espacio entre palabras a 0.16 veces no hace perder contenido ni funciones ([WCAG 2.2 §1.4.12](../fuentes/w3c/wcag22.html)).
- El contenido que aparece al pasar el puntero o al recibir el foco se puede cerrar sin moverlos, deja pasar el puntero por encima sin desaparecer y queda visible hasta que se quita el puntero o el foco, se cierra o deja de valer ([WCAG 2.2 §1.4.13](../fuentes/w3c/wcag22.html)).
- Toda función se puede usar con el teclado, sin tiempos para cada tecla, salvo la que depende del recorrido del movimiento ([WCAG 2.2 §2.1.1](../fuentes/w3c/wcag22.html)).
- El foco que entra a un componente con el teclado puede salir de él con el teclado, y si para salir hace falta algo más que las flechas, el tabulador u otra forma estándar, se le dice al usuario cómo ([WCAG 2.2 §2.1.2](../fuentes/w3c/wcag22.html)).
- Un atajo de una sola tecla de carácter se puede apagar o reasignar, o solo actúa cuando su componente tiene el foco ([WCAG 2.2 §2.1.4](../fuentes/w3c/wcag22.html)).
- Un plazo que impone el cliente se puede apagar o ampliar al menos diez veces antes de llegar a él, o se avisa antes de que venza y se extiende con una acción simple, con al menos 20 segundos para hacerlo y al menos diez veces, salvo que sea parte de un evento en tiempo real, sea esencial o pase de 20 horas ([WCAG 2.2 §2.2.1](../fuentes/w3c/wcag22.html)).
- Lo que se mueve, parpadea o se desplaza solo durante más de 5 segundos junto a otro contenido se puede pausar, detener u ocultar, y lo que se actualiza solo junto a otro contenido se puede pausar, detener, ocultar o cambiar de frecuencia, salvo que sea esencial ([WCAG 2.2 §2.2.2](../fuentes/w3c/wcag22.html)).
- Nada destella más de tres veces por segundo, salvo por debajo de los umbrales de destello ([WCAG 2.2 §2.3.1](../fuentes/w3c/wcag22.html)).
- Un bloque que se repite en varias pantallas se puede saltar ([WCAG 2.2 §2.4.1](../fuentes/w3c/wcag22.html)).
- Cada pantalla tiene un título que describe su tema o su propósito ([WCAG 2.2 §2.4.2](../fuentes/w3c/wcag22.html)).
- El foco recorre los componentes en un orden que conserva su sentido y su uso ([WCAG 2.2 §2.4.3](../fuentes/w3c/wcag22.html)).
- El propósito de cada enlace se entiende por su texto o por su contexto ([WCAG 2.2 §2.4.4](../fuentes/w3c/wcag22.html)).
- A cada pantalla se llega por más de un camino, salvo a la que es un paso o el resultado de un proceso ([WCAG 2.2 §2.4.5](../fuentes/w3c/wcag22.html)).
- Los títulos y las etiquetas describen su tema o su propósito ([WCAG 2.2 §2.4.6](../fuentes/w3c/wcag22.html)).
- El foco del teclado se ve ([WCAG 2.2 §2.4.7](../fuentes/w3c/wcag22.html)).
- Un componente que recibe el foco no queda tapado entero por otro contenido del cliente ([WCAG 2.2 §2.4.11](../fuentes/w3c/wcag22.html)).
- Lo que se hace con un gesto de varios puntos o de recorrido también se hace con un solo puntero sin recorrido, salvo que el gesto sea esencial ([WCAG 2.2 §2.5.1](../fuentes/w3c/wcag22.html)).
- Una función de un solo puntero no actúa al bajar el puntero, actúa al soltarlo y se puede abortar o deshacer, o al soltarlo revierte lo que hizo al bajarlo, salvo que actuar al bajarlo sea esencial ([WCAG 2.2 §2.5.2](../fuentes/w3c/wcag22.html)).
- El nombre de un componente con una etiqueta visible contiene el texto de esa etiqueta ([WCAG 2.2 §2.5.3](../fuentes/w3c/wcag22.html)).
- Lo que se acciona moviendo el dispositivo también se acciona con un componente, y la respuesta al movimiento se puede apagar, salvo que el movimiento llegue por una interfaz que las tecnologías de apoyo soportan o sea esencial ([WCAG 2.2 §2.5.4](../fuentes/w3c/wcag22.html)).
- Lo que se hace arrastrando también se hace con un solo puntero sin arrastrar, salvo que arrastrar sea esencial o lo fije el agente de usuario sin que el cliente lo cambie ([WCAG 2.2 §2.5.7](../fuentes/w3c/wcag22.html)).
- El idioma de cada pantalla se puede determinar por programa ([WCAG 2.2 §3.1.1](../fuentes/w3c/wcag22.html)).
- El idioma de cada fragmento en otro idioma se puede determinar por programa, salvo los nombres propios y los términos técnicos ([WCAG 2.2 §3.1.2](../fuentes/w3c/wcag22.html)).
- Recibir el foco no cambia el contexto ([WCAG 2.2 §3.2.1](../fuentes/w3c/wcag22.html)).
- Cambiar el valor de un componente no cambia el contexto sin haberlo avisado antes ([WCAG 2.2 §3.2.2](../fuentes/w3c/wcag22.html)).
- La navegación que se repite en varias pantallas va siempre en el mismo orden, salvo que el usuario lo cambie ([WCAG 2.2 §3.2.3](../fuentes/w3c/wcag22.html)).
- Los componentes con la misma función se identifican igual en todas las pantallas ([WCAG 2.2 §3.2.4](../fuentes/w3c/wcag22.html)).
- La ayuda que se repite en varias pantallas va siempre en el mismo orden, salvo que el usuario lo cambie ([WCAG 2.2 §3.2.6](../fuentes/w3c/wcag22.html)).
- Un error de entrada que se detecta solo señala el campo y se describe en texto ([WCAG 2.2 §3.3.1](../fuentes/w3c/wcag22.html)).
- Todo lo que pide una entrada tiene una etiqueta o instrucciones ([WCAG 2.2 §3.3.2](../fuentes/w3c/wcag22.html)).
- Ante un error de entrada con una corrección conocida, el cliente la sugiere, salvo que eso comprometa la seguridad ([WCAG 2.2 §3.3.3](../fuentes/w3c/wcag22.html)).
- Un pago, un compromiso legal y un cambio o un borrado de datos del usuario se pueden revertir, se revisan en busca de errores con la oportunidad de corregirlos, o se confirman antes de enviarse ([WCAG 2.2 §3.3.4](../fuentes/w3c/wcag22.html)).
- Un dato que el usuario ya dio en un proceso se completa solo o se ofrece para elegir cuando se vuelve a pedir, salvo que volver a darlo sea esencial, lo pida la seguridad o ya no valga ([WCAG 2.2 §3.3.7](../fuentes/w3c/wcag22.html)).
- Ningún paso de una autenticación exige una prueba cognitiva, como recordar una contraseña, sin otro método que no la exija o un mecanismo que ayude a resolverla, salvo que la prueba sea reconocer objetos o identificar un contenido que no es texto que el propio usuario dio ([WCAG 2.2 §3.3.8](../fuentes/w3c/wcag22.html)).
- Cada componente tiene un nombre y un rol que se pueden determinar por programa, sus estados y valores se pueden fijar por programa, y sus cambios llegan a las tecnologías de apoyo ([WCAG 2.2 §4.1.2](../fuentes/w3c/wcag22.html)).
- Un mensaje de estado llega a las tecnologías de apoyo sin mover el foco ([WCAG 2.2 §4.1.3](../fuentes/w3c/wcag22.html)).
- Cada pantalla cumple entera, en cada variante que presenta según el tamaño, y un proceso cumple en todos sus pasos ([WCAG 2.2 §5.2.2](../fuentes/w3c/wcag22.html) y [§5.2.3](../fuentes/w3c/wcag22.html)).
- Se cumple solo con formas de usar la tecnología que las tecnologías de apoyo soportan, y lo que no cumple no impide usar el resto de la pantalla ([WCAG 2.2 §5.2.4](../fuentes/w3c/wcag22.html) y [§5.2.5](../fuentes/w3c/wcag22.html)).

## Archivos

- Un archivo se sube como `multipart/form-data`, en su propia petición, nunca en base64 dentro de un JSON: base64 agranda el archivo un tercio y el servidor lee el JSON entero en memoria.

## Distribución

- Cada repositorio declara en variables de GitHub Actions en qué plataformas construye y publica cada pieza: `RELEASE_<PIEZA>_<PLATAFORMA>`, con `true` o `false`, como `RELEASE_CUSTOMER_IOS` o `RELEASE_DESKTOP_MACOS`. Una app en Flutter o en Flet lleva `ANDROID` e `IOS`; una en Kotlin, `ANDROID`, y `desktop/`, `LINUX`, `MACOS` y `WINDOWS`. CI falla si falta una, si vale otra cosa o si no es de ninguna pieza: con un valor por defecto, un repositorio mal configurado dejaría de publicar en una plataforma sin que nadie lo note.
- Los ejecutables y los instaladores de Windows van sin firmar.
- Una app de iOS se publica en la App Store.
- La versión de macOS de una app de escritorio es un DMG con la app dentro, notarizado y con el ticket grapado: desde macOS 15, una app descargada sin notarizar no abre sin pasar por los ajustes de seguridad del sistema. [Updates to runtime protection in macOS Sequoia](https://developer.apple.com/news/?id=saqachfa)
- El número de build de una app de Android, de Flutter o de Flet es un entero que vive en su manifiesto, junto a su versión, y sube con cada versión que se publica.
- Una app de Android se publica en Google Play con Play App Signing: la llave que firma la app la genera y la guarda Play, y cada versión llega a Play firmada con la llave de subida. [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)
- La descarga directa de una app de Android, si la tiene, es el APK universal que Play genera de esa misma versión: la tienda y la descarga llevan la misma firma, y una app instalada por una se actualiza por la otra. [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)

## Errores

Estándares: [RFC 9457](../fuentes/rfc/rfc9457.txt) y [RFC 9110](../fuentes/rfc/rfc9110.txt).

- Todo error que genera el servidor es `application/problem+json`, salvo los del endpoint de token, que siguen [autenticacion.md](autenticacion.md#código-de-autorización).
- La URI de un tipo propio es `https://<dominio>/api/problems/<nombre>`, con el mismo dominio en todos los entornos: un mismo error tiene un solo `type`.
- Todo problem+json lleva `traceId`, el trace-id de la petición.
- Un error de validación es de tipo `https://<dominio>/api/problems/validation`, con la extensión `errors`: una lista de `{detail, pointer}`, o de `{detail, parameter}` para un parámetro que no viene en el cuerpo.
- `pointer` es un JSON Pointer en su forma de cadena JSON, sin `#` ni la codificación de URI del fragmento.
- El cliente toma una respuesta de error sin problem+json, o con un `type` que su catálogo no conoce, como de tipo `about:blank`, con su `status`, y su catálogo tiene un texto por `status` para ese tipo.
- Ante un 5xx o un `type` que su catálogo no conoce, el cliente muestra el `traceId` junto al texto, para que el usuario lo copie.
- Cada cliente traduce el sobre a un error tipado con los mismos campos.
- Todo problem+json lleva `status`, y ninguno lleva `instance`: `traceId` ya identifica la ocurrencia ([RFC 9457 §3.1.2](../fuentes/rfc/rfc9457.txt) y [§3.1.5](../fuentes/rfc/rfc9457.txt)).
- Un error que su código de estado ya explica no tiene tipo propio: es de tipo `about:blank` ([RFC 9457 §4](../fuentes/rfc/rfc9457.txt) y [§4.2.1](../fuentes/rfc/rfc9457.txt)).
- `status` es el código de estado de la respuesta ([RFC 9457 §3.1.2](../fuentes/rfc/rfc9457.txt)).
- El `title` de un tipo no cambia de una ocurrencia a otra, salvo por el idioma, y el de `about:blank` es la frase de su código de estado ([RFC 9457 §3.1.3](../fuentes/rfc/rfc9457.txt) y [§4.2.1](../fuentes/rfc/rfc9457.txt)).
- `detail` ayuda al cliente a corregir el problema, sin datos de depuración ni de la implementación ([RFC 9457 §3.1.4](../fuentes/rfc/rfc9457.txt), [§4](../fuentes/rfc/rfc9457.txt) y [§5](../fuentes/rfc/rfc9457.txt)).
- Un tipo propio documenta su URI, su `title` y su código de estado, y su URI responde en HTML esa documentación y cómo resolver el problema ([RFC 9457 §3.1.1](../fuentes/rfc/rfc9457.txt) y [§4](../fuentes/rfc/rfc9457.txt)).
- El nombre de una extensión empieza con una letra, lleva solo letras, dígitos y `_`, y tiene al menos tres caracteres ([RFC 9457 §4](../fuentes/rfc/rfc9457.txt)).
- Ante varios problemas de tipos distintos, la respuesta lleva el más relevante ([RFC 9457 §3](../fuentes/rfc/rfc9457.txt)).
- El cliente identifica el problema por su `type`, y uno sin `type` es de tipo `about:blank` ([RFC 9457 §3.1.1](../fuentes/rfc/rfc9457.txt)).
- El cliente no descarga la URI de un tipo ([RFC 9457 §3.1.1](../fuentes/rfc/rfc9457.txt)).
- El cliente no extrae datos de `detail`: lo que necesita leer va en una extensión ([RFC 9457 §3.1.4](../fuentes/rfc/rfc9457.txt)).
- El cliente ignora un miembro cuyo valor no tiene el tipo que le corresponde, y una extensión que no conoce ([RFC 9457 §3.1](../fuentes/rfc/rfc9457.txt) y [§3.2](../fuentes/rfc/rfc9457.txt)).
- Un cuerpo que no es JSON responde 400, y uno que es JSON pero no se puede procesar, 422 ([RFC 9110 §15.5.1](../fuentes/rfc/rfc9110.txt) y [§15.5.21](../fuentes/rfc/rfc9110.txt)).
- El cliente trata un código de estado que no conoce como el x00 de su clase, y uno fuera de 100 a 599 como un 5xx ([RFC 9110 §15](../fuentes/rfc/rfc9110.txt)).

## Fechas

Estándar: [I-JSON](../fuentes/rfc/rfc7493.txt), RFC 7493.

- Una duración viaja como un entero de segundos: una duración en meses o en días no equivale a una cantidad fija de segundos.
- Una fecha sin hora viaja como una cadena `full-date` de RFC 3339, como `2026-01-08`.
- Una zona horaria viaja con su nombre de la base IANA, como `America/Mexico_City`.
- Una fecha con hora viaja como una cadena de RFC 3339, con las letras en mayúsculas, con su desfase y con los segundos aunque valgan `00` ([I-JSON §4.3](../fuentes/rfc/rfc7493.txt)).

## Idiomas

Estándares: [RFC 5646](../fuentes/rfc/rfc5646.txt) y [RFC 9110](../fuentes/rfc/rfc9110.txt).

- Todo producto se diseña multilingüe.
- El idioma base es `es`.
- La base guarda códigos, nunca textos traducidos, y cada cliente los traduce con su catálogo.
- El cliente muestra el texto de su catálogo para el `type` de un error, en vez de `detail`: el texto que ve el usuario sale del mismo catálogo que traduce el resto del cliente.
- El cliente manda en `Accept-Language` el idioma que eligió el usuario ([RFC 9110 §12.5.4](../fuentes/rfc/rfc9110.txt)).
- Un idioma se nombra con una etiqueta válida, en su forma canónica y con solo las subetiquetas que distinguen el texto ([RFC 5646 §2](../fuentes/rfc/rfc5646.txt), [§4.1](../fuentes/rfc/rfc5646.txt) y [§4.5](../fuentes/rfc/rfc5646.txt)).
- Una etiqueta se escribe como en el registro: el idioma en minúsculas, el script con la inicial en mayúscula y la región en mayúsculas ([RFC 5646 §2.1.1](../fuentes/rfc/rfc5646.txt)).
- Dos etiquetas se comparan sin distinguir mayúsculas de minúsculas ([RFC 5646 §2.1.1](../fuentes/rfc/rfc5646.txt)).

## Llamadas de voz y video

- La señalización va por el WebSocket de la app.
- coturn usa credenciales temporales, que el servidor entrega por la API.
- El cliente pide una credencial al iniciar o al atender cada llamada, y antes de cada reinicio de ICE: con una credencial vencida, coturn no abre un relay nuevo. [coturn 4.6.1](https://raw.githubusercontent.com/coturn/coturn/4.6.1/src/apps/relay/userdb.c)
- Mientras suena, el servidor guarda la llamada con su oferta, y quien la recibe la pide por REST al conectarse o al despertar por el push. El resto de la señalización no se guarda.
- Cualquiera de los dos puede mandar una oferta. Si dos se cruzan, el que atiende descarta la suya con *rollback* y acepta la del que llama.

## Mapas

Estándares: la [guía de atribución](../fuentes/osm/attribution-guidelines.md) de OpenStreetMap y [RFC 7946](../fuentes/rfc/rfc7946.txt).

- Toda posición o trazado en la API es una geometría GeoJSON.
- Las teselas son vectoriales, de OpenFreeMap.
- El mapa usa el estilo `positron` de OpenFreeMap en el modo claro, y `dark` en el oscuro: el mapa sigue el modo de la app ([Tema](#tema)), y los dos estilos comparten las teselas.
- La URL de cada estilo y la atribución las entrega el servidor en su configuración pública: cambiar de proveedor no exige publicar otra versión de las apps.
- Cada cliente muestra la atribución de la configuración como texto, y apaga el control de atribución de MapLibre: MapLibre la esconde detrás de un botón, en las apps siempre y en la web en un mapa de hasta 640 px de ancho. [MapLibre GL JS 6.18.0](https://raw.githubusercontent.com/maplibre/maplibre-gl-js/v6.18.0/src/ui/control/attribution_control.ts) [maplibre_gl 0.28.0](https://raw.githubusercontent.com/maplibre/flutter-maplibre-gl/v0.28.0/maplibre_gl/lib/src/maplibre_map.dart) [MapLibre Android 13.7.1](https://raw.githubusercontent.com/maplibre/maplibre-native/android-v13.7.1/platform/android/MapLibreAndroid/src/main/java/org/maplibre/android/maps/AttributionDialogManager.java)
- Los clientes buscan direcciones en el servidor, que consulta a Nominatim: su límite es por aplicación, y solo el servidor ve el total. [Nominatim](https://raw.githubusercontent.com/openstreetmap/owg-website/fd6937012a5b2d8f4c0255148342b97191c840e7/policies/nominatim.md)
- La atribución nombra además a OpenFreeMap y a OpenMapTiles, como la que publica OpenFreeMap con sus teselas.
- Una posición lleva solo la longitud y la latitud, sin altitud ([RFC 7946 §3.1.1](../fuentes/rfc/rfc7946.txt)).
- La atribución va en una esquina del mapa, legible y a la vista sin tocar el mapa ([OSM, *Requirements to fit within OSMF’s safe harbour*](../fuentes/osm/attribution-guidelines.md) y [*Interactive maps*](../fuentes/osm/attribution-guidelines.md)).
- Las coordenadas van en WGS 84, en grados decimales, primero la longitud y después la latitud ([RFC 7946 §3.1.1](../fuentes/rfc/rfc7946.txt) y [§4](../fuentes/rfc/rfc7946.txt)).
- Un trazado que cruza el antimeridiano se corta en dos y viaja como un `MultiLineString` ([RFC 7946 §3.1.9](../fuentes/rfc/rfc7946.txt)).
- No se agregan tipos a GeoJSON ni se cambia el sentido de sus miembros ([RFC 7946 §7](../fuentes/rfc/rfc7946.txt) y [§7.1](../fuentes/rfc/rfc7946.txt)).
- El cliente no toma la cantidad de decimales de una coordenada como su precisión ([RFC 7946 §3.1.10](../fuentes/rfc/rfc7946.txt)).
- La atribución dice «OpenStreetMap» y lleva a `openstreetmap.org/copyright` ([OSM, *Attribution text*](../fuentes/osm/attribution-guidelines.md)).
- Ninguna otra atribución hace creer que los datos no son de OpenStreetMap ([OSM, *Requirements to fit within OSMF’s safe harbour*](../fuentes/osm/attribution-guidelines.md)).
- Un cliente que busca direcciones con Nominatim atribuye a OpenStreetMap ([OSM, *Geocoding (search)*](../fuentes/osm/attribution-guidelines.md)).

## Montos

Estándar: [I-JSON](../fuentes/rfc/rfc7493.txt), RFC 7493.

- Un monto viaja como `{"amount": "10.50", "currency": "USD"}`: `amount` sin exponente, y `currency`, el código de la moneda en la [lista de monedas](https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml) de ISO 4217.
- Un monto no se formatea sin su moneda.
- Cada cliente lo conserva como cadena o como el decimal de su lenguaje, nunca como `double`, y no calcula con él: los totales, impuestos y descuentos llegan calculados del servidor. Así ningún cliente necesita una biblioteca decimal.
- `amount` es una cadena decimal: un monto pide un valor exacto ([I-JSON §2.2](../fuentes/rfc/rfc7493.txt)).

## OpenAPI y clientes

Estándar: [I-JSON](../fuentes/rfc/rfc7493.txt), RFC 7493.

- La API habla en camelCase.
- Cada cliente genera del `openapi.json` del servidor los modelos del cable, en la convención de su lenguaje, y ninguno los escribe a mano: copiado a mano en varios lenguajes, el contrato diverge sin que nadie lo note.
- Un cliente falla ante un campo que no conoce en una respuesta del servidor, salvo en un problem+json, que sigue [Errores](#errores), y salvo la web, que sale en el mismo artefacto que el servidor y se recarga cuando cambia de versión ([sveltekit.md](sveltekit.md#carga-de-datos)): como en el servidor, un campo desconocido es un error del contrato que tiene que verse.
- La respuesta de un servicio externo se lee con modelos escritos a mano, que validan los campos que el cliente lee e ignoran los que no conoce: el servicio agrega campos sin avisar, y su contrato no sale del `openapi.json`.
- Los valores de un enum van en snake_case.
- El servidor responde 422 a un campo o un parámetro que no conoce: el cliente y el servidor salen del mismo contrato, y un campo desconocido es un error del cliente que tiene que verse.
- El servidor rechaza con un error un mensaje que no es I-JSON ([I-JSON §3](../fuentes/rfc/rfc7493.txt)).
- Un mensaje va en UTF-8, y ni sus nombres ni sus cadenas llevan sustitutos sueltos ni no-caracteres de Unicode ([I-JSON §2.1](../fuentes/rfc/rfc7493.txt)).
- Ningún número pasa la magnitud o la precisión de un `double`, ni un entero pasa de 2⁵³ − 1 en valor absoluto ([I-JSON §2.2](../fuentes/rfc/rfc7493.txt)).
- Un objeto no repite el nombre de un miembro ([I-JSON §2.3](../fuentes/rfc/rfc7493.txt)).
- Un mensaje es un objeto o un arreglo ([I-JSON §4.1](../fuentes/rfc/rfc7493.txt)).
- Un dato binario va en una cadena en base64url, salvo un archivo, que se sube como fija [Archivos](#archivos) ([I-JSON §4.4](../fuentes/rfc/rfc7493.txt)).

Plantilla: [ijson.py](../plantilla/server/src/app/ijson.py), del servidor de [fastapi.md](fastapi.md), rechaza el cuerpo que no es I-JSON.

## Paginación

Estándar: [*Pagination*](../fuentes/google-aip/aip-0158.md), la AIP-158 de Google.

- La respuesta es `{"items": [...], "nextPageToken": "..."}`, y el campo `nextPageToken` siempre está.
- Con `skip`, un `pageSize` mayor que 100 responde 422: el cliente calcula `skip` con el tamaño que pidió, y un recorte se saltaría filas.
- Un error de paginación, o un `pageToken` ilegible, responde 422 de tipo `validation`, con `parameter` en el parámetro que falla.
- `pageSize` vale 50 si no viene o vale 0, y 100 como máximo. Sin `skip`, uno mayor se recorta a 100 ([AIP-158, *Guidance*](../fuentes/google-aip/aip-0158.md)).
- Una lista que muestra números de página acepta `skip` y devuelve `totalSize`, el total exacto. Las demás no ([AIP-158, *Guidance*](../fuentes/google-aip/aip-0158.md) y [*Skipping results*](../fuentes/google-aip/aip-0158.md)).
- Toda lista se pagina desde su primera versión ([AIP-158, *Guidance*](../fuentes/google-aip/aip-0158.md)).
- `pageSize` y `pageToken` son opcionales, y un `pageSize` negativo es un error ([AIP-158, *Guidance*](../fuentes/google-aip/aip-0158.md)).
- Un `pageToken` con otros parámetros que los de la petición que lo dio es un error, y un `pageSize` distinto se respeta ([AIP-158, *Guidance*](../fuentes/google-aip/aip-0158.md)).
- Una página puede traer menos elementos que `pageSize` aunque no sea la última. Solo la última trae `nextPageToken` vacío ([AIP-158, *Guidance*](../fuentes/google-aip/aip-0158.md)).
- La respuesta no es un stream ([AIP-158, *Guidance*](../fuentes/google-aip/aip-0158.md)).
- `skip` cuenta elementos, no páginas, y se suma a la posición del `pageToken`. Uno que pasa del total responde 200 con `items` vacío y `nextPageToken` vacío ([AIP-158, *Skipping results*](../fuentes/google-aip/aip-0158.md)).
- El `pageToken` es opaco y apto para una URL, y el cliente no lo interpreta: codificarlo en base64 no lo vuelve opaco ([AIP-158, *Opacity*](../fuentes/google-aip/aip-0158.md)).
- El `pageToken` solo dice dónde seguir: no da acceso a nada, y cada petición comprueba sus permisos como cualquier otra ([AIP-158, *Opacity*](../fuentes/google-aip/aip-0158.md)).

## Pagos

- El cliente cobra con el componente que la pasarela integra en él: la hoja de pago nativa en las apps y el formulario incrustado en la web, porque salir de la app para pagar se ve poco profesional. Si la pasarela no tiene uno para ese cliente, manda a su página.

## Push

Estándares: la [*Push API*](../fuentes/w3c/push-api.html) de W3C, [RFC 8030](../fuentes/rfc/rfc8030.txt) y [RFC 8292](../fuentes/rfc/rfc8292.txt).

- Android y Flutter reciben push por FCM.
- Un mensaje de FCM lleva `notification` y, en `data`, la ruta que abre al tocarlo, salvo el de una llamada entrante.
- Una llamada entrante llega por un mensaje de FCM solo de datos y de prioridad alta.
- Un push vence cuando caduca lo que avisa; el de una llamada entrante, cuando deja de sonar.
- El FID y la suscripción web pertenecen a la sesión: se borran cuando la sesión se cierra o vence.
- Registrar una suscripción web reemplaza la que tenía la sesión, y registrar la misma otra vez no cambia nada: la web la vuelve a mandar al abrir y cuando el navegador la renueva, y no sabe cuál tenía antes.
- La web recibe push con la Push API, sin el SDK de FCM: la CSP queda en `'self'`.
- En la web, el push de una llamada entrante lleva `Urgency: high` ([RFC 8030 §5.3](../fuentes/rfc/rfc8030.txt)).
- El JWT lleva en `sub` un `mailto:` de contacto del producto ([RFC 8292 §2.1](../fuentes/rfc/rfc8292.txt)).
- Un Web Push es un mensaje declarativo: `web_push` vale 8030, y `notification` lleva `title` y, en `navigate`, la ruta que abre ([Push API, *Declarative push message*](../fuentes/w3c/push-api.html)).
- La web le manda al servidor su suscripción como la serializa `toJSON()`: `endpoint`, `expirationTime` y, en `keys`, `p256dh` y `auth` en base64url ([Push API, *PushSubscription interface*](../fuentes/w3c/push-api.html) y [*PushEncryptionKeyName enumeration*](../fuentes/w3c/push-api.html)).
- Cada Web Push lleva el JWT de VAPID del servidor ([RFC 8292 §2](../fuentes/rfc/rfc8292.txt)).
- La web se suscribe con `applicationServerKey`, la clave pública de VAPID del servidor: un punto de P-256 sin comprimir, en base64url ([Push API, *PushSubscriptionOptions Interface*](../fuentes/w3c/push-api.html)).
- La clave de VAPID es un par de ECDSA sobre P-256, y el JWT se firma con ES256 ([RFC 8292 §2](../fuentes/rfc/rfc8292.txt)).
- El JWT lleva en `aud` el origen del endpoint, y en `exp`, un vencimiento a lo sumo 24 horas después de la petición ([RFC 8292 §2](../fuentes/rfc/rfc8292.txt)).
- La clave de VAPID no es la del cifrado del mensaje ([RFC 8292 §3.2](../fuentes/rfc/rfc8292.txt)).

## Reintentos

Estándar: [RFC 9110](../fuentes/rfc/rfc9110.txt).

- Un recurso que el usuario crea desde un cliente se crea por `PUT /<recurso>/{id}`, con un uuid v4 que genera el cliente. Si la respuesta se pierde, la petición repetida cae sobre la misma fila en vez de crear otra.
- El cliente reintenta ante un fallo de red, un 502, un 503 o un 504, hasta 3 veces, con espera exponencial y jitter, también con un servicio externo: un reinicio del servidor, propio o externo, no le muestra un error al usuario.
- El cliente reintenta solo una petición idempotente ([RFC 9110 §9.2.2](../fuentes/rfc/rfc9110.txt)).
- Un `PUT` o un `DELETE` repetido tiene el mismo efecto que uno solo ([RFC 9110 §9.2.2](../fuentes/rfc/rfc9110.txt)).
- Un `PUT` que crea el recurso responde 201, y uno que lo reemplaza, 200 o 204 ([RFC 9110 §9.3.4](../fuentes/rfc/rfc9110.txt)).

## Tema

Estándares: de DTCG 2025.10, el [formato](../fuentes/dtcg/format.html), el [módulo de color](../fuentes/dtcg/color.html) y el [resolver](../fuentes/dtcg/resolver.html).

- Los colores de un producto van en `brand/tokens/`: `colors.resolver.json` y los `.tokens.json` que cita. Son la única fuente de los colores de todos sus clientes.
- Los tokens tienen dos niveles: el grupo `palette` guarda los colores, en sRGB y opacos, y el grupo `color` asigna cada rol a un color de `palette` con un alias. Cambiar un color de la marca toca un solo token.
- Los roles son las 46 propiedades de color no obsoletas del `ColorScheme` de Flutter y los de los custom colors del producto, y cada modo los asigna todos. Compose, Flutter y Flet arman su esquema con esos roles, y uno sin asignar tomaría en silencio el color por defecto del framework.
- Un estado que el `ColorScheme` no tiene lleva un custom color de Material: una familia de cuatro roles, `x`, `onX`, `xContainer` y `onXContainer`, que son el `color`, `onColor`, `colorContainer` y `onColorContainer` de su `ColorGroup`. [material-color-utilities](https://raw.githubusercontent.com/material-foundation/material-color-utilities/4dbd965df653f8c82d09c0c96c8067d4b7fa9070/typescript/utils/theme_utils.ts)
- El éxito es el custom color `success`, y la advertencia, `warning`.
- Un custom color se nombra con minúsculas y dígitos, y no con el de un rol del `ColorScheme`: es un campo en cada cliente. Todos los temas y los modos tienen los mismos custom colors.
- Cada producto elige sus temas y sus modos: uno o más temas, y el modo claro, el oscuro o los dos. Cada tema tiene los modos del producto.
- Un tema cambia la paleta, y los modos asignan los roles: el mismo rol toma el mismo tono en todos los temas. Los archivos de un tema solo tienen el grupo `palette`, y los de un modo, solo el grupo `color`.
- Un tema se nombra con minúsculas y dígitos: es un miembro de un enum en cada cliente y un valor de `data-theme` en la web.
- `scripts/tokens.py` genera en cada cliente el enum `ColorTheme`, con un miembro por tema y un esquema ya armado por modo, y el tema inicial. Si el producto tiene custom colors, genera también la clase `CustomColors`, y cada tema tiene uno por modo, aparte del esquema.
- `scripts/tokens.py` falla ante lo que DTCG define fuera de las partes que siguen, ante un color que no cumpla el contraste de [Accesibilidad](#accesibilidad) y ante dos temas iguales: un producto solo usa colores sRGB opacos.
- Lo generado se commitea: un cliente compila sin correr el generador.
- Con un solo modo, el cliente lo usa siempre, aunque el sistema esté en el otro.
- Con los dos modos, el usuario elige el modo en la app: sistema, claro u oscuro. Con «sistema», con el que empieza, el cliente sigue el modo del sistema y cambia con él.
- Si el producto tiene más de un tema, el usuario también lo elige, y empieza con el inicial.
- Lo que elige el usuario son preferencias de cada dispositivo: la misma cuenta puede usar el modo oscuro en el teléfono y el claro en la computadora.
- `colors.resolver.json` tiene dos modificadores: `theme`, con un contexto por tema y el inicial en `default`, y `mode`, con `light`, `dark` o los dos ([DTCG Resolver §4.1.5](../fuentes/dtcg/resolver.html)).
- `brand/tokens/` sigue del formato las partes *Name and value*, *Description*, *Type*, *Group Structure* y *Curly Brace Syntax*, que hace cumplir `scripts/tokens.py` ([DTCG Format §5.1](../fuentes/dtcg/format.html), [§5.2.1](../fuentes/dtcg/format.html), [§5.2.2](../fuentes/dtcg/format.html), [§6.1](../fuentes/dtcg/format.html) y [§7.1.1](../fuentes/dtcg/format.html)).
- `brand/tokens/` sigue del módulo de color las partes *Format* y *sRGB*, que hace cumplir `scripts/tokens.py`, salvo un `alpha` menor que 1 y el valor `none` en un componente: un color de la paleta es opaco y tiene sus tres componentes ([DTCG Color §4.1](../fuentes/dtcg/color.html) y [§4.2.1](../fuentes/dtcg/color.html)).
- `brand/tokens/` sigue del resolver las partes *Root level properties* y *Reference objects*, que hace cumplir `scripts/tokens.py`, salvo tres reglas. Un modificador puede tener un solo contexto: un producto puede tener un solo tema o un solo modo. Los tokens van en los `.tokens.json`, no en línea en el resolver. Un `$ref` no lleva otras claves y apunta a un set, a un modificador desde `resolutionOrder` o a un `.tokens.json` entero de `brand/tokens/`: el resolver solo ordena los archivos ([DTCG Resolver §4.1](../fuentes/dtcg/resolver.html) y [§4.2](../fuentes/dtcg/resolver.html)).

Plantilla: `scripts/tokens.py` es canónico y se copia sin editar; `brand/tokens/` es un punto de partida.

## Versión mínima de cliente

Estándar: [RFC 9110](../fuentes/rfc/rfc9110.txt).

- La versión son tres enteros, `MAJOR.MINOR.PATCH`, y se compara número por número.
- Una versión menor que la mínima de su pieza recibe un error de tipo `https://<dominio>/api/problems/client-outdated`, y el cliente pide actualizar la app. Lo mismo recibe una petición con un token de app sin un `User-Agent` de pieza, o con una versión mal formada: el olvido falla en desarrollo.
- El `User-Agent` de pieza y la versión mínima van desde la primera versión que se publica: a una app instalada sin ellos nunca se le puede obligar a actualizar.
- `client-outdated` es un 400 ([RFC 9110 §15.5.1](../fuentes/rfc/rfc9110.txt)).
- Cada cliente instalable manda en cada petición `User-Agent: <pieza>/<versión>`, sin otros productos ni comentarios ([RFC 9110 §10.1.5](../fuentes/rfc/rfc9110.txt)).

## WebSocket

Estándar: el [*WebSocket Security Cheat Sheet*](../fuentes/owasp/WebSocket_Security.md) de OWASP.

- Los mensajes son JSON `{type, data}`, en camelCase como la API.
- El valor de `type` va en snake_case, como los valores de un enum.
- Al perder la conexión, el cliente reconecta con espera exponencial y jitter, con hasta 30 segundos entre intentos, y vuelve a pedir el estado por REST. Lo que se envió mientras estaba desconectado no se repite.
- Un cliente se conecta solo por `wss://` ([WebSocket Security, *Always Use WSS (WebSocket Secure)*](../fuentes/owasp/WebSocket_Security.md)).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Una variable `RELEASE_<PIEZA>_<PLATAFORMA>`, con `true` o `false`, por cada pieza que se publica y cada una de sus plataformas, y ninguna de otra | `scripts/verificar.py --repo --variables`, en el job `canone` de CI |
| El contraste de los roles de `brand/tokens/` | `scripts/tokens.py --check` |
| Las partes de DTCG que sigue `brand/tokens/` | `scripts/tokens.py --check` |
| Los dos modificadores, el nombre y el grupo de cada tema, y dos temas distintos | `scripts/tokens.py --check` |
| Todos los roles en cada modo, y de cada custom color, el nombre, los cuatro roles y que esté en todos los temas y los modos | `scripts/tokens.py --check` |
| Lo generado, al día con `brand/tokens/` | `scripts/tokens.py --check` |
| problem+json en una ruta que no existe y en un error de validación | `test_unknown_route_is_a_problem` y `test_validation_error_points_to_the_field`, del servidor |
| La URI de cada tipo propio responde HTML con su `title` | `test_problem_types_are_documented`, del servidor |
| El `traceId` en el problem+json de una ruta que no existe | `test_unknown_route_is_a_problem`, del servidor |
| El servidor rechaza un cuerpo JSON con un nombre repetido, un número fuera de un `double`, un sustituto suelto, un no-carácter, otra codificación que UTF-8 o un nivel superior que no es objeto ni arreglo | `test_body_that_is_not_ijson`, `test_body_that_is_ijson_or_not_json` y `test_repeated_member_is_a_validation_error`, del servidor |
| Un cuerpo que no es JSON responde 400 | `test_body_that_is_not_json_is_a_bad_request`, del servidor |
| Una versión menor que la mínima, o mal formada, recibe un 400 de tipo `client-outdated` | `test_outdated_client_is_rejected`, del servidor |
| Un `pageToken` ilegible o con otros parámetros que los de su petición responde 422 con `parameter` en `pageToken` | `test_invalid_page_token_points_to_the_parameter`, del servidor |
