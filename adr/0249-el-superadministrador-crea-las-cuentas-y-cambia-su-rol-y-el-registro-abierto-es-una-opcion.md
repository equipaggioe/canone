# ADR-0249 · El superadministrador crea las cuentas y cambia su rol, y el registro abierto es una opción del producto

- **Estado:** Aceptada el 2026-11-26 por el desarrollador: que el superadministrador cree la cuenta y
  el titular la tome con el código de recuperación, que cambie el rol de otra cuenta, y que el
  registro sin invitación siga posible en otros productos. Los puntos marcados *(propuesta)* se
  eligieron al construirla, sin preguntar.
- **Fecha:** 2026-11-26
- **Alcance:** `autenticacion.md` y `plantilla/server/`

## Contexto

`autenticacion.md` daba el rol `superadmin` solo al primero, con el código de instalación, y
ninguna ruta creaba otro, aunque la página ya suponía varios: «al superadministrador lo recupera
otro superadministrador». El registro estaba siempre abierto. Un producto interno, como el panel de
equipaggio, necesita incorporar administradores sin abrir el registro a cualquiera, y cambiar
después el rol de una cuenta.

La plantilla ya tenía casi todo: un superadministrador le pone a otra cuenta un correo o un teléfono
sin código, que verifica el código de recuperación; `recovery_address.granted_at` deja que un
superadministrador tome ese código en la dirección que le puso otro, hasta que entra; y una cuenta
sin passkey se recupera en el momento.

## Decisión

Las reglas están en `autenticacion.md`, «Cuentas» y «Superadministrador»; aquí va el porqué.

1. El superadministrador crea otra cuenta por `PUT /api/accounts/{id}`, con un correo o un teléfono
   y su rol, sin código ni autenticador. El titular la toma con el código de recuperación, con el
   que vincula su primer autenticador.
2. La dirección de una cuenta creada así queda puesta por un superadministrador (`granted_at`),
   cualquiera sea el rol: si la cuenta pasa a superadministrador antes de entrar, también toma el
   código *(propuesta)*.
3. El superadministrador cambia el rol de otra cuenta por `PUT /api/accounts/{id}/role`, que pide
   volver a autenticarse, como cada cambio sobre otra cuenta. Rige desde la petición siguiente,
   porque la cuenta se lee en cada una.
4. `OPEN_REGISTRATION` de `methods.py` dice si se registra cualquiera. Con el registro cerrado no se
   monta `POST /api/auth/register/code`, y solo se registra el primer superadministrador, con el
   código de instalación.
5. Con el registro cerrado, un registro que trae un código responde 403, antes de mirar la passkey
   *(propuesta)*.
6. La creación responde 201 con la cuenta y, repetida con el mismo cuerpo, 200; otro cuerpo con el
   mismo id responde 409, como la vinculación de una passkey *(propuesta)*.
7. La cuenta creada empieza en el idioma de la petición del superadministrador, y recibe el aviso
   `account_created`; el cambio de rol avisa con `role_changed` *(propuesta: los textos)*.
8. El cambio de rol va al registro de eventos como `authz_change`, con el rol anterior y el nuevo,
   además de `authz_admin`, como pide `fastapi.md`.

## Consecuencias

- Una sola idea cubre invitar, invitar con un rol y cambiarlo después, sin tabla nueva: la
  invitación pendiente es una cuenta sin autenticador, y se borra con `DELETE /api/accounts/{id}`.
- `api_router` de `main.py` recibe `open_registration`, y cada repositorio con cuentas lo pasa al
  completar `main.py` y declara `OPEN_REGISTRATION` en `methods.py`.
- El titular de una cuenta creada necesita que le llegue el código: el correo o el SMS del producto
  tienen que funcionar antes de crearla.
- Pasar a superadministrador una cuenta que entra solo con contraseña, en un producto con passkey,
  la deja sin poder entrar hasta que vincule una passkey: el superadministrador le pone su dirección
  para que la recupere.

## Descartado

- **Registrarse y que otro lo ascienda, sin crear la cuenta:** obliga al registro abierto, y deja
  cuentas sin acceso que cualquiera puede crear.
- **Una tabla de invitaciones:** duplica lo que ya hacen la cuenta sin autenticador, el código de
  recuperación y `granted_at`.
- **Que el código de instalación sirva para más superadministradores:** el código queda vigente para
  siempre, y quien lo tiene no es un superadministrador que volvió a autenticarse.
