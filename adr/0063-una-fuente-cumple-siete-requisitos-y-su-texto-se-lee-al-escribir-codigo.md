# ADR-0063 · Una fuente cumple siete requisitos, y su texto se lee al escribir código

- **Estado:** Aceptada
- **Fecha:** 2026-10-21
- **Alcance:** `plataformas/`, `fuentes/` y `principios.md`

## Contexto

`plataformas/README.md` admitía una fuente por su orden, del 1 al 4, y pedía requisitos solo a una
guía de orden 4. Una fuente de orden 1 entraba completa aunque mezclara reglas con pasos y
tutoriales. Citar una fuente adoptaba sus convenciones sin escribirlas, pero el asistente que
escribe el código no leía `fuentes/` al trabajar: una convención que no sabía de memoria y que
ninguna herramienta verificaba no le llegaba.

## Decisión

1. Una fuente, o la parte que se cita, cumple siete requisitos: es normativa, decide algo, la
   escribe una autoridad para que otros la adopten, es acotada, es fija, su licencia permite
   copiarla y no depende de la infraestructura de quien la publica. Reemplaza el punto 1 del
   [ADR-0032](0032-una-guia-de-una-organizacion-se-cita-si-se-escribio-para-que-otros-la-adopten.md).
2. Acotada es que la parte citada se puede leer entera al escribir el código de su sección, salvo
   que su fuente sea de conocimiento general o que una herramienta de «Cómo se hace cumplir» la
   verifique.
3. El orden del 1 al 4 solo desempata entre dos fuentes que cumplen los siete requisitos y regulan
   lo mismo; a igual orden, gana la que cubre más del asunto. Reemplaza el punto 3 del
   [ADR-0030](0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md) y el
   punto 4 del
   [ADR-0056](0056-una-regla-es-lo-que-escribe-la-pagina-y-lo-que-adopta-una-fuente-es-una-convencion.md).
4. Al escribir código que cae en una sección de una página, se lee el texto en `fuentes/` de lo que
   esa sección cita, con la misma salvedad del punto 2. La regla va en `principios.md`, que se lee
   siempre.

## Consecuencias

- Cada convención está escrita una sola vez, en su fuente, y la página sigue escribiendo solo sus
  tres clases de reglas.
- Se puede citar un marco entero, como PEP 8, si es de conocimiento general o lo verifica una
  herramienta.
- Una parte de la documentación oficial que no es normativa deja de poder citarse.
- Leer las fuentes al escribir código ocupa contexto en cada sesión.

## Descartado

- **Escribir en la página las convenciones de una fuente citada:** duplica su texto, y las dos
  copias se desincronizan.
- **Admitir por orden y pedir requisitos solo al orden 4:** dejaba entrar tutoriales y pasos de la
  documentación oficial.
