# ADR-0101 · El journal guarda a lo sumo 365 días, y equipaggio nota la máquina que deja de enviar

- **Estado:** Aceptada
- **Fecha:** 2026-10-28
- **Alcance:** «Registros» de [`plataformas/despliegue.md`](../plataformas/despliegue.md)

## Contexto

`despliegue.md` decía que el journal guarda 365 días, pero journald también borra por tamaño:
`SystemMaxUse=` vale por defecto el 10 % del disco, y a lo sumo 4G, en
[`journald.conf`](../fuentes/systemd/journald.conf.xml). Tampoco había una regla que dijera quién
nota que una máquina dejó de enviar su journal: el ADR-0100 lo dejaba solo como consecuencia.

## Decisión

1. El journal guarda a lo sumo 365 días. Es un máximo, por las direcciones IP de personas, no un
   mínimo.
2. `SystemMaxUse=` queda en su valor por defecto.
3. Detectar que una máquina dejó de enviar le toca a equipaggio, por la hora de la última entrada
   que recibió de ella. Cada máquina escribe en el journal al menos una vez por día, con el timer
   de la purga de `event_log`.

## Consecuencias

- Una máquina que registra mucho guarda menos de 365 días. La copia de equipaggio no cambia.
- Lo que no salió todavía se pierde si el túnel sigue caído hasta llenar el límite. El punto 3 lo
  hace notar mucho antes.
- Equipaggio decide cuánto silencio avisa, como decide qué avisar con la ruta de salud
  (ADR-0080).

## Descartado

- **Un `SystemMaxUse=` mayor, para asegurar los 365 días:** le quita disco a la app, y la copia que
  vale es la de equipaggio.
- **Un latido propio de cada máquina hacia equipaggio:** el timer de la purga ya escribe cada día.
