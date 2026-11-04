# ADR-0117 · Una fuente se cita si evita escribir al menos tres convenciones

- **Estado:** Aceptada
- **Fecha:** 2026-11-03
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

Citar una fuente cuesta su copia en `fuentes/`, su fila en `fuentes/README.md`, la cita en la
página, una nueva descarga en cada cambio de versión y leerla al escribir código. Ningún requisito
pedía que eso ahorrara algo. El requisito «Cubre» no lo resuelve: no aplica a una cita por entradas,
y en una cita entera mide qué parte de lo que regula la fuente queda resuelta, no cuánto evita
escribir. Así, `journal-upload.conf` se cita solo por `URL=`, y PEP 698, por una convención que
la página escribe de todos modos.

## Decisión

1. Una fuente cumple un octavo requisito, «Aporta»: evita escribir al menos tres convenciones,
   contando todas las páginas que la citan.
2. Cuenta cada enunciado o entrada que se cumple sin que una página lo escriba. No cuenta lo que una
   página escribe de todos modos, como una elección o lo que endurece, ni lo que deja sin efecto o
   se dirige a otro actor.
3. Una fuente que no llega a tres no se cita, y sus convenciones se escriben como propias.

## Consecuencias

- Una cita se paga solo cuando evita escribir más que lo que cuesta mantenerla.
- Tres es un corte elegido, no el resultado de una medición.
- Quedan casos dudosos: en la sección 4 del RFC 6585, el resultado depende de si «no guardar en
  caché» se dirige a otro actor.
- Ningún programa cuenta las convenciones: el requisito se aplica al revisar cada página.
- Las citas actuales que no lleguen a tres salen al revisar su página, junto con las menciones como
  «Endurece PEP 698». No se hace un barrido.

## Descartado

- **Citar si ahorra más de lo que cuesta, sin un mínimo:** cada revisión lo interpretaría distinto.
- **Contar las convenciones que aporta la fuente:** PEP 698 pasaría, aunque la página escribe su
  única convención.
