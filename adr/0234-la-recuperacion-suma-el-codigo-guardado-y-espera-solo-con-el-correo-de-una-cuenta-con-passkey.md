# ADR-0234 · La recuperación suma el código guardado y espera solo con el correo de una cuenta con passkey

- **Estado:** Aceptada. Los puntos 11 a 14 son *(propuesta)*. El [ADR-0236](0236-el-titular-y-el-superadministrador-gestionan-la-cuenta.md) reemplaza parte del punto 6.
- **Fecha:** 2026-11-24
- **Alcance:** `autenticacion.md`, `fastapi.md` y `plantilla/server/`

## Contexto

`autenticacion.md` dejaba restablecer solo la contraseña a una cuenta que tenía una, cerraba todas
las sesiones al restablecerla, bloqueaba toda la recuperación a los 100 fallos y dejaba al
administrador como salida, y aplicaba a las 24 horas la recuperación por correo de una cuenta con
passkey sin decir cómo se adelanta. NIST SP 800-63B-4 §4.2.2.2 pide, para una cuenta del nivel de
una passkey, dos códigos de métodos distintos, o un código y otro autenticador. ASVS 5.0 §7.4.3 pide
ofrecer cerrar las demás sesiones, no cerrarlas. Google y GitHub ofrecen códigos de respaldo, y Apple
y Google hacen esperar la recuperación que llega con poco.

## Decisión

1. Con el código, cualquier cuenta restablece o agrega la contraseña, o vincula una passkey, de los
   métodos del producto.
2. El titular tiene un código guardado. El código enviado y el guardado juntos recuperan en el
   momento.
3. La recuperación espera 24 horas solo en una cuenta con passkey que llega solo con el código del
   correo. Un inicio de sesión del titular la cancela, y el titular la cancela desde la app.
4. Ni cambiar la contraseña ni recuperar la cuenta cierran sesiones: la app ofrece cerrar las demás,
   con `DELETE /api/account/sessions`.
5. El correo, el teléfono y el código guardado cuentan sus fallos cada uno aparte, y a los 100 ese
   camino responde 403 de tipo `recovery-disabled`.
6. La cuenta de administración del producto no se recupera con el código: la recupera otro
   administrador, y la primera, quien opera el servidor. El administrador de una organización
   cliente es una cuenta común.
7. Las rutas son `POST /api/auth/recovery/code`, `/recovery/password`, `/recovery/options` y
   `/recovery/passkey`. Las opciones verifican el código sin gastarlo.
8. La recuperación no abre una sesión. Responde 204 si se aplica, 202 si espera y 200 con el código
   guardado nuevo si gastó el anterior.
9. La recuperación pendiente vive en la tabla `recovery`, y la tarea `recover` la aplica cada minuto.
10. Las rutas de la recuperación se montan si el producto usa la passkey o la contraseña, y cada
    forma, con su método.
11. *(propuesta)* El código guardado son 80 bits en 16 caracteres de base32, creado por
    `PUT /api/account/recovery-code` después de volver a autenticarse, y el servidor guarda su hash
    Argon2id.
12. *(propuesta)* Los fallos del correo y del teléfono viven en `recovery_address`, y los del código
    guardado, con su hash, en `recovery_code`.
13. *(propuesta)* Un inicio de sesión pone en cero los fallos de los tres caminos.
14. *(propuesta)* `GET /api/account/recovery` muestra la recuperación pendiente, y responde 404 si
    no hay.

## Consecuencias

- Quien tiene el teléfono o el código guardado no espera. Solo espera quien llega con el correo a una
  cuenta con passkey, que es el caso del correo robado.
- Un ladrón que cambia la contraseña no deja afuera al dueño, y el dueño cierra la sesión del ladrón.
  Cambia la regla de la parte 5.
- `tasks.py` declara `TIMERS` con la tarea `recover`.
- Una cuenta que perdió el correo, el teléfono y el código guardado depende de un administrador.

## Descartado

- **Que una cuenta con contraseña solo la restablezca.** Quien perdió la passkey y olvidó la
  contraseña no podría vincular una passkey nueva.
- **Cerrar todas las sesiones al recuperar o al cambiar la contraseña.** Si quien recupera es un
  ladrón, deja afuera al dueño.
- **Quitar la espera.** Quien toma el correo tomaría en el acto una cuenta protegida con passkey.
- **Un solo bloqueo para toda la recuperación.** Quien tira códigos al correo bloquearía también el
  teléfono y el código guardado.
- **Un administrador como salida habitual.** Los servicios grandes lo dejan como último recurso o no
  lo tienen.
- **Opciones de la passkey sin el código.** Mostrarían los credential ID de la cuenta a quien sepa el
  correo.
