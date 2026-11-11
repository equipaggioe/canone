# Plataformas

Cada página reúne las convenciones de una tecnología o ámbito de implementación. `transversal.md` reúne las que deben cumplir conjuntamente varias piezas de un sistema, y `autenticacion.md`, las del registro, la autenticación y la sesión de una cuenta, en el servidor y en sus clientes.

Para trabajar en una pieza se consulta su página, su página madre si la tiene y las secciones de `transversal.md` y `autenticacion.md` que esas páginas enlazan. Las demás páginas no aplican.

## Terminología

- **Ámbito:** área de implementación que agrupa convenciones aplicables a distintas tecnologías o piezas.
- **Asunto:** grupo de decisiones que se responden juntas, como el vencimiento de la sesión o los atributos de su cookie. Una sección de una página reúne uno o varios asuntos.
- **Convención:** criterio que determina cómo se construyen, organizan o integran las piezas de un sistema.
- **Convención adoptada:** convención establecida por una fuente normativa externa, que la página escribe con su origen.
- **Convención propia:** convención establecida directamente por Canone porque la fuente de su asunto no resuelve esa decisión o el asunto no tiene fuente, o porque es necesario elegir o modificar lo que establece la fuente.
- **Fuente normativa:** documento externo que establece convenciones que pueden adoptarse.
- **Material de referencia:** lista de nombres o valores que utiliza una convención, como un registro, sin ser una fuente normativa.
- **Origen:** la fuente, y la sección o las secciones de ella, de la que sale una convención adoptada.
- **Parte:** una sección de una fuente, o el fragmento de una sección que trata un mismo asunto.
- **Pieza:** componente identificable de un sistema que tiene una responsabilidad y puede documentarse por separado.
- **Tecnología:** herramienta, lenguaje, framework, plataforma o sistema concreto utilizado para implementar una pieza.

## Páginas

| Página | Cubre |
| :--- | :--- |
| [transversal.md](transversal.md) | Lo que deben cumplir conjuntamente varias piezas |
| [autenticacion.md](autenticacion.md) | El registro, la autenticación y la sesión de una cuenta, en el servidor y en sus clientes |
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

Una página es un catálogo de convenciones de una tecnología o ámbito. Cada convención está escrita en la página: la adoptada, con su origen en una fuente, y la propia, establecida directamente por Canone.

Las convenciones sirven para tres propósitos:

- **Uniformidad:** que los repositorios se organicen y se lean de la misma manera, con los mismos nombres y estructuras.
- **Decisiones comunes:** que las elecciones sobre tecnologías, bibliotecas, versiones y configuraciones se tomen una sola vez.
- **Contratos entre piezas:** que los componentes de un sistema se entiendan y cumplan las mismas condiciones, como el formato de error, la paginación o la sesión.

Una convención que no contribuye a ninguno de estos propósitos no se incluye. Su utilidad no depende de que alguna herramienta pueda hacerla cumplir.

### Selección de fuentes

La revisión empieza por identificar qué decisiones obliga a tomar la tecnología. Una fuente se adopta para un asunto porque sus convenciones se acomodan a lo que el producto necesita, no para cubrir decisiones sueltas. Cada decisión se resuelve con una convención de la fuente de su asunto o, si esa fuente no la resuelve o el asunto no tiene fuente, con una convención propia.

Una fuente debe cumplir además los siete requisitos siguientes:

1. **Normativa:** establece qué se debe, se debería o no se debe hacer. Cada convención que se toma de ella debe poder expresarse como «se usa X» o «no se hace Y». Los procedimientos, ejemplos y explicaciones no cuentan, aunque aparezcan en la documentación oficial.
2. **Decide algo:** responde a uno de los puntos que deben resolverse para la tecnología o ámbito.
3. **Autoridad:** procede de quien define la tecnología o de un organismo que publica criterios para que otros los adopten: un estándar, una especificación, una guía de estilo oficial, OWASP o NIST. No cuentan los tutoriales, ejemplos de código, proyectos de muestra, blogs, cursos, foros, prácticas de la comunidad ni la popularidad.
4. **De la versión en uso:** corresponde a la versión de la tecnología utilizada. La copia conservada en `fuentes/` fija el texto del que salen las convenciones adoptadas.
5. **Independiente:** las convenciones adoptadas no dependen de la infraestructura de quien publica la fuente.
6. **Cubre:** resuelve la mayoría de las decisiones de los asuntos que regula, considerando conjuntamente todas las páginas, para que esos asuntos sigan su enfoque. En esos asuntos, lo no cubierto debe quedar en minoría. Lo que se contradice o se dirige a otro actor no cuenta como cubierto. Si una fuente no cumple este requisito, no es fuente, y las convenciones que se aprovechen de ella se establecen como convenciones propias.
7. **Aporta:** es el origen de al menos tres convenciones, contando todas las páginas. Cuentan también las elecciones y los endurecimientos que la tienen como origen. No cuenta lo que se dirige a otro actor. Si no llega a tres, no es fuente, y sus convenciones se escriben como propias.

Entre las fuentes que cumplen los siete requisitos y se acomodan a un asunto, se elige la que se acomoda a más asuntos, contando todas las páginas, siempre que resuelva la mayoría de las decisiones de ese asunto. Para contar, los documentos de un mismo publicador que no se contradicen valen como uno, aunque cada uno sigue siendo una fuente aparte. Si aun así empatan, se elige la de mayor prioridad en la tabla y, a igual prioridad, la que resuelve más decisiones del asunto. El asunto sigue solo a la fuente elegida: las demás no se citan en él, aunque digan lo mismo.

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

Adoptar una fuente es escribir sus convenciones en la página, cada una con su origen. Se aplican como obligatorias, incluso cuando ninguna herramienta las hace cumplir. Lo que la página no escribe no rige.

#### Origen

- Una convención adoptada termina con su origen: un enlace a la copia de su fuente en `fuentes/`, con el nombre de la fuente y la sección de la que sale. La sección se nombra por su número, si la fuente las numera, o por su título en cursiva. Por ejemplo: `([RFC 6749 §4.1.3](../fuentes/rfc/rfc6749.txt))` o `([PEP 8, *Imports*](../fuentes/python/pep-0008.rst))`.
- Una convención tiene como origen una sola fuente, y puede nombrar varias de sus secciones.
- Una convención con origen solo dice lo que su origen establece, con su razón cuando la lleva, o la opción que elige o la forma que endurece. Un valor o un comportamiento que la fuente no fija va en otra convención, propia y sin origen.
- Una convención propia no lleva origen, salvo una elección o un endurecimiento, que llevan el de la regla de la que salen.
- Una sección con convenciones adoptadas empieza por un párrafo `Estándar:` o `Estándares:` que nombra, con su enlace, los documentos que son su origen. Es informativo: no adopta nada por sí mismo, y no nombra secciones ni lleva «salvo».

#### Qué no se escribe

- **Lo que hace cumplir una herramienta:** si una herramienta de «Cumplimiento» hace cumplir entera una parte de una fuente, la página no escribe sus convenciones. Escribe una sola convención que nombra esa parte, con su origen, y dice qué reglas de esa parte no sigue, con su razón. La herramienta va en «Cumplimiento». Lo que la herramienta no cubre se escribe convención por convención.
- **Lo dirigido a otro actor:** no se escriben las obligaciones dirigidas a quienes desarrollan una herramienta que el producto utiliza, como coturn, Uvicorn o un navegador, ni las dirigidas a la otra parte de un protocolo, como el servicio de push de Web Push. Sí se escriben las opciones que la herramienta deja a quien la configura, como los destinos a los que coturn niega relevar.
- **Lo de una función que no se ofrece:** no se escribe. Agregarla obliga a volver a la fuente.
- **Lo de un asunto que sigue a otra fuente:** no se escribe con el origen de esta. Si la fuente de ese asunto no lo resuelve, se escribe como convención propia.
- **Lo repetido:** lo que dicen varias partes de la fuente de un asunto se escribe una sola vez, con todas esas partes.
- **Lo que no se sigue:** no se escribe, salvo en la convención que nombra una parte que hace cumplir una herramienta: ahí se dice qué reglas no se siguen y por qué. Si la página hace otra cosa, escribe lo que hace como convención propia.

#### Una convención, una sección

- Cada convención se escribe en una sola sección, de cualquier página.
- Dos convenciones no deben regular lo mismo.

#### Convenciones propias y valores predeterminados

- Los valores predeterminados de una herramienta que ninguna fuente exige rigen mientras la página no establezca otra cosa. Cambiarlos constituye una convención propia, salvo que la fuente de su asunto exija el cambio.
- Un valor predeterminado que exige la fuente de su asunto es una convención adoptada, y se escribe.
- Una convención propia que se apoya en un hecho que no es evidente, como el comportamiento de un navegador, enlaza el documento que lo prueba, en su versión fija. Si es una elección, no lleva enlace. El enlace no adopta el resto del documento, y ese documento no se copia en `fuentes/`. La convención no menciona otros documentos, ni siquiera para contradecirlos. Incluye únicamente la convención, cuando corresponda su razón, y ese enlace.
- Una convención que utiliza material de referencia indica de dónde lo obtiene. Enlaza su copia en `fuentes/` si un programa de Canone toma valores de él, y su URL pública si no.

#### Verificación

- `scripts/verificar.py --canone` comprueba en CI que:
  - Cada enlace a `fuentes/` apunte a un archivo que existe.
  - Cada sección que nombra un origen exista en su archivo.
  - Cada archivo de `fuentes/` sea el origen de alguna convención, salvo una lista de la que un programa de Canone toma valores.
  - El párrafo `Estándar:` de una sección nombre los mismos documentos que son origen de sus convenciones, y nada más que esos documentos.
  - Cada convención tome su origen de un solo documento de `fuentes/`.

## Convenciones de la página

La página escribe cada convención que rige, adoptada o propia, salvo lo que deja fuera «Qué no se escribe».

Las convenciones propias se establecen en tres casos:

1. **Elecciones:** se selecciona una opción o un valor que la fuente permite, como un plazo menor que su máximo. Se escribe solo la opción elegida, con el origen de la regla.
2. **Excepciones:** se hace algo distinto de lo que establece una fuente, o se endurece lo que establece. Endurecer significa convertir en obligatorio lo que la fuente recomienda como preferencia, ofrece como opción o condiciona a que sea posible. Se escribe lo que se hace; un endurecimiento se escribe solo en su forma endurecida, con el origen de la regla que endurece.
3. **Decisiones no cubiertas:** se establecen convenciones sobre las decisiones que la fuente de su asunto no resuelve, o sobre asuntos sin fuente.

### Versiones

- Cada página fija en «Proyecto» las versiones de sus tecnologías. La plantilla y las fuentes dependen de la página: la plantilla no declara una versión que la página no estipule, y las fuentes se descargan de esa versión.
- La versión se fija por tecnología, no por pieza: una tecnología lleva la misma versión en todas las piezas que la usan.
- Lo que el servidor instala desde los paquetes de su sistema, como Python, PostgreSQL o Valkey, usa la versión de esos paquetes en todas las piezas, también en las que no corren en el servidor, en la máquina de desarrollo y en CI: así se desarrolla y se prueba con la misma versión que corre en producción.
- Lo demás usa la última versión estable, o la última LTS si la tecnología las publica.
- Una excepción lleva su razón en la página.

### Redacción

- Cada convención expresa qué se utiliza y cómo queda. No describe procedimientos ni explica cómo hacerlo.
- Las convenciones de una misma página no deben contradecirse. Si una convención modifica el alcance de otra, debe indicar expresamente qué casos quedan fuera.
- Una convención incluye una justificación breve únicamente cuando se aparta de una fuente o la endurece, o cuando explica una elección cuyo motivo no resulta evidente. Las preferencias triviales, como un color o el largo de línea, no llevan justificación.
- No se añaden comentarios, explicaciones ni ejemplos que no sean necesarios para entender o aplicar la convención.
- En cada sección van primero las convenciones propias, y después las adoptadas. De las propias, primero las que no llevan origen, y después las elecciones y los endurecimientos.

### Estructuras y distribución

- Las estructuras, como el árbol de directorios, se muestran completas. La estructura completa es la convención que debe seguirse.
- Después de una estructura solo se especifica dónde colocar los elementos que podrían ubicarse en más de un archivo.
- No se repite información que ya queda determinada por el nombre de un archivo u otra sección.

Estos mismos criterios de redacción se aplican a los comentarios incluidos en `plantilla/`.

## Orden de las secciones

Las secciones de una página siguen este orden. Se incluyen únicamente los bloques que correspondan a la tecnología o ámbito documentado.

1. **Proyecto:** la sección `Proyecto`, con versión, sistema de construcción, estructura de directorios y plantillas, y después las dependencias.
2. **Código:** formato, análisis estático, tipado, organización de paquetes y convenciones de nombres.
3. **Arquitectura:** organización interna de la aplicación y uso de las estructuras o mecanismos propios de la tecnología.
4. **Temas:** convenciones agrupadas por tema, con los temas en orden alfabético.
5. **Pruebas:** la sección `Pruebas`, con herramientas, organización y convenciones de pruebas.
6. **Entrega:** construcción, ejecución y preparación para el despliegue.
7. **Cumplimiento:** herramientas que verifican o imponen las convenciones documentadas.

### Criterios de orden

- En **Código** y **Arquitectura**, las secciones se ordenan según sus dependencias: primero se describe lo necesario para comprender las secciones posteriores.
- Los temas de **Temas** se presentan en orden alfabético.
- Cuando un mismo tema aparece en distintas páginas, conserva el mismo título y ubicación relativa siempre que corresponda al mismo bloque.

## Cumplimiento

Esta sección registra las herramientas que verifican o hacen cumplir las convenciones definidas en la página.

Se utiliza una tabla con estas columnas:

| Convención | Herramienta |
| :--- | :--- |
| Convención de la página que se hace cumplir | Herramienta que la verifica o impone |

### Criterios

- Cada fila debe referirse a una convención escrita en la página. La tabla no introduce convenciones nuevas.
- La herramienta debe hacer cumplir todo lo indicado en la primera columna.
- Una herramienta que imponga convenciones adicionales a las documentadas en esa fila no se incluye. No debe introducir requisitos que la página no haya establecido.

## Alcance

- Una página con página madre hereda sus convenciones. No debe repetirlas; únicamente documenta las particularidades de su ámbito. Por ejemplo, `fastapi.md`, `flet.md` y `qt.md` heredan de `python.md`.
- Cada página dice solo lo que hace su pieza.
- Las convenciones que deben cumplir conjuntamente varias piezas de un sistema se documentan en `transversal.md`, salvo las de la autenticación, que van en `autenticacion.md`. Las páginas correspondientes enlazan las secciones de esas dos páginas que les aplican.
- Cada página identifica las plantillas de `plantilla/` que se derivan de sus convenciones.
- Las páginas no indican qué repositorios utilizan cada tecnología ni establecen cuándo elegir una plataforma sobre otra.

## En desarrollo

Una página que empieza con la nota «En desarrollo; no se implementa» no se aplica a ningún repositorio mientras la nota esté: no seguirla no es una desviación, y `verificar.py` no exige nada de ella. Dentro de Canone se revisa y se desarrolla como cualquier otra parte.

## Revisión

Una revisión evalúa cada fuente, cada convención y cada fila de «Cumplimiento», utilizando los criterios establecidos en este documento. Una convención adoptada se compara con su origen. En cada fuente, lo que la página no escribe tiene que caer en un caso de «Qué no se escribe». No se limita a señalar problemas: también deja constancia de lo que se revisó y se mantiene.

El resultado se presenta en una tabla, con una fila por cada elemento evaluado:

| Elemento evaluado | Alternativa | Veredicto |
| :--- | :--- | :--- |
| Fuente, convención o fila de cumplimiento, con su ubicación en la página, o lo que la página no escribe de una fuente | Lo que se consideró en su lugar, o «Ninguna» | «Se queda», «Cambia» o «Sale», con la razón y la evidencia |

### Evidencia

- **Comprobado:** se verificó mediante una herramienta o un comando reproducible. Se indica cómo repetir la comprobación.
- **Leído:** se verificó directamente en una fuente. Se indica la sección o el fragmento que lo respalda.
- **Sin confirmar:** no fue posible verificarlo. Se identifica expresamente como tal; no se presenta como un hecho.

Las herramientas que hacen cumplir las convenciones se comprueban mediante experimentos, no de memoria ni por lo que aparentan hacer según su documentación.

Ningún elemento queda fuera de la revisión sin que conste que no fue evaluado.

## Base de las convenciones

Ni el código de los proyectos, ni una página anterior, ni los ADR son fuente, ni justifican recomendar una fuente o una convención propia. El código solo sirve para identificar necesidades y casos de uso. Una página se escribe de cero desde sus fuentes.
