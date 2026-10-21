# ADR-0032 · Una guía de una organización se cita si se escribió para que otros la adopten

- **Estado:** Reemplazada por [ADR-0063](0063-una-fuente-cumple-siete-requisitos-y-su-texto-se-lee-al-escribir-codigo.md)
- **Fecha:** 2026-10-05
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

El [ADR-0030](0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md)
pone en el orden 4 las guías de una organización de referencia, como las de Google, Microsoft o
Zalando. Ninguna de esas organizaciones hace estándares: escriben guías para sus propios equipos,
sin un proceso abierto de consenso, y las cambian cuando quieren.

## Decisión

1. Una guía de orden 4 se cita solo si cumple cuatro condiciones:
   1. Es pública y su licencia permite usarla.
   2. Es normativa: reglas numeradas con MUST o SHOULD, no consejos sueltos.
   3. Está versionada, con historial de cambios.
   4. La parte citada no depende de la infraestructura de quien la publica.

## Consecuencias

- Lo que importa de una guía es para quién se escribió, no a qué se dedica quien la publica.
- La copia de `fuentes/` fija la versión adoptada: un cambio de la organización no cambia la
  página hasta que se revisa.

## Descartado

- **Citar solo organismos de estándares:** asuntos como la paginación de una API REST no tienen
  estándar, y una guía normativa y pública es mejor base que una regla propia escrita de cero.
- **Juzgar una guía por lo conocida que es:** la popularidad no es una fuente.
