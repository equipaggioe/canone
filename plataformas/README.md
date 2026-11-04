# Plataformas

Cada página reúne las convenciones de una tecnología o ámbito de implementación. `transversal.md` reúne las que deben cumplir conjuntamente varias piezas de un sistema.

Para trabajar en una pieza se consulta su página, su página madre si la tiene y las secciones de `transversal.md` que esas páginas enlazan. Las demás páginas no aplican.

## Terminología

- **Ámbito:** área de implementación que agrupa convenciones aplicables a distintas tecnologías o piezas.
- **Convención:** criterio que determina cómo se construyen, organizan o integran las piezas de un sistema.
- **Convención adoptada:** convención establecida por una fuente normativa externa que Canone incorpora y aplica dentro del alcance indicado.
- **Convención propia:** convención establecida directamente por Canone porque ninguna fuente adoptada resuelve esa decisión, o porque es necesario elegir o modificar lo que establecen las fuentes.
- **Entrada:** elemento independiente de una fuente compuesta por elementos que pueden adoptarse individualmente.
- **Fuente normativa:** documento externo que establece convenciones que pueden adoptarse.
- **Material de referencia:** lista de nombres o valores que utiliza una convención, como un registro, sin ser una fuente normativa.
- **Parte:** título de una fuente con todo su contenido subordinado. Si el título se repite, se identifica también el título que lo contiene. Cuando un mismo apartado abarca asuntos de secciones distintas, puede identificarse el párrafo que corresponde a cada una.
- **Pieza:** componente identificable de un sistema que tiene una responsabilidad y puede documentarse por separado.
- **Tecnología:** herramienta, lenguaje, framework, plataforma o sistema concreto utilizado para implementar una pieza.

## Páginas

| Página | Cubre |
| :--- | :--- |
| [transversal.md](transversal.md) | Lo que deben cumplir conjuntamente varias piezas |
| [python.md](python.md) | Lo común a todas las piezas implementadas en Python |
| [fastapi.md](fastapi.md) | Un servidor en FastAPI |
| [postgres.md](postgres.md) | La base de datos |
| [sveltekit.md](sveltekit.md) | Una superficie web con SvelteKit y UnoCSS |
| [flutter.md](flutter.md) | Una aplicación en Flutter |
| [android.md](android.md) | Una aplicación de Android con Kotlin y Jetpack Compose |
| [flet.md](flet.md) | Una aplicación en Flet |
| [qt.md](qt.md) | Una aplicación de escritorio con Qt Widgets y PySide6 |
| [despliegue.md](despliegue.md) | La configuración del servidor |

## Función de las páginas

Una página es un catálogo de convenciones de una tecnología o ámbito. Cada convención es adoptada de una fuente citada o establecida directamente por Canone.

Las convenciones sirven para tres propósitos:

- **Uniformidad:** que los repositorios se organicen y se lean de la misma manera, con los mismos nombres y estructuras.
- **Decisiones comunes:** que las elecciones sobre tecnologías, bibliotecas, versiones y configuraciones se tomen una sola vez.
- **Contratos entre piezas:** que los componentes de un sistema se entiendan y cumplan las mismas condiciones, como el formato de error, la paginación o la sesión.

Una convención que no contribuye a ninguno de estos propósitos no se incluye. Su utilidad no depende de que alguna herramienta pueda hacerla cumplir.

### Selección de fuentes

La revisión empieza por identificar qué decisiones obliga a tomar la tecnología. Cada punto se resuelve adoptando una convención de una fuente normativa o, si ninguna fuente adecuada lo cubre, estableciendo una convención propia.

Una fuente debe cumplir los ocho requisitos siguientes:

1. **Normativa:** establece qué se debe, se debería o no se debe hacer. Cada enunciado citado debe poder expresarse como «se usa X» o «no se hace Y». Los procedimientos, ejemplos y explicaciones no cuentan, aunque aparezcan en la documentación oficial.
2. **Decide algo:** responde a uno de los puntos que deben resolverse para la tecnología o ámbito.
3. **Autoridad:** procede de quien define la tecnología o de un organismo que publica criterios para que otros los adopten: un estándar, una especificación, una guía de estilo oficial, OWASP o NIST. No cuentan los tutoriales, ejemplos de código, proyectos de muestra, blogs, cursos, foros, prácticas de la comunidad ni la popularidad.
4. **Acotada:** el contenido citado puede leerse completo al escribir el código al que aplica. Se exceptúan las fuentes de conocimiento general, como PEP 8 o SemVer, y aquellas cuyo cumplimiento verifica una herramienta de la sección «Cumplimiento».
5. **De la versión en uso:** corresponde a la versión de la tecnología utilizada. La copia conservada en `fuentes/` fija el texto que se adopta.
6. **Independiente:** las convenciones adoptadas no dependen de la infraestructura de quien publica la fuente.
7. **Cubre:** una fuente citada entera debe resolver la mayoría de las decisiones de los asuntos que regula, considerando conjuntamente lo que adoptan todas las páginas. En esos asuntos, lo no cubierto debe quedar en minoría. Lo que se contradice, se deja sin efecto o se dirige a otro actor no cuenta como cubierto. Si una fuente no cumple este requisito, no se cita y las convenciones que se aprovechen de ella se establecen como convenciones propias.
8. **Aporta:** evita escribir al menos tres convenciones, contando todas las páginas que la citan. Cuenta cada enunciado o entrada que se cumple sin que una página lo escriba. No cuenta lo que una página escribe de todos modos, como una elección o lo que endurece, ni lo que deja sin efecto o se dirige a otro actor. Si no llega a tres, no se cita y sus convenciones se escriben como propias.

Si varias fuentes que cumplen los ocho requisitos regulan el mismo asunto, se prefiere la que tenga mayor prioridad en la tabla. A igual prioridad, se elige la que cubra una parte mayor del asunto.

| Orden | Fuente |
| :--- | :--- |
| 1 | Un estándar de la tecnología o una recomendación publicada en su documentación |
| 2 | Un estándar de un campo, como OWASP, NIST o ISO |
| 3 | Una especificación de facto, como SemVer, Conventional Commits o The Twelve-Factor App |
| 4 | Una guía de una organización de referencia, como Google AIP o las guías de API de Microsoft |

Este orden da preferencia a lo que publica quien define la tecnología:

- **Conocimiento especializado:** quien define la tecnología suele conocerla mejor, y sus propuestas pasan por la revisión de una comunidad amplia antes de publicarse.
- **Compatibilidad con las herramientas:** los formateadores, analizadores y frameworks suelen construirse sobre esas convenciones. Adoptarlas requiere menos configuración y evita sorpresas.
- **Vigencia:** sus recomendaciones evolucionan junto con la tecnología, mientras que una convención propia puede quedar obsoleta sin que se advierta.
- **Conocimiento compartido:** quienes ya conocen la tecnología, incluidas las personas que se incorporan al proyecto, suelen conocer también sus convenciones oficiales.

### Adopción de fuentes

Citar una fuente significa adoptar sus convenciones explícitas dentro del alcance citado: lo que indica que se debe, se debería o no se debe hacer. Se aplican como obligatorias, incluso cuando ninguna herramienta las hace cumplir.

#### Unidad y alcance de la cita

- Una fuente se cita entera o por entradas:
  - **Entera:** cuando presenta un enfoque o conjunto de convenciones sobre un asunto. Se adopta todo su contenido, menos lo que una página deje sin efecto.
  - **Por entradas:** cuando ofrece opciones independientes, como `systemd.exec` o `sshd_config`. Se citan las entradas utilizadas.
- [fuentes/README.md](../fuentes/README.md) registra si cada fuente se cita entera o por entradas.
- La unidad de cita es el contenido publicado en una URL propia, sin contar el fragmento de la dirección. Puede ser un documento, una referencia, una cheat sheet, un PEP o un capítulo de un estándar o manual. No es el organismo que lo publica ni necesariamente el manual completo.

#### Distribución entre secciones

- Las obligaciones dirigidas a otro actor no se adoptan como convenciones de la pieza. Por ejemplo, no se trasladan las instrucciones dirigidas a quienes desarrollan una herramienta que el producto utiliza, como coturn, Uvicorn o un navegador, ni las dirigidas a la otra parte de un protocolo, como el servicio de push de Web Push. Sí se adoptan las opciones que la herramienta deja a quien la configura, como los destinos a los que coturn niega relevar.
- Una fuente citada entera puede contener convenciones que correspondan a varias secciones. La cita entera aparece en una sola sección. Cada sección identifica las partes que le corresponden, porque son las que deben consultarse al escribir el código de esa sección.
- Cada parte que contiene convenciones rige en una sola sección, de cualquier página. Si una parte no se sigue, se deja sin efecto en la sección a la que pertenece y se indica la razón.
- Dos partes citadas no deben regular lo mismo. Si dos fuentes entran en conflicto sobre un asunto, se elige la que mejor se adapta o se deja sin efecto la parte conflictiva de una de ellas.

#### Convenciones propias y valores predeterminados

- Los valores predeterminados de una herramienta no proceden de una fuente citada, pero rigen mientras la página no establezca otra cosa. Cambiarlos constituye una convención propia, salvo que una fuente citada exija el cambio.
- Una convención propia no menciona fuentes que la página no cita, ni siquiera para contradecirlas. Incluye únicamente la convención y, cuando corresponda, su razón.
- Una convención que utiliza material de referencia indica de dónde lo obtiene. Enlaza su copia en `fuentes/` si un programa de Canone toma valores de él, y su URL pública si no.

#### Enlaces y verificación de citas

- Cada sección enlaza en `fuentes/` la copia del contenido que cita. Identifica cada parte por su título en cursiva o por su entrada entre comillas invertidas, antes o después del enlace. Por ejemplo: «las secciones *A* y *B* de [X]» o «[X], la sección *A*».
- La cita va en un párrafo propio que empieza por `Estándar:` o `Estándares:`; `scripts/verificar.py --canone` solo revisa esos párrafos.
- Cuando no se indican partes, la cita abarca la fuente entera. Las partes de esa fuente que rigen en otras secciones se indican después de «salvo».
- `scripts/verificar.py --canone` comprueba en CI que:
  - Cada fuente citada tenga su campo «Cita».
  - Las fuentes citadas por entradas indiquen las entradas adoptadas.
  - Las fuentes citadas enteras aparezcan como tales en una sola sección e indiquen con «salvo» las partes que rigen en otras.
  - Ninguna parte rija en más de una sección.
  - No se cite una lista de nombres como si fuera una fuente.

## Convenciones de la página

La página no vuelve a redactar las convenciones que adopta de sus fuentes. Solo establece las convenciones propias necesarias para completar las adoptadas y fijar las decisiones del proyecto.

Las convenciones propias se establecen en tres casos:

1. **Elecciones:** se selecciona una opción cuando una fuente permite varias.
2. **Excepciones:** se contradice, deja sin efecto o endurece una convención adoptada. Endurecer significa convertir en obligatorio lo que la fuente recomienda como preferencia o condiciona a que sea posible.
3. **Decisiones no cubiertas:** se establecen convenciones sobre asuntos que ninguna fuente citada resuelve.

### Redacción

- Cada convención expresa qué se utiliza y cómo queda. No describe procedimientos ni explica cómo hacerlo.
- Las convenciones de una misma página no deben contradecirse. Si una convención modifica el alcance de otra, debe indicar expresamente qué casos quedan fuera.
- Una convención incluye una justificación breve únicamente cuando contradice, deja sin efecto o endurece una fuente, o cuando explica una elección cuyo motivo no resulta evidente. Las preferencias triviales, como un color o el largo de línea, no llevan justificación.
- No se añaden comentarios, explicaciones ni ejemplos que no sean necesarios para entender o aplicar la convención.

### Estructuras y distribución

- Las estructuras, como el árbol de directorios, se muestran completas, aunque reproduzcan convenciones de sus fuentes. La estructura completa es la convención que debe seguirse.
- Después de una estructura solo se especifica dónde colocar los elementos que podrían ubicarse en más de un archivo.
- No se repite información que ya queda determinada por el nombre de un archivo, una fuente citada u otra sección.

Estos mismos criterios de redacción se aplican a los comentarios incluidos en `plantilla/`.

## Orden de las secciones

Las secciones de una página siguen este orden. Se incluyen únicamente los bloques que correspondan a la tecnología o ámbito documentado.

1. **Proyecto:** la sección `Proyecto`, con versión, sistema de construcción, estructura de directorios y plantillas, y después las dependencias.
2. **Código:** formato, análisis estático, tipado, organización de paquetes y convenciones de nombres.
3. **Arquitectura:** organización interna de la aplicación y uso de las estructuras o mecanismos propios de la tecnología.
4. **Temas:** convenciones agrupadas por asunto, con los temas en orden alfabético.
5. **Pruebas:** la sección `Pruebas`, con herramientas, organización y convenciones de pruebas.
6. **Entrega:** construcción, ejecución y preparación para el despliegue.
7. **Cumplimiento:** herramientas que verifican o imponen las convenciones documentadas.

### Criterios de orden

- En **Código** y **Arquitectura**, las secciones se ordenan según sus dependencias: primero se describe lo necesario para comprender las secciones posteriores.
- Los temas de **Temas** se presentan en orden alfabético.
- Cuando un mismo asunto aparece en distintas páginas, conserva el mismo título y ubicación relativa siempre que corresponda al mismo bloque.

## Cumplimiento

Esta sección registra las herramientas que verifican o hacen cumplir las convenciones definidas en la página.

Se utiliza una tabla con estas columnas:

| Convención | Herramienta |
| :--- | :--- |
| Fuente, parte citada o convención propia que se hace cumplir | Herramienta que la verifica o impone |

### Criterios

- Cada fila debe referirse a una fuente, parte citada o convención propia ya documentada en la página. La tabla no introduce convenciones nuevas.
- La herramienta debe hacer cumplir todo lo indicado en la primera columna.
- Una herramienta que imponga convenciones adicionales a las documentadas en esa fila no se incluye. No debe introducir requisitos que la página no haya establecido.

## Alcance

- Una página con página madre hereda sus convenciones. No debe repetirlas; únicamente documenta las particularidades de su ámbito. Por ejemplo, `fastapi.md`, `flet.md` y `qt.md` heredan de `python.md`.
- Cada página dice solo lo que hace su pieza.
- Las convenciones que deben cumplir conjuntamente varias piezas de un sistema se documentan en `transversal.md`. Las páginas correspondientes enlazan las secciones transversales que les aplican.
- Cada página identifica las plantillas de `plantilla/` que se derivan de sus convenciones.
- Las páginas no indican qué repositorios utilizan cada tecnología ni establecen cuándo elegir una plataforma sobre otra.

## Revisión

Una revisión evalúa cada fuente citada, cada convención propia y cada fila de «Cumplimiento», utilizando los criterios establecidos en este documento. No se limita a señalar problemas: también deja constancia de lo que se revisó y se mantiene.

El resultado se presenta en una tabla, con una fila por cada elemento evaluado:

| Elemento evaluado | Alternativa | Veredicto |
| :--- | :--- | :--- |
| Fuente y parte citada, convención propia o fila de cumplimiento, con su ubicación en la página | Lo que se consideró en su lugar, o «Ninguna» | «Se queda», «Cambia» o «Sale», con la razón y la evidencia |

### Evidencia

- **Comprobado:** se verificó mediante una herramienta o un comando reproducible. Se indica cómo repetir la comprobación.
- **Leído:** se verificó directamente en una fuente. Se indica la sección o el fragmento que lo respalda.
- **Sin confirmar:** no fue posible verificarlo. Se identifica expresamente como tal; no se presenta como un hecho.

Las herramientas que hacen cumplir las convenciones se comprueban mediante experimentos, no de memoria ni por lo que aparentan hacer según su documentación.

Ningún elemento queda fuera de la revisión sin que conste que no fue evaluado.

## Base de las convenciones

Ni el código de los proyectos, ni una página anterior, ni los ADR son fuente, ni justifican recomendar una fuente o una convención propia. El código solo sirve para identificar necesidades y casos de uso. Una página se escribe de cero desde sus fuentes.

El porqué de estos criterios está en [adr/](../adr/README.md), con el alcance y el estado de cada decisión.
