# Plataformas

Una página por tecnología, y [transversal.md](transversal.md) con lo que cumplen juntas varias
piezas. **Se lee la de lo que el repositorio use**, junto con transversal.md; las demás no aplican.

| Página | Cubre |
|---|---|
| [transversal.md](transversal.md) | Lo que tienen que cumplir juntas varias piezas |
| [python.md](python.md) | Lo común a toda pieza en Python |
| [fastapi.md](fastapi.md) | Un servidor en FastAPI |
| [postgres.md](postgres.md) | La base de datos |
| [sveltekit.md](sveltekit.md) | Una superficie web con SvelteKit y UnoCSS |
| [flutter.md](flutter.md) | Una app en Flutter |
| [android.md](android.md) | Una app de Android en Kotlin y Jetpack Compose |
| [flet.md](flet.md) | Una aplicación en Flet |
| [qt.md](qt.md) | Una aplicación de escritorio con Qt Widgets y PySide6 |
| [despliegue.md](despliegue.md) | Cómo queda el servidor |

## Qué es una página

Un catálogo de convenciones de una tecnología. Una convención la adopta una fuente citada o la
escribe la página como regla, y sirve para una de tres cosas:

- **Que todos los repositorios se lean igual:** el mismo layout y los mismos nombres.
- **Que cada elección se tome una sola vez:** la tecnología, la biblioteca, la versión y la
  configuración.
- **Que las piezas de un sistema se entiendan:** el servidor y sus clientes cumplen el mismo
  contrato, como el sobre de error, la paginación o la sesión.

Una convención que no sirve para ninguna de las tres no va, y una que sirve vale aunque ninguna
herramienta la haga cumplir.

### Qué puede ser fuente

Una revisión empieza por la lista de lo que la tecnología obliga a decidir. Cada punto se responde
con una fuente citada o, si ninguna lo cubre, con una regla propia. Una fuente, o la parte que se
cita, cumple los siete requisitos:

1. **Normativa:** dice qué se debe, se debería o no se debe hacer. Cada frase citada se puede
   reescribir como «se usa X» o «no se hace Y». Los pasos, los ejemplos y las explicaciones no
   cuentan, aunque estén en la documentación oficial.
2. **Decide algo:** responde a un punto de la lista de lo que hay que decidir.
3. **Autoridad:** la escribe quien define la tecnología, o un organismo, para que otros la
   adopten: un estándar, una especificación, una guía de estilo oficial, OWASP o NIST. Un
   tutorial, el código de los ejemplos, un proyecto de muestra, un blog, un curso, un foro, lo que
   hace la comunidad o la popularidad no.
4. **Acotada:** la parte citada se puede leer entera al escribir el código de su sección, salvo que
   su fuente sea de conocimiento general, como PEP 8 o SemVer, o que una herramienta de «Cómo se
   hace cumplir» la verifique.
5. **Fija:** tiene versión o fecha y corresponde a la versión de la tecnología que se usa. La copia
   de [fuentes/](../fuentes/) congela esa versión.
6. **Con licencia:** su licencia permite copiar el texto en `fuentes/`.
7. **Independiente:** la parte citada no depende de la infraestructura de quien la publica.

Si dos fuentes que cumplen los siete requisitos regulan lo mismo, se cita la de menor orden y, a
igual orden, la que cubre más del asunto:

| Orden | Fuente |
|---|---|
| 1 | Un estándar de la tecnología y la recomendación escrita en su documentación |
| 2 | Un estándar de un campo, como OWASP, NIST o ISO |
| 3 | Una especificación de facto, como SemVer, Conventional Commits o The Twelve-Factor App |
| 4 | Una guía de una organización de referencia, como Google AIP o las guías de API de Microsoft |

### Qué implica citar

- Se cita lo que se adopta en su mayoría: una fuente entera o solo una parte, como una sección, un
  capítulo, una AIP o un nivel de ASVS. Todo lo demás, venga de donde venga, es una regla propia.
- Citar una fuente, o una parte de ella, adopta todas sus convenciones explícitas: lo que se debe,
  se debería o no se debe hacer, aunque nada lo haga cumplir. Se cumplen como si fueran
  obligatorias.
- Dos partes citadas nunca regulan lo mismo. Si dos fuentes chocan en un asunto, se cita solo la
  que mejor se adapta, o se dice qué secciones se aplican de cada una.
- Lo que una herramienta hace por defecto no viene de ninguna fuente, pero rige mientras la página
  no diga otra cosa. Cambiarlo es una regla propia, salvo que una fuente citada pida el cambio.
- Una regla propia no nombra una fuente que la página no cita, tampoco para contradecirla: lleva
  solo su razón.
- Cada sección nombra las partes que cita y enlaza su texto en `fuentes/`, que guarda solo lo que
  se cita. Una fuente que rige varias secciones se cita en cada una solo con la parte que la rige,
  y ninguna parte se cita en dos secciones.

### Qué escribe la página

La página escribe solo tres clases de reglas:

- La opción que elige donde una fuente deja varias.
- Lo que contradice, deja sin efecto o endurece de una fuente. Endurecer es volver obligatorio lo
  que la fuente recomienda «cuando sea posible» o deja como preferencia.
- Sus reglas propias: las que no se apoyan en ninguna fuente citada.

Cómo se escribe:

- Cada regla dice qué se usa y cómo queda. No es un procedimiento ni un tutorial.
- Dos reglas de una página no chocan: una que deja casos fuera de otra los nombra.
- Una regla lleva razón, en una frase corta, solo en dos casos: por qué contradice, deja sin efecto
  o endurece una fuente, y cómo ayuda una elección que no es trivial. Una regla trivial, como un
  color o el largo de línea, no lleva razón: es una preferencia. Fuera de la razón, sin
  comentarios, explicaciones ni ejemplos innecesarios. Vale también para los comentarios de
  `plantilla/`.
- El layout se dibuja completo, como árbol, aunque repita partes de sus fuentes. El árbol es la
  convención misma, y a pedazos no se lee.
- Debajo del árbol va solo dónde va algo que podría ir en otro archivo. Lo que un archivo tiene por
  su nombre, por su fuente o por otra sección de la página no se escribe.

### Orden de las secciones

Las secciones van en siete bloques, en este orden. Una página escribe solo los bloques que tiene.

| Bloque | Qué va |
|---|---|
| Proyecto | La sección `Proyecto`, con la versión, el build, el árbol y la plantilla, y después las dependencias |
| Código | El formato, el analizador, los tipos, los paquetes y los nombres |
| Arquitectura | Cómo se organiza la pieza por dentro con su framework |
| Temas | Una sección por asunto, en orden alfabético del título |
| Pruebas | La sección `Pruebas` |
| Entrega | Cómo se construye y se sirve la pieza |
| Cómo se hace cumplir | La tabla |

- En Código y Arquitectura, una sección va después de las que necesita para leerse.
- Los temas van en orden alfabético: un tema que aparece en varias páginas queda en el mismo
  orden en todas.
- Un título nombra lo mismo en todas las páginas.

### Cómo se hace cumplir

- La tabla «Cómo se hace cumplir» nombra en su primera columna la fuente o la parte citada, o
  una regla que la página ya escribió. Nunca redacta una regla nueva para llenar la fila.
- Una herramienta que marca más de lo que dice su fila impone una convención no escrita, y no va.
- Las herramientas de una fila hacen cumplir todo lo que nombra su primera columna.

### Alcance

- Hereda de su página madre y no repite nada de ella: `fastapi.md`, `flet.md` y `qt.md` heredan de
  `python.md`.
- Dice solo lo que hace su pieza. Lo que tienen que cumplir juntas varias piezas va en
  [transversal.md](transversal.md), y la sección de cada pieza que lo implementa enlaza ahí: quien
  trabaja en una pieza encuentra sus reglas en su página.
- Nombra los archivos de `plantilla/` que salen de ella.
- No dice qué repositorio la usa ni cuándo elegir una plataforma sobre otra.

### Cómo se revisa

Una revisión da un veredicto sobre cada fuente citada, cada regla y cada fila de «Cómo se hace
cumplir», contra los criterios de este archivo, y no solo sobre lo que encuentra mal: lo que no se
evaluó queda a la vista.

- Cada veredicto lleva su evidencia: comprobado, con el comando que lo reproduce; leído, con la
  línea de la fuente, o sin confirmar.
- Lo que marca una herramienta se comprueba con un experimento, no de memoria.

### De dónde se escribe

Ni el código de los repositorios, ni lo que la página ya dice, ni los ADR son fuente. Una página se
escribe de cero desde sus fuentes, nunca corrigiendo la versión anterior.

El porqué, en el [ADR-0018](../adr/0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md),
el [ADR-0028](../adr/0028-una-pagina-esta-completa-cuando-sus-estandares-cubren-lo-que-hay-que-decidir.md),
el [ADR-0029](../adr/0029-las-secciones-de-una-pagina-van-en-bloques-fijos-y-los-temas-en-orden-alfabetico.md),
el [ADR-0030](../adr/0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md),
el [ADR-0031](../adr/0031-una-revision-empieza-por-lo-que-la-tecnologia-obliga-a-decidir.md),
el [ADR-0032](../adr/0032-una-guia-de-una-organizacion-se-cita-si-se-escribio-para-que-otros-la-adopten.md),
el [ADR-0051](../adr/0051-un-tutorial-no-se-cita-y-lo-que-se-toma-de-el-es-regla-propia.md),
el [ADR-0056](../adr/0056-una-regla-es-lo-que-escribe-la-pagina-y-lo-que-adopta-una-fuente-es-una-convencion.md)
el [ADR-0063](../adr/0063-una-fuente-cumple-siete-requisitos-y-su-texto-se-lee-al-escribir-codigo.md)
y el [ADR-0064](../adr/0064-una-revision-da-un-veredicto-con-evidencia-sobre-cada-regla-fuente-y-fila.md).
