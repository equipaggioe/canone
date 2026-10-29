# ADR-0103 · unattended-upgrades reinicia la máquina a las 04:00 cuando una actualización lo pide

- **Estado:** Aceptada
- **Fecha:** 2026-10-28
- **Alcance:** «Máquina» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

El punto 4 del ADR-0092 dejaba el kernel nuevo para un reinicio a mano. Contradice su punto 1: una
actualización de seguridad que espera a alguien deja la máquina expuesta mientras tanto, y nadie
mira la máquina cada día.

## Decisión

1. `unattended-upgrades` reinicia la máquina a las 04:00 cuando una actualización lo pide:
   `Automatic-Reboot "true"` y `Automatic-Reboot-Time "04:00"`. Reemplaza el punto 4 del ADR-0092.
2. Van en `/etc/apt/apt.conf.d/52automatic-reboot`, que instala `install.py`, y no en
   `20auto-upgrades`, el archivo que escribe el paquete al instalarse (ADR-0092).

## Consecuencias

- Cuando llega un kernel nuevo, la app cae alrededor de un minuto a las 04:00 y se cortan las
  llamadas en curso.
- Un respaldo en curso se corta, y el siguiente corre igual. Con `--append-only`, el lock del
  respaldo cortado queda en el repositorio, y limpiarlo le toca a la receptora (ADR-0079).
- Las 04:00 son de la hora de la máquina: `install.py` no fija la zona horaria.
- Comprobado en el código de `unattended-upgrades` 2.12: su gancho del kernel,
  `kernel/postinst.d/unattended-upgrades`, crea `/var/run/reboot-required`, que es lo que mira
  `Automatic-Reboot`.
- Comprobado con `scripts/infra/backup.sh`: un respaldo que se mata mientras tiene su lock no frena
  el siguiente.

## Descartado

- **Reiniciar a mano, el punto 4 del ADR-0092:** la máquina queda expuesta hasta que alguien
  reinicia.
- **Avisar en la ruta de salud que falta reiniciar:** igual espera a alguien.
- **Reiniciar en el momento, el valor por defecto de `Automatic-Reboot-Time`:** corta la app en
  horario de uso.
