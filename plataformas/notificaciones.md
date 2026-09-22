# Notificaciones: push y correo

Cómo sale un aviso del servidor.

## La regla que vale para todas

**Primero la evidencia, después la entrega.**

1. Lo que hay que conservar —la notificación, el registro del aviso— se escribe en la base, dentro
   de la transacción de quien llama.
2. La entrega al mundo exterior ocurre **después** y es best-effort.
3. **Un fallo de entrega nunca tumba la operación que lo originó.** Si el proveedor está caído, el
   registro se completa igual y se registra el error.

**Un SDK bloqueante va en `asyncio.to_thread`.** Llamarlo directo desde una corrutina congela el
event loop, y con él los WebSocket del mismo proceso.

## Push

| Destino | Mecanismo |
|---|---|
| App nativa | FCM (`firebase-admin`) |
| Navegador y PWA | Web Push (`pywebpush`) |

**El destino decide, no el repositorio.** Un producto con app y PWA necesita los dos, y el servicio
elige por el tipo de token registrado, no por configuración.

- Sin las credenciales del proveedor (claves VAPID, cuenta de servicio) **no se intenta el envío**:
  no hay con qué firmar. Es una condición de arranque, no una rama silenciosa en cada envío.
- **Una suscripción caducada se desactiva, no se borra.** El proveedor devuelve 404 o 410 cuando el
  navegador la invalidó o la app se desinstaló; reintentar sobre un endpoint muerto es trabajo
  perdido en cada notificación futura, y borrar la fila pierde el historial de qué dispositivos
  hubo. `is_active = false` dice «no la uses» sin perder el rastro.
- Un contador de fallos en memoria sirve para notar que los push dejaron de salir; no es una métrica
  histórica y se reinicia con el proceso.

## Correo transaccional

- El proveedor se aísla en un servicio (`services/email.py`); los routers no lo conocen.
- **Sin credencial no se envía: se registra el enlace en el log.** En desarrollo todavía no hay
  dominio verificado con SPF y DKIM, y un flujo de registro que revienta porque falta una credencial
  de terceros bloquea toda la verificación. El enlace en el log alcanza para probar el flujo.
- El SDK es síncrono: va en `asyncio.to_thread`.

## Contenido

**Nada se guarda traducido.** La fila guarda el tipo del aviso y sus datos; el cliente renderiza en
el idioma del usuario — ver [i18n.md](i18n.md).
