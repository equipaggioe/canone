# Tiempo real

Lo que no cabe en un request: WebSocket y llamadas.

## WebSocket

Estándares: [RFC 6455](../estandares/rfc/rfc6455.txt),
[*WebSockets*](../estandares/fastapi/websockets.md) de FastAPI y
[*WebSocket Security Cheat Sheet*](../estandares/owasp/WebSocket_Security.md) de OWASP.

- El cliente se autentica mandando el token de acceso en el primer mensaje. Si no llega en 5
  segundos, el servidor cierra con 1008. De las dos formas que da OWASP, el mensaje no deja el
  token en los registros de acceso.
- Al refrescar la sesión, el cliente manda el token nuevo por la misma conexión. Cuando vence el
  que tiene, el servidor cierra con 1008.
- Cerrar sesión cierra sus conexiones en todos los procesos.
- Los mensajes son JSON `{type, data}`, en camelCase como el resto del cable.
- Al perder la conexión, el cliente reconecta con espera exponencial y jitter, y vuelve a pedir el
  estado por REST. Lo que se envió mientras estaba desconectado no se repite.

## Varios procesos

Estándar: [*Redis Pub/sub*](../estandares/redis/pubsub.md).

- Cada proceso se suscribe a Redis y reenvía a sus conexiones, con un canal por usuario. Pub/sub
  entrega a lo sumo una vez; por eso el cliente pide el estado por REST al reconectar.

## Llamadas de voz y video

Estándares: [WebRTC](../estandares/w3c/webrtc.html) de W3C,
[RFC 8489](../estandares/rfc/rfc8489.txt) (STUN), [RFC 8656](../estandares/rfc/rfc8656.txt)
(TURN) y la [documentación de coturn](../estandares/coturn/README.turnserver).

- La señalización va por el WebSocket de la app.
- coturn usa credenciales temporales (`use-auth-secret`), que el servidor entrega por la API. Los
  clientes no guardan una contraseña fija de TURN.
- coturn escucha en 3478 (UDP y TCP) y en 5349 (TLS), y niega relevar hacia direcciones privadas con
  `denied-peer-ip`. TURN no sirve de puente a la red interna.
