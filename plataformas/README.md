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

Un catálogo de convenciones de una tecnología. Una convención sirve para una de tres cosas:

- **Que todos los repositorios se lean igual:** el mismo layout y los mismos nombres.
- **Que cada elección se tome una sola vez:** la tecnología, la biblioteca, la versión y la
  configuración.
- **Que las piezas de un sistema se entiendan:** el servidor y sus clientes cumplen el mismo
  contrato, como el sobre de error, los nombres en el cable o la sesión.

Una regla que no sirve para ninguna de las tres no va. Una convención vale aunque ninguna
herramienta la haga cumplir.

### Las fuentes son las convenciones

- Se cita lo que se adopta en su mayoría. Todo lo demás, venga de donde venga, es una regla propia.
- Citar una fuente, o una parte de ella, adopta todas sus convenciones: se cumplen como si fueran
  obligatorias y no se escriben. La página anota solo las que contradice, deja sin efecto o
  endurece; el resto sigue rigiendo.
- Para cada asunto se busca una fuente en este orden, y se prefiere la de menor número:

  | Orden | Fuente |
  |---|---|
  | 1 | El texto normativo de un estándar de la tecnología (MUST, SHOULD o RECOMMENDED) y la recomendación escrita en su documentación, en su versión más reciente |
  | 2 | Un estándar de un campo, como OWASP, NIST o ISO |
  | 3 | Una especificación de facto, como SemVer, Conventional Commits o The Twelve-Factor App |
  | 4 | Una guía publicada por una organización de referencia, como Google AIP o las guías de API de Zalando o de Microsoft |

- Una guía de orden 4 se cita solo si se escribió para que otros la adopten:
  - Es pública y su licencia permite usarla.
  - Es normativa: reglas numeradas con MUST o SHOULD, no consejos sueltos.
  - Está versionada, con historial de cambios. La copia de `estandares/` fija la versión adoptada.
  - La parte citada no depende de la infraestructura de quien la publica.
- Elegir una fuente de mayor número en un asunto que otra de menor número ya cubre es contradecir
  a esa otra, y se anota con su razón.
- Se cita una fuente entera o solo la parte que se adopta: una sección, un capítulo, una AIP o un
  nivel de ASVS.
- Una parte se cita si se adopta en su mayoría. Si de ella solo se toman algunas reglas, no se
  cita: esas reglas se escriben como propias, sin nombrar de dónde salen.
- Una regla propia no nombra una fuente que la página no cita, tampoco para contradecirla: lleva
  solo su razón.
- Dos partes citadas nunca regulan lo mismo. Si dos fuentes chocan en un asunto, se cita solo la
  que mejor se adapta, o se dice qué secciones se aplican de cada una.
- Una fuente que rige varias secciones de la página se cita en cada una solo con la parte que la
  rige, y ninguna parte se cita en dos secciones.
- Cada sección nombra las fuentes que cita y enlaza su texto en [estandares/](../estandares/). Ahí
  se guarda solo lo que se cita.
- Nunca se citan el código de los ejemplos, los proyectos de muestra, lo que hace la comunidad, la
  popularidad, los blogs, los cursos ni los foros. Una convención que sale de ahí entra como
  propia.
- Lo que una herramienta hace por defecto no viene de ninguna fuente, pero rige mientras la página
  no diga otra cosa. Cambiarlo es una regla propia, salvo que una fuente citada pida el cambio.
- Una revisión empieza por la lista de lo que la tecnología obliga a decidir. Cada punto se
  responde con una fuente citada o, si ninguna lo cubre, con una regla propia.

### Qué escribe la página

Sobre sus fuentes, solo tres cosas. Una sección sin puntos sigue enteras las partes que cita.

- La opción que elige donde una fuente deja varias.
- Lo que contradice o endurece de una fuente. Endurecer es volver obligatorio lo que la fuente
  recomienda «cuando sea posible» o deja como preferencia.
- Sus reglas propias.

Cómo se escribe:

- Cada regla dice qué se usa y cómo queda. No es un procedimiento ni un tutorial.
- Sin comentarios ni explicaciones, salvo dos, cada una en una frase corta: por qué la página
  contradice o endurece una fuente, y cómo ayuda una elección que no es trivial. Una regla trivial,
  como un color o el largo de línea, no lleva frase: su razón es una preferencia. Vale también para
  los comentarios de `plantilla/`.
- El layout se dibuja completo, como árbol, aunque repita partes de sus fuentes. El árbol es la
  convención misma, y a pedazos no se lee.

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
- Una herramienta que marca más de lo que la regla dice impone una regla no escrita, y no va.

### Alcance

- Hereda de su página madre y no repite nada de ella: `fastapi.md`, `flet.md` y `qt.md` heredan de
  `python.md`.
- Dice solo lo que hace su pieza. Lo que tienen que cumplir juntas varias piezas va en
  [transversal.md](transversal.md), y la sección de cada pieza que lo implementa enlaza ahí: quien
  trabaja en una pieza encuentra sus reglas en su página.
- Nombra los archivos de `plantilla/` que salen de ella.
- No dice qué repositorio la usa ni cuándo elegir una plataforma sobre otra.

### Fuentes

Ni el código de los repositorios, ni lo que la página ya dice, ni los ADR son fuente. Una página se
escribe de cero desde sus fuentes, nunca corrigiendo la versión anterior.

Se agrega una página cuando la tecnología se estrena en algún repositorio.

El porqué, en el [ADR-0018](../adr/0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md),
el [ADR-0028](../adr/0028-una-pagina-esta-completa-cuando-sus-estandares-cubren-lo-que-hay-que-decidir.md),
el [ADR-0029](../adr/0029-las-secciones-de-una-pagina-van-en-bloques-fijos-y-los-temas-en-orden-alfabetico.md),
el [ADR-0030](../adr/0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md),
el [ADR-0031](../adr/0031-una-revision-empieza-por-lo-que-la-tecnologia-obliga-a-decidir.md)
y el [ADR-0032](../adr/0032-una-guia-de-una-organizacion-se-cita-si-se-escribio-para-que-otros-la-adopten.md).
