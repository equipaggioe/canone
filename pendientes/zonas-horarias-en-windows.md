# Las zonas horarias en Windows

Tema pendiente: **sin decidir**.

## Estado (verificado 2026-11-18)

Python en Windows no trae la base de zonas horarias de IANA: `zoneinfo.available_timezones()` da 0 y `ZoneInfo("America/Mexico_City")` falla. Debian 13 sí la trae, así que la máquina y el CI no lo ven. En posta fallan en Windows las pruebas de las paqueterías, la impresión, los reportes y los cobros; en la distro WSL `Testing` pasan.

| Pieza | Estado |
| :--- | :--- |
| [postgres.md](../plataformas/postgres.md) | Nombra cada zona con su nombre de IANA |
| [python.md](../plataformas/python.md) | No dice de dónde sale la base de zonas fuera de Linux |

## Qué hay que decidir

- Si cada servidor que usa `zoneinfo` declara `tzdata`, que Python lee solo donde el sistema no trae la base.
- Si las pruebas del servidor corren solo en Linux, en la distro de pruebas, y no en Windows.

## Cuándo se retoma

Con el próximo servidor que use una zona horaria, o cuando se decida dónde corren las pruebas en local.
