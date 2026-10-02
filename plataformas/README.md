# Plataformas

Una página por tecnología, o por contrato que cruza varias piezas, como la seguridad o el tiempo
real. **Se lee la de lo que el repositorio use**; las demás no aplican.

| Página | Cubre |
|---|---|
| [python.md](python.md) | Versión, uv, estilo, tipos, paquetes, logging, fechas, async, pruebas, auditoría de dependencias |
| [fastapi.md](fastapi.md) | Layout, configuración, SQLAlchemy async, migraciones, errores RFC 9457, trazas, fechas, montos, paginación, OpenAPI, pruebas |
| [postgres.md](postgres.md) | Clave primaria, tipos, borrado, nombres, índices, geografía |
| [seguridad.md](seguridad.md) | Contraseñas, restablecimiento, tokens y sesión, segundo factor, qué guarda cada cliente, límite de tasa, permisos, cabeceras |
| [tiempo-real.md](tiempo-real.md) | WebSocket, varios procesos con Redis, llamadas con WebRTC y coturn |
| [notificaciones.md](notificaciones.md) | Push por FCM y Web Push, correo por SES |
| [pagos.md](pagos.md) | Stripe Checkout, webhooks, montos |
| [i18n.md](i18n.md) | Idioma base, códigos en la base y catálogos por cliente |
| [accesibilidad.md](accesibilidad.md) | WCAG 2.2 y cómo lo cumple cada cliente |
| [archivos.md](archivos.md) | Subida, almacenamiento y borrado de los archivos de los usuarios |
| [mapas.md](mapas.md) | Teselas, búsqueda de direcciones, atribución y biblioteca por cliente |
| [sveltekit.md](sveltekit.md) | Proyecto, carga de datos, cliente generado, adaptador estático, estado, UnoCSS, pruebas |
| [flutter.md](flutter.md) | Estilo, analizador, arquitectura, modelos, estado, tema, almacenamiento |
| [android.md](android.md) | Gradle, estilo, arquitectura, red, Compose, tema, almacenamiento, pruebas |
| [flet.md](flet.md) | Layout, tema, red, almacenamiento, publicación |
| [qt.md](qt.md) | Layout, API de PySide6, `@override`, interfaz en código, `QSettings`, Fusion y hoja de estilo, red, pruebas, empaquetado |
| [despliegue.md](despliegue.md) | Caddy, servicios de systemd, configuración, datos, registros, respaldos |

## Qué es una página

Un catálogo de convenciones de una tecnología o de un contrato entre piezas. Una convención sirve para una de tres cosas:

- **Que todos los repositorios se lean igual:** el mismo layout y los mismos nombres.
- **Que cada elección se tome una sola vez:** la tecnología, la biblioteca, la versión y la
  configuración.
- **Que las piezas de un sistema se entiendan:** el servidor y sus clientes cumplen el mismo
  contrato, como el sobre de error, los nombres en el cable o la sesión.

Una regla que no sirve para ninguna de las tres no va. Una convención vale aunque ninguna
herramienta la haga cumplir.

- Dice qué se usa y cómo queda. No es un procedimiento ni un tutorial.
- Cada regla dice lo que se hace. Lo que la página no dice lo decide el estándar.
- Sale de la recomendación oficial más reciente. Una regla propia va solo donde lo oficial tiene
  una deficiencia, no existe o deja la elección abierta.
- Es oficial el texto normativo de un estándar (MUST, SHOULD o RECOMMENDED) y la recomendación
  escrita en la documentación de la tecnología. Nada más: ni el código de sus ejemplos, ni sus
  proyectos de muestra, ni lo que hace la comunidad. Una regla que sale de ahí es propia.
- Citar un estándar adopta sus recomendaciones: lo que recomienda se hace como si fuera
  obligatorio, y no se escribe.
- El comportamiento por defecto de una herramienta no es una recomendación. Si la página no dice
  nada, rige; cambiarlo es oficial solo si la documentación lo pide.
- Cada sección nombra los estándares que sigue y enlaza su texto en [estandares/](../estandares/).
  Lo que el estándar dice no se escribe.
- La excepción es el layout: se dibuja completo, como árbol, aunque repita partes del estándar. El
  árbol es la convención misma, y a pedazos no se lee.
- Sobre el estándar, la página escribe solo tres cosas:
  - La opción que elige donde el estándar deja varias.
  - Lo que contradice o endurece del estándar. Endurecer es volver obligatorio lo que el estándar
    recomienda «cuando sea posible» o deja como preferencia.
  - Lo que ningún estándar cubre.
- La tabla «Cómo se hace cumplir» nombra en su primera columna el estándar o su sección, o una
  regla que la página ya escribió. Nunca redacta una regla nueva para llenar la fila.
- Nombra los archivos de `plantilla/` que salen de ella.
- Ni el código de los repositorios, ni lo que la página ya dice, ni los ADR son fuente. Una página
  se escribe de cero desde sus estándares, nunca corrigiendo la versión anterior. Lo que un
  repositorio hace distinto va a [homologacion.md](../homologacion.md), que es el documento de
  trabajo y se borra cuando la homologación termine.
- Sin comentarios ni explicaciones, salvo dos, cada una en una frase corta: por qué la página
  contradice o endurece el estándar, y cómo ayuda una elección que no es trivial. Una regla trivial,
  como un color o el largo de línea, no lleva frase: su razón es una preferencia. Vale también para
  los comentarios de `plantilla/`.
- Hereda de su página madre y no repite nada de ella: `fastapi.md`, `flet.md` y `qt.md` heredan de
  `python.md`.
- No dice qué repositorio la usa ni cuándo elegir una plataforma sobre otra.

Se agrega una página cuando la tecnología o el contrato se estrena en algún repositorio.

El porqué, en el [ADR-0018](../adr/0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md).

## Lo que cruza plataformas

| Qué | Regla |
|---|---|
| **El sobre de error** | RFC 9457, definido en [fastapi.md](fastapi.md). Cada cliente lo traduce a un error tipado con los mismos campos. `type` es el contrato; `detail` es texto para mostrar |
| **Nombres en el cable** | La API habla en camelCase, como fija [fastapi.md](fastapi.md). Cada cliente usa la convención de su lenguaje (`snake_case` en Python, camelCase en Dart y TypeScript) y convierte en un solo punto: su cliente de la API |
| **Los tokens de diseño** | Un solo módulo por cliente, sin colores ni tamaños literales fuera de él. Si el producto tiene superficie web, es la misma paleta y el archivo dice de cuál es espejo |
| **Montos** | Viajan como `{amount, currency}`, con el monto en cadena, como fija [fastapi.md](fastapi.md). Cada cliente lo conserva como cadena o como el decimal de su lenguaje, nunca como `double`, y no calcula con él: los totales, impuestos y descuentos llegan calculados del servidor. Así ningún cliente necesita una biblioteca decimal |
| **Versión mínima de cliente** | Cada cliente instalable manda `User-Agent: <pieza>/<versión>` desde su primera versión publicada, como fija [fastapi.md](fastapi.md). Ante `client-outdated`, pide actualizar la app |
| **Refrescar la sesión** | Ante un 401, una sola vez y un solo reintento. Nunca un bucle silencioso |
| **Entrega al exterior** | Primero la evidencia en la base, después el envío best-effort. Un fallo de entrega no tumba la operación |
