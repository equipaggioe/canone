# ADR-0030 · Una página cita lo que adopta en su mayoría, y lo demás es regla propia

- **Estado:** Aceptada. El punto 4 lo reemplaza el [ADR-0056](0056-una-regla-es-lo-que-escribe-la-pagina-y-lo-que-adopta-una-fuente-es-una-convencion.md), y el punto 3, el [ADR-0063](0063-una-fuente-cumple-siete-requisitos-y-su-texto-se-lee-al-escribir-codigo.md)
- **Fecha:** 2026-10-05
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

El [ADR-0018](0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md)
tomaba como única fuente la recomendación oficial de la tecnología, y todo lo demás era regla
propia. Para lo que la tecnología no cubre no decía dónde buscar, así que una regla propia salía de
cualquier lado. Tampoco decía si se podía citar solo una parte de un estándar, ni qué pasaba con un
estándar del que solo se querían una o dos reglas: citarlo hacía pensar que se cumplía entero.

## Decisión

Reemplaza los puntos 2, 3, 4, 5 y 9 del ADR-0018.

1. Se cita lo que se adopta en su mayoría. Todo lo demás, venga de donde venga, es una regla propia.
2. Citar una fuente, o una parte de ella, adopta todas sus convenciones: se cumplen sin escribirlas.
   La página anota solo las que contradice, deja sin efecto o endurece.
3. Para cada asunto se busca una fuente en este orden, y se prefiere la de menor número:
   1. El texto normativo de un estándar de la tecnología y la recomendación escrita en su
      documentación.
   2. Un estándar de un campo, como OWASP, NIST o ISO.
   3. Una especificación de facto, como SemVer o The Twelve-Factor App.
   4. Una guía publicada por una organización de referencia, como Google AIP.
4. Elegir una fuente de mayor número en un asunto que otra de menor número ya cubre es contradecir
   a esa otra, y se anota con su razón.
5. Se cita una fuente entera o solo una de sus partes numeradas, si se adopta en su mayoría. Las
   reglas que se toman sueltas de una fuente se escriben como propias, sin nombrar de dónde salen.
6. Dos partes citadas nunca regulan lo mismo. Si dos fuentes chocan, se cita solo la que mejor se
   adapta, o se dice qué secciones se aplican de cada una.
7. `fuentes/` guarda el texto de cada fuente citada, sea del nivel que sea, y nada más.
8. Nunca se citan el código de los ejemplos, los proyectos de muestra, lo que hace la comunidad, la
   popularidad, los blogs, los cursos ni los foros. Una convención que sale de ahí entra como
   propia.
9. Sobre sus fuentes, la página escribe solo la opción que elige donde una fuente deja varias, lo
   que contradice o endurece, y sus reglas propias.

## Consecuencias

- Una cita dice exactamente lo que se cumple: quien lee la página no tiene que adivinar qué parte
  de una fuente rige.
- `fuentes/` puede guardar guías que no son estándares.
- Las citas actuales de `plataformas/` se revisan contra este criterio: una fuente que hoy se cita
  y se usa solo en parte pasa a reglas propias.

## Descartado

- **Citar solo los niveles 1 y 2:** lo que ninguno cubre quedaba sin fuente aunque una guía de
  referencia lo resolviera bien.
- **Que entre dos fuentes que chocan mande la de menor número:** la contradicción quedaba en la
  página y quien lee tendría que conocer la regla de prioridad para saber qué se cumple.
- **Nombrar la fuente de una regla tomada suelta:** haría pensar que la fuente está adoptada.
- **Citar un estándar del que se usa una parte y anotar el resto como excepción:** la lista de
  excepciones sería más larga que lo adoptado.
