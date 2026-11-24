# ADR-0233 · Una cuenta de administración cuenta sus fallos como cualquier otra

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Alcance:** `autenticacion.md` y `plantilla/server/`

## Contexto

El [ADR-0226](0226-el-registro-trae-el-codigo-y-la-passkey-y-volver-a-autenticarse-renueva-la-sesion.md)
respondía 401 a la contraseña de una cuenta de administración sin verificarla ni contar un fallo, para
no revelar que es de administración, y la primera versión del código por SMS hacía lo mismo con el
código. Se comprobó en la plantilla que una cuenta se revela igual por otras vías: tras 5 fallos, una
cuenta que existe responde 429 y una que no existe sigue con 401 o 400; una contraseña equivocada
tarda unos 67 ms con Argon2 en una cuenta que existe y 5 ms en una que no; y desde cualquier cuenta,
pedir el código para cambiar el correo a uno ajeno responde 409. Una cuenta de administración que
nunca cuenta fallos se distingue de las demás por la misma vía del 429.

## Decisión

1. Una cuenta de administración cuenta sus fallos, espera y se deshabilita como cualquier cuenta.
2. Si el producto usa la passkey, una contraseña o un código correctos de una cuenta de
   administración responden 403: solo los ve quien tiene la credencial.
3. Si el producto usa la passkey, pedir el código para entrar o para volver a autenticarse de una
   cuenta de administración responde 403, sin SMS.
4. La solicitud del código sigue respondiendo 404 a una cuenta que no existe.

## Consecuencias

- Las diferencias de una cuenta de administración quedan en lo que la define: el código de
  instalación, la passkey con UV y que no se recupera con el código.
- Quien sabe el teléfono de una cuenta de administración puede saber que lo es, por el 403 al pedir
  el código. Saberlo no le da una credencial.

## Descartado

- **Ocultar que una cuenta existe.** Habría que cerrar a la vez el 404 de las solicitudes de código,
  el 409 del cambio de correo o de teléfono, el 429 de las esperas y el tiempo de Argon2, y quien
  escribe mal su dirección no sabría por qué no le llega el código. Una IP enumera 10 direcciones
  cada 15 minutos, y saber que una cuenta existe no da una credencial.
- **Ocultar que una cuenta es de administración.** Exige un camino propio para esas cuentas en cada
  método, y se revela igual por las esperas.
