# ADR-0016 · Una página de plataforma es un catálogo de convenciones que sale de la recomendación oficial

- **Estado:** Aceptada
- **Fecha:** 2026-09-26
- **Alcance:** `plataformas/` y los archivos de `plantilla/` que rige cada página

## Contexto

Reemplaza al [ADR-0014](0014-una-pagina-se-escribe-desde-la-recomendacion-oficial.md), que fijaba
la fuente de una página —la recomendación oficial, no el código— pero no su forma. Las páginas
se llenaron de explicaciones de lo que la documentación oficial ya dice, repiten reglas de su página
madre y conservan reglas que salieron de los repositorios o de lo que la propia página ya decía. Al
revisarlas se tomó como «oficial» cualquier cosa publicada por la tecnología: su texto, el código
de sus ejemplos y sus proyectos de muestra.

## Decisión

1. Una página es un catálogo de convenciones: qué se usa y cómo queda. No es un procedimiento ni un
   tutorial. Una convención sirve para que todos los repositorios se lean igual, para que cada
   elección se tome una sola vez o para que las piezas de un sistema se entiendan. Una regla que no
   sirve para ninguna de las tres no va.
2. La fuente es la recomendación oficial más reciente de la tecnología. Una regla propia va solo
   donde lo oficial tiene una deficiencia, no existe o deja la elección abierta.
3. Ni el código de los repositorios ni lo que la página ya dice son fuente. Lo que un repositorio
   hace distinto va a [homologacion.md](../homologacion.md).
4. Sin comentarios ni explicaciones, salvo dos, cada una en una frase corta: por qué una regla se
   aparta de la recomendación oficial, y cómo ayuda una elección que no es trivial. Una elección
   trivial, como un color, no lleva frase. Vale también para los comentarios de los archivos de
   `plantilla/`.
5. Una página hereda de su página madre y no repite nada de ella: `fastapi.md`, `flet.md` y `qt.md`
   heredan de `python.md`.
6. Cada sección nombra el estándar del que sale.
7. Qué cuenta como recomendación oficial:

   | Fuente | ¿Oficial? |
   |---|---|
   | El texto normativo de un estándar: MUST, SHOULD o RECOMMENDED de un RFC, una PEP o una especificación del W3C | Sí |
   | Una recomendación explícita en el texto de la documentación de la tecnología | Sí |
   | Todo lo demás: el código de los ejemplos, los proyectos de muestra, lo que hace la comunidad, una preferencia | No. Una regla que sale de ahí es propia |

   El comportamiento por defecto de una herramienta no es una recomendación. Si la página no dice
   nada, rige; cambiarlo es oficial solo si la documentación lo pide.

## Consecuencias

- Cada página se revisa contra estos puntos.
- Una página puede exigir algo que ningún repositorio cumple hoy. Eso no es un defecto de la página.

## Descartado

- **Conservar el ADR-0014 y sumar otro para la forma:** serían dos ADR para decidir qué es una
  página.
- **Explicar cada regla:** la explicación de una regla oficial repite la documentación y se queda
  vieja cuando esta cambia.
