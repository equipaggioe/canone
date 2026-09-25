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

## Qué es y qué no es una página

Una página dice **cómo se hace**. No dice qué repositorio la usa hoy ni cuándo elegir una plataforma
sobre otra: lo primero es un dato que envejece, lo segundo se decide producto por producto.

Se agrega una página cuando la tecnología se estrena en algún repositorio. Se escribe desde la
documentación oficial más reciente, o desde la mejor práctica establecida donde no la hay, y nunca
desde el código existente — ver
[ADR-0014](../adr/0014-una-pagina-se-escribe-desde-la-recomendacion-oficial.md). Lo que un
repositorio hace distinto va a [homologacion.md](../homologacion.md), que es el documento de trabajo
y se borra cuando la homologación termine.

## Lo que cruza plataformas

| Qué | Regla |
|---|---|
| **El sobre de error** | Lo define [fastapi.md](fastapi.md) y cada cliente lo traduce a un error tipado con los mismos campos. `errorCode` es el contrato; `detail` es texto para mostrar |
| **Los tokens de diseño** | Un solo módulo por cliente, sin colores ni tamaños literales fuera de él. Si el producto tiene superficie web, es la misma paleta y el archivo dice de cuál es espejo |
| **Refrescar la sesión** | Ante un 401, una sola vez y un solo reintento. Nunca un bucle silencioso |
| **Entrega al exterior** | Primero la evidencia en la base, después el envío best-effort. Un fallo de entrega no tumba la operación |
