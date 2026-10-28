# ADR-0098 · *Protection* se cumple con los permisos y el respaldo, y no detecta cambios ni audita accesos

- **Estado:** Aceptada
- **Fecha:** 2026-10-27
- **Alcance:** «Registro de eventos» de [`plataformas/fastapi.md`](../plataformas/fastapi.md) y
  `plantilla/server/`

## Contexto

`fastapi.md` cita *Protection* del *Logging Cheat Sheet* de OWASP, y citarla adopta todas sus
convenciones. El
[ADR-0058](0058-los-eventos-se-nombran-con-el-vocabulario-de-owasp-y-un-cambio-de-fila-es-un-evento.md)
la cumplía con los permisos del rol de la app, pero la sección pide además detectar que un registro
se cambió o se borró, registrar y vigilar cada acceso, y revisar cada cierto tiempo quién lee.

Comprobado en Debian 13.5 con PostgreSQL 17.11 y 16 clientes:

- Una cadena de hashes que escribe un trigger del dueño detecta una fila cambiada y una borrada,
  pero baja las escrituras de 4532 a 480 por segundo, y las de un evento dentro de un cambio de
  5 ms, de 1852 a 130: la cabeza de la cadena las pone en fila.
- pgaudit, con un rol auditor sobre `event_log`, registra cada lectura de la app, del dueño y del
  volcado, y el dueño no puede cambiar `pgaudit.role`, pero le quita el `SELECT` al auditor sin
  aviso y deja de quedar registrado.

## Decisión

1. Solo el rol de la app y el dueño leen `event_log`, y ningún rol es miembro de ellos. Una prueba
   lo comprueba en cada CI: es la revisión periódica de quién lee.
2. La copia en solo lectura es el respaldo append-only, en cada corrida.
3. *Protection* queda sin efecto en detectar que un registro se cambió o se borró.
4. *Protection* queda sin efecto en registrar y vigilar cada acceso.

## Consecuencias

- Un cambio o un borrado del dueño o de `root` después del último respaldo no se detecta. Lo
  anterior queda en una copia que no se reescribe, y se compara a mano si hace falta.
- Si un día los eventos salen a un sistema central de logs, con quien lo vigile, los puntos 3 y 4
  se vuelven a evaluar.

## Descartado

- **La cadena de hashes con trigger:** cuesta entre 9 y 14 veces las escrituras, y `root` también
  cambia lo que verifica la cadena.
- **pgaudit:** audita a quien opera el servidor, el único que lee además de la app, y el dueño lo
  apaga sin aviso. Vigilar el registro es un proceso de operación, como *Monitoring of events*.
- **Dejar de citar *Protection*:** se adopta la mayor parte, y la página dice lo que deja sin
  efecto.
