# ADR-0009 · El login no delata cuentas por tiempo y el bloqueo vive en una tabla

- **Estado:** Reemplazada por [ADR-0038](0038-el-login-sigue-a-owasp-y-el-conteo-de-intentos-fallidos-vive-en-valkey.md)
- **Fecha:** 2026-09-23
- **Alcance:** `server/app/services/`, todos los repositorios con autenticación

## Contexto

`seguridad.md` dice cómo se guardan las contraseñas y los tokens, pero no dice cómo se comporta el
endpoint que los usa. Verificado leyendo el código el 2026-09-23:

| Repositorio | Bloqueo por fuerza bruta | El tiempo de respuesta delata si la cuenta existe |
|---|---|---|
| navetta | Ninguno | — |
| presenze | Ninguno | **Sí**: `if user is None` sale antes de verificar la contraseña |
| banditore | Ninguno | **Sí**: `user is None or not verify_password(...)` corta por la izquierda |
| vettore | En memoria del proceso | — |
| concordia | Sobre la tabla `login_attempt` | No: verifica contra un hash señuelo |

Tres de los cinco no tienen ninguna defensa contra probar contraseñas en serie. El de vettore no
sirve con más de una instancia, y su propio `core/rate_limit.py` lo documenta: cada proceso lleva su
conteo y el límite real es N veces el declarado. Un límite que se multiplica en silencio es peor
que no tenerlo, porque se cree que está.

El tiempo como canal es fácil de pasar por alto: argon2 cuesta ~100 ms a propósito, así que
responder de inmediato cuando el correo no existe mide la diferencia desde fuera aunque el mensaje
de error sea idéntico.

## Decisión

1. **Verificar siempre una contraseña, exista la cuenta o no.** El camino del identificador
   desconocido compara contra un hash señuelo calculado al arrancar. Sin esto, el mensaje de error
   uniforme no vale nada.
2. **Un solo error para todos los motivos del login**: identificador desconocido, contraseña mala,
   cuenta inactiva. El `errorCode` es el mismo; el motivo real va al registro de eventos, no a la
   respuesta.
3. **El bloqueo por fuerza bruta se calcula sobre `login_attempt`** (ADR-0008), con dos umbrales:
   por identificador y por IP, sobre una ventana de minutos. Nunca en memoria del proceso.
4. **Si la pertenencia al producto es dato sensible, el repositorio lo declara en un ADR propio** y
   entonces el alta y la recuperación también responden igual exista o no la cuenta, y el aviso al
   titular sale por correo. Esto **no** es universal: en un producto donde tener cuenta no
   compromete a nadie, un `409` al registrarse es mejor para quien se registra.
5. **La rotación del refresh detecta el reuso, y el reuso revoca todo lo del usuario.** Sin
   detección, rotar solo cambia el token que hay que copiar.
6. **Cambiar o restablecer la contraseña cierra todas las sesiones.** Quien restablece sospecha de
   un acceso ajeno; dejar viva la sesión del atacante vacía el gesto.
7. **El intento fallido no guarda la contraseña ni nada del cuerpo.** El identificador tecleado sí,
   porque es la señal de enumeración, y por eso `login_attempt` tiene retención de días.

## Consecuencias

- navetta, presenze y banditore necesitan la tabla `login_attempt` y el bloqueo; hoy no existen.
- presenze y banditore cambian el orden de su verificación de credenciales. Es un cambio corto y
  sin efecto visible salvo que el login pasa a tardar lo mismo siempre.
- vettore sustituye su limitador en memoria en el camino de login. El resto de sus límites en
  memoria quedan fuera de este ADR.
- El punto 4 deja explícito que concordia se aparta del resto **por su dominio**, no por gusto, y
  que ese apartamiento va escrito en su repositorio.
- Un umbral por identificador es también una forma de negar el servicio a una cuenta ajena a
  propósito. El umbral por IP y la ventana corta lo acotan; eliminarlo del todo exigiría un segundo
  factor, que no todos los productos tienen.

## Descartado

- **Mensajes de error distintos por motivo**, que es lo cómodo para quien se equivoca de correo.
  Convierte el login en un verificador de cuentas para cualquiera.
- **Límite de tasa solo por IP**, sin umbral por identificador: no frena a quien prueba una
  contraseña por IP desde muchas.
- **Bloqueo en memoria del proceso.** Se pierde al reiniciar y se multiplica por worker.
- **Bloquear la cuenta de forma permanente** hasta intervención. Convierte un ataque barato en una
  baja de servicio garantizada.
