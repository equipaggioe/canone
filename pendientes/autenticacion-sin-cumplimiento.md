# «Cumplimiento» de autenticacion.md

Tema pendiente: la plantilla de autenticación se escribe por partes, y cada parte suma sus filas a «Cumplimiento» de `autenticacion.md`.

## Estado (verificado 2026-11-22)

| Pieza | Estado |
| :--- | :--- |
| Parte 1, la sesión | Hecha: el login con contraseña, la cookie, el token de acceso, el refresco rotado, el `Origin`, las esperas y el deshabilitado por fallos, cerrar sesión y la purga, en `plantilla/server/` y `tests/test_sessions.py`, con sus filas en «Cumplimiento» ([ADR-0219](../adr/0219-una-app-presenta-un-token-de-acceso-opaco-y-el-login-tiene-una-ruta-por-metodo-y-forma.md)) |
| `scripts/verificar.py` | Solo comprueba las versiones de pwdlib, phonenumbers y `webauthn` (`PYPROJECT`), que son de `stack.md` |

## Qué falta

| # | Parte | Pruebas que se podrían sumar |
| :--- | :--- | :--- |
| 2 | Código de autorización: el endpoint de autorización, el canje en el endpoint de token y el flujo de la web por el servidor | Sin `code_challenge`, o con `plain`, responde `invalid_request`; con `scope`, `invalid_scope`; un código presentado dos veces responde `invalid_grant` y borra la sesión; el canje lleva `no-store` y `Pragma` |
| 3 | Registro y cuentas: el registro, el código de instalación, la cuenta de administración, cambiar el correo o el teléfono, los avisos | Una cuenta de administración no entra con contraseña ni con código por SMS, ni con una passkey sin el flag UV, y no se recupera con el código |
| 4 | Contraseñas: crear y cambiar, la lista de bloqueo, cerrar las demás sesiones | — |
| 5 | Código por SMS y recuperación | — |
| 6 | Passkeys | Respuesta de WebAuthn armada sin UV |
| 7 | WebSocket: el handshake con la cookie o el token, el cierre 4401 | — |
| 8 | `verificar.py` compara los archivos de autenticación que se copian sin editar | Después de las partes anteriores, igual que el resto de la plantilla del servidor |
