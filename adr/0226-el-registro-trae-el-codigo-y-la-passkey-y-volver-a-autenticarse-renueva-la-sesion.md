# ADR-0226 · El registro trae el código y la passkey, y volver a autenticarse renueva la sesión

- **Estado:** Aceptada. El punto 2, en lo que responde a la contraseña de una cuenta de administración, lo reemplaza el [ADR-0233](0233-una-cuenta-de-administracion-cuenta-sus-fallos-como-cualquier-otra.md), y el punto 1, en el registro del primer superadministrador, el [ADR-0235](0235-el-superadministrador-se-registra-con-el-codigo-de-instalacion-y-un-administrador-de-cliente-es-una-cuenta-comun.md)
- **Fecha:** 2026-11-23
- **Alcance:** `autenticacion.md`, `fastapi.md`, `plantilla/server/` y los workflows

## Contexto

`autenticacion.md` decía qué pasa al registrarse, al volver a autenticarse y en una cuenta de
administración, pero no cómo: qué autenticador vincula una cuenta común, qué responde el servidor a un
administrador que entra mal, qué es «volver a autenticarse en ese momento» ni de dónde sale «a quién
escribir» en un aviso.

Se comprobó leyendo `validate_certificate_chain` de `webauthn` 3.0.1 que, sin certificados raíz, no
valida la cadena de `x5c`: acepta un `packed` con cualquier certificado que firme bien. El servidor
rechaza él mismo la atestación que no es `none` ni `packed` sin `x5c`.

## Decisión

1. El registro trae el código y el primer autenticador en la misma petición, y abre la sesión. Una
   cuenta con teléfono puede registrarse sin autenticador.
2. Una cuenta de administración que entra con contraseña recibe 401, sin verificarla ni contar un
   fallo, y el registro con el código de instalación no acepta contraseña.
3. Una cuenta de administración que entra con una passkey sin el flag UV recibe 403 de tipo
   `user-verification-required`, sin contar un fallo.
4. Volver a autenticarse es un paso aparte que renueva la fila de la sesión: tokens nuevos y
   `authenticated_at`. Una operación que lo pide lo acepta durante 5 minutos.
5. «A quién escribir» es `contact` de `Settings`.
6. La cuenta guarda su rol en `role`.
7. Los avisos van por correo y por SMS. El push llega cuando la plantilla lo tenga.
8. Un correo o un SMS se encola en la sesión de la petición y sale después del commit,
   también el de un `KeptError`.
9. Los límites son ventanas deslizantes en sorted sets de Valkey, y un script de Lua
   cuenta el intento en todos solo si ninguno está lleno.
10. El registro verifica la passkey antes que el código.
11. Dos registros con el código de instalación se esperan con
    `pg_advisory_xact_lock`.
12. Un código equivocado o vencido responde 400 de tipo `invalid-code`.
13. El host del SMS es el `Host` de la petición, y uno que no es una superficie de
    `domain` responde 400.
14. Registrarse no avisa: la passkey se vincula a una cuenta que acaba de nacer.

## Consecuencias

- Una passkey que falla al registrarse deja una credencial sin cuenta en el dispositivo, y el usuario
  pide opciones nuevas.
- Después de volver a autenticarse, el token de refresco anterior es un reúso, y presentarlo borra la
  sesión.
- `httpx` pasa a ser una dependencia del servidor, y `phonenumbers` entra en la plantilla.
- Cada despliegue escribe `contact`, `equipaggio_key`, `setup_code` y `sms_hashes` en sus
  credenciales.

## Descartado

- **Que el código abra una sesión sin autenticador.** Una cuenta con solo correo no podría volver a
  entrar, ni volver a autenticarse para vincular algo.
- **Responder con un tipo propio a la contraseña de un administrador.** Le diría a quien sabe el correo
  que la cuenta es de administración.
- **La credencial en la misma petición que la operación.** Agregar una passkey pediría dos ceremonias
  en una petición, y no renovaría la fila.
- **Un ticket de un solo uso al volver a autenticarse.** Tampoco renueva la fila.
- **Ventanas fijas con `INCR` y `EXPIRE`.** Dejan pasar el doble en el borde de la ventana.
- **El push dentro de esta parte.** Pide FCM, Web Push y el FID y la suscripción de cada sesión.
