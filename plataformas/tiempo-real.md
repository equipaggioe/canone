# Tiempo real: WebSocket, llamadas y TURN

Cómo se hace lo que no cabe en un request.

## WebSocket

- Bajo `/ws`, autenticado igual que el resto de la API.
- Cada mensaje lleva un campo de tipo, y el payload es un schema de Pydantic serializado igual que
  una respuesta HTTP: camelCase y el mismo formato de fecha.
- El código del socket vive en `app/ws/`, y llama a los mismos servicios que los routers. No hay una
  segunda implementación de la lógica para el canal en vivo.
- Un error en el socket se manda con la misma forma que el sobre de error HTTP.

## Varios procesos

Un registro de conexiones en memoria **solo sirve con un proceso**. Con varios workers, cada uno ve
sus propias conexiones y los mensajes no cruzan.

Con varios workers hace falta pub/sub en Redis, y entonces **Redis es obligatorio**: arrancar con
más de un worker sin Redis tiene que fallar al arranque. Importar Redis «solo si `REDIS_URL` está
definida» es un degradado silencioso —las conexiones se parten y nada falla—, que es justo lo que
`principios.md` prohíbe.

## Llamadas de voz y video

WebRTC, con los servidores ICE entregados por la API:

- **STUN público además de TURN, no en su lugar.** STUN alcanza para la mayoría de las redes y no
  cuesta nada mantenerlo.
- **TURN propio con credenciales efímeras.** El endpoint las firma con el secreto compartido y
  tienen vencimiento; no se reparte una credencial fija.
- El secreto, el puerto y el realm de coturn son **datos del despliegue**, no valores que el backend
  elija: anuncia en sus URLs `turn:` exactamente lo que quedó en el servidor — ver
  [despliegue.md](despliegue.md). Si los genera por su cuenta, el servidor exige un secreto que el
  backend ya no tiene y las llamadas se caen sin que nada lo diga.

## Trabajo pesado en el mismo proceso

El proceso que sirve los WebSocket es el mismo que atiende HTTP. Cualquier llamada bloqueante —un
SDK síncrono, una inferencia, un archivo grande— va en `asyncio.to_thread`: si no, congela también
el chat en vivo.
