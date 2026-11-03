# ADR-0113 · En `fuentes/` solo queda la lista de la que un programa de canone toma valores

- **Estado:** Aceptada
- **Fecha:** 2026-11-03
- **Alcance:** «Convenciones propias y valores predeterminados» de
  [`plataformas/README.md`](../plataformas/README.md), [`fuentes/README.md`](../fuentes/README.md),
  [`README.md`](../README.md) y las páginas que enlazan una lista

## Contexto

El ADR-0095 pedía guardar en `fuentes/` la copia de toda lista que usara una regla, y había siete.
Una lista que está en un programa no debe cambiar por sorpresa: su valor sigue igual aunque cambie
en su origen, hasta que se decida actualizarlo. Eso no vale para las demás: ningún programa lee ISO
4217 ni RFC 6455, y `svelte-check` y `flutter analyze` usan la lista de la versión instalada, no la
copia.

## Decisión

1. Una lista queda en `fuentes/` solo si un programa de canone toma valores de ella: hoy, los
   registros de IANA, de los que sale `turnserver.conf`, y el del W3C, del que sale `FEATURES` en
   `install.py`.
2. Una convención que usa otra lista la enlaza por su URL pública. Reemplaza el punto 1 del ADR-0095
   en lo que pide guardar la copia de toda lista.
3. Se borran las copias de ISO 4217, RFC 6455, las advertencias del compilador de Svelte y
   `flutter_lints`.

## Consecuencias

- Al actualizar una lista que se queda, `git diff` muestra qué cambió, y la copia permite comparar
  el programa con ella.
- Comprobado: `peers.py` falla si a `turnserver.conf` le falta un bloque de los registros de IANA.
- Nada compara `FEATURES` con el registro del W3C por sí solo: hoy coinciden sus 50 funciones.
- El contenido de una URL pública puede cambiar sin aviso, y nada lo registra.

## Descartado

- **Conservar las siete:** cuatro copias no fijan nada de lo que corre.
- **Conservar solo las que CI compara, las de IANA:** `FEATURES` se quedaría sin la versión de la
  que salió.
