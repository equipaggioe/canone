# ADR-0066 · Una fuente corresponde a la versión en uso, aunque no tenga fecha

- **Estado:** Aceptada
- **Fecha:** 2026-10-21
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

El [ADR-0063](0063-una-fuente-cumple-siete-requisitos-y-su-texto-se-lee-al-escribir-codigo.md)
pedía que una fuente fuera fija: con versión o fecha, y de la versión de la tecnología que se usa.
El requisito venía del
[ADR-0032](0032-una-guia-de-una-organizacion-se-cita-si-se-escribio-para-que-otros-la-adopten.md),
que pedía a una guía de una organización estar versionada porque quien la publica la cambia cuando
quiere.

## Decisión

1. El requisito 5 es «De la versión en uso»: la fuente corresponde a la versión de la tecnología
   que se usa, y la copia de `fuentes/` congela ese texto. Ya no pide versión ni fecha. Reemplaza
   esa parte del punto 1 del ADR-0063.

## Consecuencias

- Una página sin versión ni fecha puede ser fuente si cumple los demás requisitos.
- Un cambio del texto original no cambia la página: se ve con `git diff` al volver a descargarlo.

## Descartado

- **Pedir versión o fecha:** la copia de `fuentes/` ya resuelve que el texto cambie sin aviso, y
  la fecha deja fuera textos normativos que no la publican.
