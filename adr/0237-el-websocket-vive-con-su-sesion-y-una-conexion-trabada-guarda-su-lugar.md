# ADR-0237 · El WebSocket vive con su sesión, y una conexión trabada guarda su lugar

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Alcance:** `autenticacion.md`, `transversal.md`, `fastapi.md`, `despliegue.md` y
  `plantilla/server/`

## Contexto

Las páginas decían cómo se autentica el WebSocket, que cerrar una sesión cierra sus conexiones y sus
límites, sin rutas, códigos ni mecanismo. Se comprobó, con FastAPI 0.165.0, Uvicorn 0.54.0,
valkey-py 6.2.0 y el Caddy 2.6.2 de Debian 13:

- Una dependencia con `Request` responde 500 en un handshake, y con `HTTPConnection` funciona. Una
  excepción antes de aceptar sale por su manejador, con su estado y su problem+json.
- Con 20 conexiones abiertas, 20 dependencias `scope="function"` siguen tomadas.
- Uvicorn cierra a los 40 s la conexión que no responde el ping, también detrás de Caddy. A la que
  dejó de leer con datos por entregar no la cierra en 120 s, ni Caddy: `keepalive_timeout` llama a
  `transport.close()`, que espera vaciar el buffer. La app tampoco recibe `websocket.disconnect`.
- valkey-py no reconecta una suscripción perdida: la lectura lanza `ConnectionError`. `listen()`
  también la da por perdida al pasar el `socket_timeout` del cliente sin mensajes: en la prueba, una
  conexión en silencio se cerró antes de 15 s. `get_message` con su propio plazo no la pierde.
- Con dos procesos de Uvicorn, uno detrás de Caddy, cerrar sesión en uno cierra con 4401 la conexión
  del otro. Una conexión trabada siguió ocupando su lugar 75 s y lo soltó al terminar su TCP.
- Si el proceso de Uvicorn muere, Caddy 2.6.2 no cierra la conexión con un cliente que no lee: seguía
  abierta 90 s después.
- Uvicorn 0.54.0 nunca marca como terminado un handshake que se rechaza con su respuesta, y por eso
  escribe un `ERROR` en cada uno (`run_asgi`, en `websockets_sansio_impl.py`). Era la última versión
  el 2026-11-24.
- openapi-typescript 7.13.0, datamodel-code-generator 0.100.0, openapi-generator 7.27.0 y
  swagger_parser 2.3.0 generan los esquemas que ninguna ruta usa. openapi-generator funde una unión
  de los dos problemas en una clase con `errors` obligatorio: con un solo esquema, `MessageProblem`,
  los cuatro dejan `errors` opcional.

## Decisión

1. El WebSocket es `GET /api/websocket`. Su rechazo es el problem+json de la API, salvo el de la
   sesión, que acepta y cierra con 4401.
2. Las conexiones de un usuario se cuentan por un lugar en Valkey que vence y se renueva. La número
   11 responde 429.
3. Una app manda su token nuevo en un mensaje `access_token`. Su conexión vence con el último token
   que presentó; la de la web, a los 30 días del último uso de la sesión.
4. El cierre se publica después del commit. Un proceso que pierde su suscripción cierra sus
   conexiones con 1012, y los clientes se autentican de nuevo.
5. Un mensaje que no se acepta recibe uno de `type` `error`, con su problem+json, y deja su evento.
   Uno binario cierra con 1003.
6. Una conexión con 100 mensajes por enviar se cierra con 1013.
7. Solo los fallos dejan evento.
8. La plantilla trae el reenvío, y cada producto agrega sus tipos de mensaje.
9. Una conexión guarda su lugar hasta que termina su TCP, aunque ya no sirva.
10. Los esquemas de los mensajes van en `components` del `openapi.json`.

## Consecuencias

- Un usuario acumula a lo sumo 10 conexiones trabadas mientras vive el proceso: ocupan sus propios
  lugares. Un reinicio del servidor libera los lugares, y Caddy conserva las suyas.
- El cierre no espera la siguiente revisión, y una publicación perdida se corrige al reconectar.
- Uvicorn escribe en su log `ASGI callable returned without completing handshake` en cada handshake
  rechazado, aunque el rechazo llega bien.
- Cada proceso tiene una sola suscripción, que abre con su primera conexión.

## Descartado

- **Un contador de conexiones que sube y baja.** Un proceso que muere no lo baja.
- **Cerrar la conexión de una app al refrescar.** La cortaría antes de que llegue el token nuevo.
- **La purga diaria para vencer la conexión de la web.** Llega hasta un día tarde.
- **Cerrar con un código ante un mensaje que no valida.** El cliente no sabría qué campo falló.
- **Descartar los mensajes más viejos de una conexión lenta.** El cliente no sabría qué perdió.
- **Un plazo por envío, además de la cola.** La cola ya limita la memoria, y una conexión lenta con
  poco por enviar se recupera sola.
- **Reemplazar el protocolo de Uvicorn para abortar el TCP.** Depende de su código interno, y la
  conexión de Caddy con el cliente seguiría trabada.
- **Registrar cada apertura y cada cierre**, como sugiere OWASP: nada los consulta, y la sesión ya
  deja los suyos.
