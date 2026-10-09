# ADR-0038 · El login sigue a OWASP, y el conteo de intentos fallidos vive en Valkey

- **Estado:** Aceptada
- **Fecha:** 2026-10-08
- **Alcance:** las secciones «Autenticación» y «Tokens» de
  [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

El [ADR-0009](0009-el-login-no-delata-cuentas-y-el-bloqueo-vive-en-la-base.md) fijó siete reglas
del login, y ninguna página las aplicaba. Revisadas contra las fuentes que cita fastapi.md, tres ya
las exige el *Authentication Cheat Sheet* de OWASP (el hash señuelo, un solo error y no guardar la
contraseña del intento), y las demás chocaban con la página o con OWASP.

## Decisión

1. El login sigue el *Authentication Cheat Sheet* y el *Forgot Password Cheat Sheet* de OWASP,
   también en el bloqueo por intentos fallidos.
2. El conteo de intentos fallidos vive en Valkey, y no vence con el tiempo.
3. El bloqueo llega con 10 intentos fallidos seguidos y dura 30 minutos, el tercero es permanente,
   y cada uno avisa al titular.
4. El registro responde 409 si la cuenta ya existe, y una IP que recibe 10 respuestas 409 en 15
   minutos queda bloqueada 30 minutos.
5. Usar un token de refresco ya rotado borra la sesión de ese dispositivo, avisa al titular por los
   medios que registró y cuenta como un intento fallido de la cuenta.
6. Cambiar la contraseña cierra las demás sesiones y renueva los tokens de la sesión que hizo el
   cambio; restablecerla cierra todas.

## Consecuencias

- Reemplaza el punto 3 del
  [ADR-0008](0008-un-sobre-unico-de-evento-y-el-catalogo-es-del-repositorio.md): los intentos de
  acceso ya no van a la tabla `login_attempt`. Lo que se investiga después va al registro de
  eventos, que OWASP exige para cada fallo y cada bloqueo.
- Si Valkey pierde sus datos, los contadores vuelven a cero y el atacante gana intentos. El
  registro de eventos no se pierde.
- El registro dice si una cuenta existe. Quien se registra se entera de que ya tiene cuenta, y
  quien busca cuentas desde una IP se topa con el bloqueo. Desde muchas IPs, no: ninguna fuente da
  números para detectarlo, y los de la IP son una elección propia.

## Descartado

- **Contar los intentos en una tabla.** Cada intento escribe una fila, y hace falta una tarea que
  borre las viejas. En Valkey el contador es una sola llave por cuenta, y ahí ya viven los
  contadores del límite de tasa.
- **Contar los intentos dentro de una ventana de tiempo**, como CIS y Microsoft. Quien prueba
  menos intentos que el umbral en cada ventana nunca llega al bloqueo, y prueba sin fin.
- **Deshabilitar el método tras 100 intentos fallidos**, como NIST SP 800-63B-4. Le deja al
  atacante cien intentos por cuenta. El bloqueo de OWASP no deja fuera al titular: lo levanta
  restableciendo la contraseña.
- **Responder igual en el registro exista o no la cuenta, y avisar por correo.** Quien ya tiene
  cuenta no se entera al registrarse.
- **Revocar todas las sesiones del usuario al reusar un refresco.** El token robado compromete la
  sesión de ese dispositivo; el aviso al titular y el conteo como intento fallido cubren el resto.
- **Cerrar también la sesión que cambia la contraseña.** Quien la cambia ya demostró quién es.
