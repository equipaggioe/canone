# Autenticación sin probar en el dispositivo o el servicio

Tema pendiente: la plantilla de autenticación está escrita y con sus filas en «Cumplimiento» de [autenticacion.md](../plataformas/autenticacion.md), y lo que sigue falta probarlo donde corre.

## Estado (verificado 2026-11-24)

| Pieza | Comprobado | Falta |
| :--- | :--- | :--- |
| Plugin `passkey` de Flutter y extensión `flet_passkey` | Compila en Android. El C++ de Windows compila con Visual Studio Build Tools 2022 17.14 y Flutter en una máquina con Windows 10, y la capa de Dart de Windows pasa sus pruebas con el canal simulado | Compilarlo en iOS y en macOS, y crear y usar una passkey en un dispositivo de cada sistema ([ADR-0224](../adr/0224-el-plugin-de-passkeys-cubre-windows-11-y-macos.md)) |
| Passkeys en Windows 10 | En Windows 10 22H2, `webauthn.dll` da la versión 2 de su API y dice que hay un autenticador del sistema con verificación del usuario | Crear y usar una passkey |
| Correo y SMS por Equipaggio | `PUT https://equipaggio.net/api/email/{id}` sin una clave válida responde 401, y los cuerpos son los de su `openapi.json` | Enviar con la clave de un despliegue |
| Push por FCM | Una cuenta de servicio falsa responde el error esperado | Enviar a un dispositivo con Android y a uno con iOS, con la cuenta de servicio de un proyecto |
| Web Push | Llegó a Chrome, a Firefox y a Edge en Windows | Safari |

## Qué falta

Lo de la última columna. Cada fila se borra cuando se prueba.
