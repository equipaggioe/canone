# «Cumplimiento» de autenticacion.md

Tema pendiente: la plantilla de autenticación se escribe por partes, y cada parte suma sus filas a «Cumplimiento» de `autenticacion.md`.

## Estado (verificado 2026-11-23)

| Pieza | Estado |
| :--- | :--- |
| Parte 1, la sesión | Hecha: el login con contraseña, la cookie, el token de acceso, el refresco rotado, el `Origin`, las esperas y el deshabilitado por fallos, cerrar sesión y la purga, en `plantilla/server/` y `tests/test_sessions.py`, con sus filas en «Cumplimiento» ([ADR-0219](../adr/0219-una-app-presenta-un-token-de-acceso-opaco-y-el-login-tiene-una-ruta-por-metodo-y-forma.md)) |
| Parte 2, las passkeys | Hecha: el login con passkey, por la cookie y por los tokens, con la verificación de `webauthn` y lo que el servidor comprueba aparte, en `plantilla/server/` y `tests/test_passkeys.py` ([ADR-0221](../adr/0221-el-rp-id-y-los-origins-de-las-passkeys-salen-de-settings.md)). Falta el aviso al titular de una passkey posiblemente clonada, que llega con los avisos |
| `scripts/verificar.py` | Solo comprueba las versiones de pwdlib, phonenumbers y `webauthn` (`PYPROJECT`), que son de `stack.md` |

## Qué falta

| # | Parte | Pruebas que se podrían sumar |
| :--- | :--- | :--- |
| 3 | Código de autorización: el endpoint de autorización, con su página que entra con la passkey (sin decidir: si la sirve el servidor o la web), el canje en el endpoint de token y el flujo de la web por el servidor. Los clientes son una constante del código | Sin `code_challenge`, o con `plain`, responde `invalid_request`; con `scope`, `invalid_scope`; un código presentado dos veces responde `invalid_grant` y borra la sesión; el canje lleva `no-store` y `Pragma` |
| 4 | Registro y cuentas: el registro, el código de instalación, la cuenta de administración, vincular una passkey, cambiar el correo o el teléfono, los avisos | Una cuenta de administración no entra con contraseña ni con código por SMS, ni con una passkey sin el flag UV, y no se recupera con el código |
| 5 | Contraseñas: crear y cambiar, la lista de bloqueo, cerrar las demás sesiones | — |
| 6 | Código por SMS y recuperación | — |
| 7 | WebSocket: el handshake con la cookie o el token, el cierre 4401 | — |
| 8 | `verificar.py` compara los archivos de autenticación que se copian sin editar | Después de las partes anteriores, igual que el resto de la plantilla del servidor |
