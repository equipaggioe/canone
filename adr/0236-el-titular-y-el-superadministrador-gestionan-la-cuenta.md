# ADR-0236 · El titular y el superadministrador gestionan la cuenta, y deshabilitarla le quita sus autenticadores

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Alcance:** `autenticacion.md`, `fastapi.md` y `plantilla/server/`

## Contexto

`autenticacion.md` decía que el titular ve sus fallos, sus autenticadores deshabilitados y sus
sesiones, que una cuenta se borra o se deshabilita y que un superadministrador recupera otra, sin
rutas ni formas. NIST SP 800-63B-4 §3.2.2 pide volver a vincular un autenticador deshabilitado, y
§4.5 define invalidarlo como quitar su vínculo. ASVS 5.0 §7.5.3 pide volver a autenticarse antes de
una operación muy sensible, y §7.4.5, que un administrador cierre las sesiones de una cuenta o de
todas. Google Play pide que una app que crea cuentas deje borrarlas en la app y en una página web
([Google Play](https://support.google.com/googleplay/android-developer/answer/13327111), leído); la
guía 5.1.1(v) de Apple lo pide en la app (sin confirmar: se leyó un resumen).

La página se contradecía: un superadministrador recuperaba cualquier otra cuenta cambiando su correo
o su teléfono, pero el código para un superadministrador respondía siempre 403.

## Decisión

1. Los intentos fallidos salen de `event_log`, con el reúso de un token de refresco, la IP y el user
   agent, por `GET /api/account/failures`.
2. `GET /api/account` responde el estado de la contraseña y del teléfono, y la lista de passkeys, el
   de cada una.
3. Volver a habilitar una passkey o el teléfono es `POST .../enable`. La contraseña se vuelve a
   habilitar al cambiarla o al restablecerla.
4. La fila de la sesión guarda el user agent, y el titular cierra una, también la suya.
5. El titular borra su cuenta, y un superadministrador, la de otro. Un superadministrador no actúa
   sobre la suya.
6. Deshabilitar es `disabled_at`, y borra los autenticadores, lo que recupera la cuenta y sus
   sesiones. Solo lo hace un superadministrador.
7. Un superadministrador cambia el correo o el teléfono de otra cuenta sin código.
8. Cambiar el correo o el teléfono pone en cero los fallos de recuperación de ese camino.
9. Un superadministrador encuentra la cuenta en `GET /api/accounts`, y una cuenta sin ese rol recibe
   403 en esas rutas.
10. El código vale para un superadministrador en la dirección que le puso otro, hasta
    que entra. Recupera como se registra: con una passkey con el flag UV, si el producto la usa.
11. Un superadministrador cierra las sesiones de otra cuenta, o las de todas menos la
    que llama.
12. Borrar la cuenta y cada cambio de un superadministrador sobre otra piden volver a
    autenticarse.
13. Una sesión de una cuenta deshabilitada no vale, y el canje de un código de
    autorización de una cuenta deshabilitada o borrada responde `invalid_grant`.
14. Volver a habilitar un autenticador que no está deshabilitado, o deshabilitar una
    cuenta que ya lo está, no cambia nada.

## Consecuencias

- `event_log` lleva un índice parcial por cuenta para los fallos, y los de la recuperación dicen su
  camino en `details`.
- Una cuenta que se vuelve a habilitar entra con el código por SMS o se recupera: sus passkeys y su
  contraseña no vuelven.
- Un login o una recuperación que corren a la vez que el deshabilitado pueden dejar una sesión o una
  recuperación pendiente: la sesión no vale y la recuperación se descarta al aplicarla.
- Borrar una cuenta falla si una tabla del producto la apunta con `RESTRICT`: la borra o la pasa cada
  producto.

## Descartado

- **Solo los contadores de cada autenticador.** No muestran cada intento ni de dónde vino.
- **Leer el dispositivo de una sesión de `event_log`.** Se purga a los 365 días, y una sesión en uso
  puede durar más.
- **Suspender la cuenta sin borrar sus autenticadores.** NIST §4.5 pide invalidarlos.
- **Que un superadministrador borre o deshabilite su cuenta.** Si fuera el último, el código de
  instalación registraría a quien lo tenga.
- **Un código a la dirección nueva, que el titular dicta al superadministrador.** El de la
  recuperación ya la verifica.
- **Dejar los fallos del camino al cambiar la dirección.** Quien gastó los 100 fallos del correo
  dejaría sin salida la recuperación del superadministrador.
