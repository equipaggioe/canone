# «Cumplimiento» de autenticacion.md

Tema pendiente: la plantilla de autenticación se escribe por partes, y cada parte suma sus filas a «Cumplimiento» de `autenticacion.md`.

## Estado (verificado 2026-11-23)

| Pieza | Estado |
| :--- | :--- |
| Parte 1, la sesión | Hecha: el login con contraseña, la cookie, el token de acceso, el refresco rotado, el `Origin`, las esperas y el deshabilitado por fallos, cerrar sesión y la purga, en `plantilla/server/` y `tests/test_sessions.py`, con sus filas en «Cumplimiento» ([ADR-0219](../adr/0219-una-app-presenta-un-token-de-acceso-opaco-y-el-login-tiene-una-ruta-por-metodo-y-forma.md)) |
| Parte 2, las passkeys | Hecha: el login con passkey, por la cookie y por los tokens, con la verificación de `webauthn` y lo que el servidor comprueba aparte, en `plantilla/server/` y `tests/test_passkeys.py` ([ADR-0221](../adr/0221-el-rp-id-y-los-origins-de-las-passkeys-salen-de-settings.md)) |
| Plugin `passkey` de Flutter y extensión `flet_passkey` | Escritos en `plantilla/packages/passkey/`, para Android, iOS, macOS y Windows ([ADR-0224](../adr/0224-el-plugin-de-passkeys-cubre-windows-11-y-macos.md)). Compila en Android, y la capa de Dart de Windows pasa sus pruebas con el canal simulado. Sin compilar: iOS, macOS y el C++ de Windows. Sin probar en un dispositivo, y Windows 10 sin confirmar |
| Parte 3, el código de autorización | Hecha para el escritorio y la web: la página que sirve el servidor, el canje en el endpoint de token y el flujo de la web por el servidor, en `plantilla/server/` y `tests/test_authorization.py` ([ADR-0223](../adr/0223-el-servidor-sirve-la-pagina-de-autorizacion-y-el-codigo-queda-para-el-escritorio-y-la-web.md)). Faltan los colores de la marca en la página |
| Parte 4, registro y cuentas | Hecha: el registro con el código por correo o por SMS y la passkey, el código de instalación y la cuenta de administración, volver a autenticarse, vincular, ver y borrar passkeys, cambiar el correo o el teléfono, y los avisos por correo y por SMS, también el de una passkey posiblemente clonada, en `plantilla/server/`, `tests/test_registration.py`, `tests/test_account.py` y `tests/test_messages.py` ([ADR-0225](../adr/0225-equipaggio-y-consola-son-instrumentos-de-canone.md) y [ADR-0226](../adr/0226-el-registro-trae-el-codigo-y-la-passkey-y-volver-a-autenticarse-renueva-la-sesion.md)). Falta el registro con contraseña, que llega con la parte 5, y sin autenticador con teléfono, que llega con la 6. La URL de la API de Equipaggio no se probó contra el servicio |
| `scripts/verificar.py` | Solo comprueba las versiones de pwdlib, phonenumbers y `webauthn` (`PYPROJECT`), que son de `stack.md` |

## Qué falta

| # | Parte | Pruebas que se podrían sumar |
| :--- | :--- | :--- |
| 5 | Contraseñas: crear y cambiar, la lista de bloqueo, cerrar las demás sesiones, y registrarse con contraseña | Una cuenta de administración no agrega una contraseña |
| 6 | Código por SMS y recuperación, y registrarse con teléfono sin autenticador | Una cuenta de administración no entra con código por SMS y no se recupera con el código |
| 7 | Gestión de la cuenta: ver cada intento fallido y cada autenticador deshabilitado, volver a habilitarlo, ver y cerrar las sesiones, y borrar o deshabilitar una cuenta. Va después de la 6: el teléfono, el tercer autenticador, cuenta sus fallos desde ella | — |
| 8 | WebSocket: el handshake con la cookie o el token, el cierre 4401 | — |
| 9 | Push en los avisos: FCM, Web Push, y el FID y la suscripción de cada sesión | — |
| 10 | `verificar.py` compara los archivos de autenticación que se copian sin editar | Después de las partes anteriores, igual que el resto de la plantilla del servidor |
