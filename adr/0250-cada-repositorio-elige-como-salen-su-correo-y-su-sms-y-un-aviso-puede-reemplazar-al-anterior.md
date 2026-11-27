# ADR-0250 · Cada repositorio elige cómo salen su correo y su SMS, y un aviso puede reemplazar al anterior

- **Estado:** Aceptada el 2026-11-26 por el desarrollador: separar el transporte del correo y del
  SMS en un archivo que cada repositorio elige, y que un push lleve un `tag` opcional.
- **Fecha:** 2026-11-26
- **Alcance:** `fastapi.md`, `transversal.md`, `autenticacion.md` y `plantilla/server/`

## Contexto

`services/messages.py` decidía a la vez cuándo sale un correo o un SMS (después del commit, sin
hacer fallar la petición) y cómo (por HTTP a la API de Equipaggio). Equipaggio es esa API y pone
sus mensajes en su propia cola, así que reescribía `messages.py`, `test_messages.py` y
`test_registration.py`, y declaraba tres desviaciones: cada cambio de canone en ellos se pasaba a
mano.

Las alertas de un monitor avisan el estado nuevo de una misma cosa, y sin `tag` se apilan en la
bandeja. El mensaje declarativo de la Push API, FCM y APNs tienen un campo que reemplaza la
notificación con el mismo valor: `tag`, `AndroidNotification.tag` y `apns-collapse-id`.

## Decisión

Las reglas están en `fastapi.md`, «Correo y SMS» y «Push», y en `transversal.md`, «Push»; aquí va
el porqué.

1. `services/transport.py` tiene `email` y `sms`, y cada repositorio lo elige, como `push.py`: la
   plantilla manda a la API de Equipaggio. `tests/test_transport.py` prueba ese transporte.
2. `services/messages.py` queda con `later` y `flush`, igual en todo repositorio. `flush` atrapa
   cualquier error, no solo los de HTTP: un transporte puede fallar de otra forma, y la petición ya
   se confirmó.
3. `test_registration.py` deja de comprobar el host y la clave del `PUT`, que pasan a
   `test_transport.py`.
4. `Content` lleva un `tag` opcional, que va en el mensaje declarativo, en `AndroidNotification` y
   en `apns-collapse-id`. Los avisos de seguridad no lo llevan: cada uno cuenta algo aparte.

## Consecuencias

- Un repositorio con cuentas copia `transport.py` y `test_transport.py` como punto de partida.
- Equipaggio deja de apartarse de los tres archivos.

## Descartado

- **Que `messages.py` reciba el transporte por configuración:** otra indirección para lo que ya
  resuelve un archivo que el repositorio elige.
