# ADR-0018 · Una página se revisa contra la copia de sus estándares y solo dice lo que elige, endurece o no cubren

- **Estado:** Aceptada. Los puntos 2, 3, 4, 5 y 9 los reemplaza el [ADR-0030](0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md), y el punto 6, en lo que deja sin efecto, el [ADR-0056](0056-una-regla-es-lo-que-escribe-la-pagina-y-lo-que-adopta-una-fuente-es-una-convencion.md)
- **Fecha:** 2026-09-27
- **Alcance:** `plataformas/`, `fuentes/` y los archivos de `plantilla/` que rige cada página

## Contexto

Reemplaza al [ADR-0016](0016-una-pagina-es-un-catalogo-de-convenciones-que-sale-de-la-recomendacion-oficial.md),
que pedía nombrar el estándar de cada sección y no repetir la documentación oficial. Después de
varias revisiones, `python.md`, `qt.md` y `fastapi.md` seguían copiando reglas de sus estándares:
al compararlas con el texto oficial aparecieron doce, como `UPPER_CASE` para las constantes, que ya
está en PEP 8, o `@Slot`, que ya recomienda Qt for Python. Las revisiones se hacían de memoria, sin
el texto delante, y el ADR-0016 no decía si volver obligatorio lo que un estándar solo recomienda
era elegir o repetir.

## Decisión

1. Una página es un catálogo de convenciones: qué se usa y cómo queda. No es un procedimiento ni un
   tutorial. Una convención sirve para que todos los repositorios se lean igual, para que cada
   elección se tome una sola vez o para que las piezas de un sistema se entiendan. Una regla que no
   sirve para ninguna de las tres no va.
2. La fuente es la recomendación oficial más reciente de la tecnología. Ni el código de los
   repositorios ni lo que la página ya dice son fuente.
3. `fuentes/` guarda el texto de cada estándar que siguen las páginas, sin editar, con la URL de
   origen de cada archivo en su `README.md`. Una página web se guarda convertida a Markdown. Una
   página se escribe y se revisa contra ese texto.
4. Cada sección nombra los estándares que sigue y enlaza su copia. Lo que el estándar dice no se
   escribe. Citarlo adopta sus recomendaciones: lo que recomienda se hace como si fuera
   obligatorio, sin escribirlo.
5. Sobre el estándar, la página escribe solo tres cosas: la opción que elige donde el estándar deja
   varias, lo que contradice o endurece, y lo que ningún estándar cubre. Endurecer es volver
   obligatorio lo que el estándar recomienda «cuando sea posible» o deja como preferencia.
6. Sin comentarios ni explicaciones, salvo dos, cada una en una frase corta: por qué la página
   contradice o endurece el estándar, y cómo ayuda una elección que no es trivial. Una regla
   trivial, como un color o el largo de línea, no lleva frase: su razón es una preferencia. Vale
   también para los comentarios de los archivos de `plantilla/`.
7. La tabla «Cómo se hace cumplir» nombra el estándar o su sección, o una regla que la página ya
   escribió. Nunca redacta una regla para llenar la fila.
8. Una página hereda de su página madre y no repite nada de ella: `fastapi.md`, `flet.md` y `qt.md`
   heredan de `python.md`.
9. Qué cuenta como recomendación oficial:

   | Fuente | ¿Oficial? |
   |---|---|
   | El texto normativo de un estándar: MUST, SHOULD o RECOMMENDED de un RFC, una PEP o una especificación del W3C | Sí |
   | Una recomendación explícita en el texto de la documentación de la tecnología | Sí |
   | Todo lo demás: el código de los ejemplos, los proyectos de muestra, lo que hace la comunidad, una preferencia | No. Una regla que sale de ahí es propia |

   El comportamiento por defecto de una herramienta no es una recomendación. Si la página no dice
   nada, rige; cambiarlo es oficial solo si la documentación lo pide.

## Consecuencias

- El repositorio carga unos 8 MB de texto ajeno.
- Una copia envejece cuando su fuente cambia. Se actualiza descargándola de nuevo, y `git diff`
  muestra qué cambió en el estándar.
- Un estándar que ninguna página cita se borra.

## Descartado

- **Enlazar la fuente sin copiarla:** el texto no queda a mano y la revisión se sigue haciendo de
  memoria.
- **Sumar un ADR al 0016 en vez de reemplazarlo:** serían dos ADR para decidir qué es una página.
- **Escribir cada recomendación que se sigue:** el estándar y su resumen serían dos fuentes de
  verdad, y una recomendación sin copiar quedaría en duda.
