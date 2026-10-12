# ADR-0044 · El bloqueo cuenta los intentos en una ventana, y el titular lo ve en la app

- **Estado:** Aceptada
- **Fecha:** 2026-10-11
- **Alcance:** las secciones «Autenticación» y «Sesión» de
  [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

El [ADR-0038](0038-el-login-sigue-a-owasp-y-el-conteo-de-intentos-fallidos-vive-en-valkey.md)
contaba los intentos fallidos sin ventana de tiempo, y avisaba de cada bloqueo por los medios que
registró el titular. Este ADR lo reemplaza: mantiene sus demás puntos y cambia esos dos.

## Decisión

1. El login sigue el *Authentication Cheat Sheet* y el *Forgot Password Cheat Sheet* de OWASP,
   también en el bloqueo por intentos fallidos.
2. El conteo de intentos fallidos vive en Valkey.
3. Una cuenta con 10 intentos fallidos en 15 minutos queda bloqueada 30 minutos, y con el segundo
   bloqueo queda bloqueada para siempre.
4. El titular ve en la app cada intento fallido y cada bloqueo de su cuenta.
5. El registro responde 409 si la cuenta ya existe, y una IP que recibe 10 respuestas 409 en 15
   minutos queda bloqueada 30 minutos.
6. Usar un token de refresco ya rotado borra la sesión de ese dispositivo, avisa al titular por los
   medios que registró y cuenta como un intento fallido de la cuenta.
7. Cambiar la contraseña cierra las demás sesiones y renueva los tokens de la sesión que hizo el
   cambio; restablecerla cierra todas.

## Consecuencias

- Reemplaza el punto 3 del
  [ADR-0008](0008-un-sobre-unico-de-evento-y-el-catalogo-es-del-repositorio.md): los intentos de
  acceso no van a la tabla `login_attempt`. Lo que se investiga después va al registro de eventos,
  que OWASP exige para cada fallo y cada bloqueo.
- Si Valkey pierde sus datos, los contadores vuelven a cero y el atacante gana intentos. El
  registro de eventos no se pierde.
- Quien prueba menos de 10 contraseñas cada 15 minutos nunca llega al bloqueo.
- El aviso de un token de refresco ya rotado sigue yendo por los medios que registró el titular.
  Se revisa con la sección «Sesión». Está en el punto 6.

## Descartado

- **Contar los intentos sin ventana de tiempo**, como el ADR-0038. Contradecía la ventana que OWASP
  cuenta entre los valores del bloqueo.
- **Avisar por correo o por SMS.** Son los canales más comunes del phishing, y cada SMS cuesta.
- **Contar los intentos en una tabla.** Cada intento escribe una fila, y hace falta una tarea que
  borre las viejas. En Valkey el contador es una sola llave por cuenta, y ahí ya viven los
  contadores del límite de tasa.
- **Responder igual en el registro exista o no la cuenta, y avisar por correo.** Quien ya tiene
  cuenta no se entera al registrarse.
- **Revocar todas las sesiones del usuario al reusar un refresco.** El token robado compromete la
  sesión de ese dispositivo; el aviso al titular y el conteo como intento fallido cubren el resto.
- **Cerrar también la sesión que cambia la contraseña.** Quien la cambia ya demostró quién es.
