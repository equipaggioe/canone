# ADR-0238 · Los avisos llegan por push, y el servidor envía el Web Push sin seguir ni leer la respuesta

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Alcance:** `autenticacion.md`, `transversal.md`, `fastapi.md`, `sveltekit.md`, `stack.md` y `plantilla/server/`

## Contexto

Las páginas decían con qué se envía el push y a quién pertenecen el FID y la suscripción, sin rutas,
tablas ni qué producto lo lleva. Se comprobó, con firebase-admin 7.8.0, pywebpush 2.5.0, py-vapid
1.9.6 y aiohttp 3.14.5:

- `webpush_async` sigue redirecciones. Con el resolver que pedía la página, un endpoint que responde
  307 hacia `http://127.0.0.1` llevó al servidor a esa dirección: aiohttp no pasa por el resolver una
  IP escrita en la URL, tampoco en la redirección.
- `webpush_async` lee el cuerpo entero y lo descomprime: una respuesta gzip que se expande a 200 MB
  le sumó 396 MB al proceso.
- Con `socket_factory`, ninguna de ocho formas de escribir una dirección de la máquina o de los
  metadatos llegó a conectarse: cuatro las rechazó él, dos aiohttp y dos py-vapid. Un host público, sí.
- `send_each_async` renueva el token de Google con una llamada síncrona: con un servidor de tokens
  que tarda 3 s y responde 503, el bucle de eventos se detuvo 11,9 s, y el plazo de 5 s no lo cortó.
  Con `get_access_token` en un hilo, 0,1 s.
- Un 401 de FCM renueva el token dos veces por mensaje, también síncrono: con 3 mensajes y un
  servidor de tokens que tarda 3 s, 18,1 s de envío, con el bucle detenido hasta 9 s seguidos. FCM lo
  responde también cuando falta la clave de APNs o no vale.
- El aviso enviado por el código de la plantilla llegó a Chrome, a Firefox y a Edge, y se mostró.
- Mozilla responde 404 y FCM 410 a una suscripción que no existe. A un envío firmado con otra clave,
  FCM responde 403, y Mozilla y Microsoft, 401. Con la suscripción anterior, `subscribe()` con otra
  clave falla con `InvalidStateError` en los tres navegadores, y después de `unsubscribe()` funciona.
- FCM manda al canal del manifiesto el mensaje que nombra uno que la app no creó.
- La plantilla ocupa 135 MB, y 14 son de firebase-admin, aiohttp y pywebpush.

## Decisión

1. El FID y la suscripción web son dos tablas que amplían la sesión.
2. Lo que tenía otra sesión pasa a la que lo registra.
3. El push llega a las apps y a la web, a todas las sesiones vigentes, también a la que hizo el
   cambio. Las de una cuenta que se borra o se deshabilita se leen antes de cerrarlas.
4. El repositorio declara en `PUSH` por dónde envía.
5. La clave pública de VAPID sale de la privada, y la web la pide por la API.
6. El push abre `/account` y va por el canal `security` de Android.
7. El push lleva también el texto del correo.
8. `firebase_credentials` y `vapid_key` son obligatorias siempre, y sin FCM la primera es `{}`.
9. No hay rutas para borrar el FID ni la suscripción, y la sesión de la otra forma recibe 403.
10. El Web Push sale con aiohttp directo: `socket_factory` rechaza las direcciones no globales, y no
    se siguen redirecciones, no se lee el cuerpo ni se guardan cookies.
11. El token de Google se renueva en un hilo, y los push salen a la vez y esperan a lo sumo 5
    segundos.
12. La credencial de Google no se renueva durante el envío, y su token es solo para FCM: un 401 es la
    respuesta de su mensaje.
13. La web que encuentra otra clave de VAPID en el servidor se da de baja y se suscribe de nuevo.

## Consecuencias

- Cada app de Android crea el canal `security`, y cada cliente tiene la pantalla `/account`.
- El aviso por push también dice qué hacer y a quién escribir, como pide NIST SP 800-63B-4 §4.6 para
  cada dirección.
- Después de cambiar `vapid_key`, un navegador no recibe push hasta que el usuario abre la web. El
  correo le sigue llegando.
- Un mensaje que recibe 401 sale tres veces con el mismo token: el SDK reintenta.
- Un producto sin FCM carga igual firebase-admin.
- No se envió a Safari, ni por FCM a un dispositivo: pide la cuenta de servicio de un proyecto.

## Descartado

- **Columnas en `account_session`.** Los campos de la suscripción existen todos o ninguno, y pedirían
  un `CHECK` más por cada forma.
- **Solo el título en el push.** NIST pide las instrucciones y el contacto en cada aviso.
- **Campos de `Settings` solo si `PUSH` los usa.** Cada producto editaría `config.py` y el servicio
  que los lee; `sms_hashes` ya queda en `{}` sin SMS.
- **`DELETE` del FID y de la suscripción.** Cerrar sesión los borra, y darse de baja en el dispositivo
  hace que el servicio responda `UNREGISTERED`, 404 o 410. La ruta dejaría que quien roba una sesión
  callara sus avisos.
- **409 a la sesión de la otra forma.** RFC 9110 lo reserva para un conflicto que el cliente puede
  resolver, y una sesión no cambia de forma.
- **El resolver con una lista de redirecciones permitidas.** Ningún servicio de push redirige un envío.
- **Una credencial que falla al renovarse durante el envío.** El 401 de un mensaje dejaría a los demás
  sin respuesta, y los `UNREGISTERED` sin borrar.
- **`send_each` en un hilo.** Ocuparía hilos del proceso mientras Google no responde, sin un plazo que los corte.
