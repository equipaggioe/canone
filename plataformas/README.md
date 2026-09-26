# Plataformas

Una página por tecnología. **Se lee la de lo que el repositorio use**; las demás no aplican.

| Página | Cubre |
|---|---|
| [python.md](python.md) | Versión, dependencias, PEP 8 con `ruff format`, PEP 257, imports absolutos, `__init__.py`, tipos, lint base |
| [fastapi.md](fastapi.md) | Layout de `server/`, capas, settings, sesión de base, el sobre de error, paginación, OpenAPI, tests, lint |
| [postgres.md](postgres.md) | Tipos, alias de columna, enums, geografía, nombres, idempotencia, migraciones, borrado |
| [seguridad.md](seguridad.md) | Contraseñas, tipos de token, TOTP, qué guarda cada cliente, límite de tasa, permisos |
| [tiempo-real.md](tiempo-real.md) | WebSocket, varios procesos y Redis, WebRTC, STUN y TURN |
| [notificaciones.md](notificaciones.md) | Push (FCM y Web Push) y correo transaccional |
| [pagos.md](pagos.md) | Aislamiento del proveedor, capacidades, idempotencia de webhooks |
| [i18n.md](i18n.md) | Catálogos por plataforma y qué no se guarda traducido |
| [sveltekit.md](sveltekit.md) | Adaptador, layout de `src/lib`, UnoCSS, runes, cliente de la API, tests |
| [flutter.md](flutter.md) | Layout de `lib/`, tokens, estado, red, almacenamiento, analizador, mapas |
| [flet.md](flet.md) | Layout de `src/`, `core/`, tokens, cliente de la API, sesión, empaquetado |
| [qt.md](qt.md) | Layout, API de PySide6, archivos `.ui`, padres, layouts, diálogos, model/view, `QSettings`, Fusion y hoja de estilos global, red e hilos, tests con `pytest-qt`, empaquetado con `pyside6-deploy` |
| [despliegue.md](despliegue.md) | Cómo tiene que quedar el servidor: qué se expone, los procesos, los datos, la configuración |

## Qué es una página

Un catálogo de convenciones de una tecnología. Una convención sirve para una de tres cosas:

- **Que todos los repositorios se lean igual:** el mismo layout y los mismos nombres.
- **Que cada elección se tome una sola vez:** la tecnología, la biblioteca, la versión y la
  configuración.
- **Que las piezas de un sistema se entiendan:** el servidor y sus clientes cumplen el mismo
  contrato, como el sobre de error, los nombres en el cable o la sesión.

Una regla que no sirve para ninguna de las tres no va. Una convención vale aunque ninguna
herramienta la haga cumplir.

- Dice qué se usa y cómo queda. No es un procedimiento ni un tutorial.
- Sale de la recomendación oficial más reciente. Una regla propia va solo donde lo oficial tiene
  una deficiencia, no existe o deja la elección abierta.
- Es oficial el texto normativo de un estándar (MUST, SHOULD o RECOMMENDED) y la recomendación
  escrita en la documentación de la tecnología. Nada más: ni el código de sus ejemplos, ni sus
  proyectos de muestra, ni lo que hace la comunidad. Una regla que sale de ahí es propia.
- El comportamiento por defecto de una herramienta no es una recomendación. Si la página no dice
  nada, rige; cambiarlo es oficial solo si la documentación lo pide.
- Cada sección nombra el estándar del que sale.
- Ni el código de los repositorios ni lo que la página ya dice son fuente. Lo que un repositorio
  hace distinto va a [homologacion.md](../homologacion.md), que es el documento de trabajo y se
  borra cuando la homologación termine.
- Sin comentarios ni explicaciones, salvo dos, cada una en una frase corta: por qué una regla se
  aparta de la recomendación oficial, y cómo ayuda una elección que no es trivial. Una elección
  trivial, como un color, no lleva frase. Vale también para los comentarios de `plantilla/`.
- Hereda de su página madre y no repite nada de ella: `fastapi.md`, `flet.md` y `qt.md` heredan de
  `python.md`.
- No dice qué repositorio la usa ni cuándo elegir una plataforma sobre otra.

Se agrega una página cuando la tecnología se estrena en algún repositorio.

El porqué, en el [ADR-0016](../adr/0016-una-pagina-es-un-catalogo-de-convenciones-que-sale-de-la-recomendacion-oficial.md).

## Lo que cruza plataformas

| Qué | Regla |
|---|---|
| **El sobre de error** | RFC 9457, definido en [fastapi.md](fastapi.md). Cada cliente lo traduce a un error tipado con los mismos campos. `type` es el contrato; `detail` es texto para mostrar |
| **Nombres en el cable** | La API habla en camelCase, como fija [fastapi.md](fastapi.md). Cada cliente usa la convención de su lenguaje (`snake_case` en Python, camelCase en Dart y TypeScript) y convierte en un solo punto: su cliente de la API |
| **Los tokens de diseño** | Un solo módulo por cliente, sin colores ni tamaños literales fuera de él. Si el producto tiene superficie web, es la misma paleta y el archivo dice de cuál es espejo |
| **Refrescar la sesión** | Ante un 401, una sola vez y un solo reintento. Nunca un bucle silencioso |
| **Entrega al exterior** | Primero la evidencia en la base, después el envío best-effort. Un fallo de entrega no tumba la operación |
