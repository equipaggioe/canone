# La primera cuenta de administrador en una máquina

Tema pendiente: **sin decidir**.

## Estado (verificado 2026-11-18)

Canone no dice cómo nace la primera cuenta con la que se entra al panel de un producto, la del dueño de la plataforma.

| Pieza | Estado |
| :--- | :--- |
| `seeders/` de [fastapi.md](../plataformas/fastapi.md#seeders) | Corre en cada despliegue, sin entrada: no puede pedir una contraseña |
| `credentials.py` de [despliegue.md](../plataformas/despliegue.md#configuración) | Cifra campos de `Settings`, que el servidor lee en cada arranque: una contraseña inicial quedaría como credencial para siempre |
| posta | `scripts/seeders/platform_admin.py` la pide en la terminal, con las credenciales de la unidad, que en la máquina solo tiene systemd |

## Qué hay que decidir

- Si la crea una tarea de `python -m app.tasks`, lanzada por un comando de `database.py`, con la contraseña por stdin.
- Si la crea un seeder con un correo o un teléfono de `Settings`, y la cuenta entra la primera vez por un código.

## Cuándo se retoma

Antes de que un producto con panel pase a producción: hoy la cuenta se crea a mano en cada máquina.
