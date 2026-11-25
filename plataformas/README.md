# Plataformas

Cada página reúne las convenciones de una tecnología o ámbito de implementación. `transversal.md` reúne las que deben cumplir conjuntamente varias piezas de un sistema, y `autenticacion.md`, las del registro, la autenticación y la sesión de una cuenta, en el servidor y en sus clientes.

Para trabajar en una pieza se leen enteras su página y las que nombra «Se lee con» en [Páginas](#páginas), y de [stack.md](../stack.md), el bloque de cada una. Las demás páginas no aplican.

El resto de este documento dice cómo se escribe y cómo se revisa una página.

## Terminología

- **Ámbito:** área de implementación que agrupa convenciones aplicables a distintas tecnologías o piezas.
- **Asunto:** grupo de decisiones que se responden juntas, como el vencimiento de la sesión o los atributos de su cookie. Una sección de una página reúne uno o varios asuntos.
- **Convención:** criterio que determina cómo se construyen, organizan o integran las piezas de un sistema.
- **Convención adoptada:** convención que establece una fuente normativa, y que la página escribe con su origen.
- **Convención propia:** convención que establece Canone. No lleva origen, salvo que sea una elección o un endurecimiento.
- **Elección:** convención propia que fija una opción o un valor que una regla de una fuente permite. Lleva el origen de esa regla.
- **Endurecimiento:** convención propia que vuelve obligatorio lo que una regla de una fuente sugiere considerar, ofrece como opción o condiciona a que sea posible. Lleva el origen de esa regla. Una preferencia de la fuente entre dos formas, como «prefer X to Y», no es un endurecimiento: es una posición, y se adopta tal cual.
- **Fuente normativa:** documento externo que establece convenciones que pueden adoptarse.
- **Material de referencia:** lista de nombres o valores que utiliza una convención, como un registro, sin ser una fuente normativa.
- **Origen:** la fuente, y la sección o las secciones de ella, de la que sale una convención.
- **Parte:** una sección de una fuente, o el fragmento de una sección que trata un mismo asunto.
- **Pieza:** componente identificable de un sistema que tiene una responsabilidad y puede documentarse por separado.
- **Tecnología:** herramienta, lenguaje, framework, plataforma o sistema concreto utilizado para implementar una pieza.

## Páginas

| Página | Cubre | Se lee con |
| :--- | :--- | :--- |
| [transversal.md](transversal.md) | Lo que deben cumplir conjuntamente varias piezas | — |
| [autenticacion.md](autenticacion.md) | El registro, la autenticación y la sesión de una cuenta, en el servidor y en sus clientes | — |
| [python.md](python.md) | Lo común a todas las piezas implementadas en Python | — |
| [fastapi.md](fastapi.md) | Un servidor en FastAPI | `python.md`, `postgres.md`, `transversal.md` y `autenticacion.md` |
| [postgres.md](postgres.md) | La base de datos | — |
| [sveltekit.md](sveltekit.md) | Una superficie web con SvelteKit y UnoCSS | `transversal.md` y `autenticacion.md` |
| [flutter.md](flutter.md) | Una aplicación en Flutter | `transversal.md` y `autenticacion.md` |
| [android.md](android.md) | Una aplicación de Android con Kotlin y Jetpack Compose | `transversal.md` y `autenticacion.md` |
| [flet.md](flet.md) | Una aplicación en Flet | `python.md`, `transversal.md` y `autenticacion.md` |
| [qt.md](qt.md) | Una aplicación de escritorio con Qt Widgets y PySide6 | `python.md`, `transversal.md` y `autenticacion.md` |
| [java.md](java.md) | Una pieza en Java que solo llama el servidor, en la misma máquina | — |
| [despliegue.md](despliegue.md) | La configuración del servidor | — |

### Alcance

- Una página con página madre hereda sus convenciones. No debe repetirlas; únicamente documenta las particularidades de su ámbito. Por ejemplo, `fastapi.md`, `flet.md` y `qt.md` heredan de `python.md`.
- Cada página dice solo lo que hace su pieza, salvo `autenticacion.md`, que reúne todo el registro, la autenticación y la sesión de una cuenta, también lo que hace una sola pieza.
- Las convenciones que deben cumplir conjuntamente varias piezas de un sistema se documentan en `transversal.md`, salvo las de la cuenta, que van en `autenticacion.md`: `transversal.md` no trata el registro, la autenticación ni la sesión. Una sección de esas dos páginas que no obliga a todas las piezas dice a cuáles.
- Una sección de la página de una pieza que cumple una sección de `transversal.md` o de `autenticacion.md` la enlaza en un párrafo `Contrato:`, antes de sus convenciones y después del párrafo `Estándar:`, si lo lleva.
- Lo que se instala en la máquina va en `despliegue.md`, también la unidad que corre una pieza. La página de la pieza escribe lo que está en su carpeta del repositorio.
- Cada página identifica las plantillas de `plantilla/` que se derivan de sus convenciones.
- Las páginas no fijan qué se usa en cada plataforma ni en qué versión: eso está en [stack.md](../stack.md), y cada página escribe cómo se usa.
- Las páginas no indican qué repositorios utilizan cada tecnología ni establecen cuándo elegir una plataforma sobre otra.
- Una página escribe cómo se construye, se firma y se publica en cada plataforma como si el producto tuviera las cuentas y los certificados que esa plataforma pide. En qué plataformas construye y publica un producto lo elige cada repositorio ([transversal.md](transversal.md#distribución)).

### En desarrollo

Una página que empieza con la nota «En desarrollo; no se implementa» no se aplica a ningún repositorio mientras la nota esté: no seguirla no es una desviación, y `verificar.py` no exige nada de ella. Dentro de Canone se revisa y se desarrolla como cualquier otra parte.

## Qué entra en una página

Una página escribe decisiones, no cómo funciona su tecnología. Se escribe desde las decisiones que la tecnología obliga a tomar, y escribe cada convención que rige, adoptada o propia.

Una convención entra solo si cumple las dos condiciones:

1. **Hay elección:** existe otra forma que también funciona. Lo que tiene una sola forma correcta, como el orden en que una API exige sus llamadas, es conocimiento de la tecnología y no se escribe: quien escribe el código ya lo sabe.
2. **Se puede nombrar qué empeora sin ella**, aunque todavía no haya pasado, en el producto tal como es y no en una escala que no tiene ([principios.md](../principios.md#poder-nombrar-el-síntoma)):
   - **Eficacia:** el programa falla, da un resultado incorrecto sin que nadie lo note, queda expuesto a un ataque o pierde datos.
   - **Eficiencia:** el programa usa más tiempo, memoria o red de lo necesario.
   - **Uso:** la interfaz se ve o se comporta distinto según la parte del producto, o deja a un usuario sin poder usarlo.
   - **Estructura:** dos piezas no se entienden, un repositorio no se lee como los demás, una decisión se vuelve a tomar en cada repositorio, o un cambio o una actualización cuesta más de lo necesario.

Una preferencia cumple la segunda condición por la estructura: sin la convención, cada sesión o cada repositorio elegiría distinto. En una regla de estilo se pregunta qué empeora si no hubiera regla, no si otro valor sería peor.

Lo que tiene una sola forma correcta se escribe solo si ya se hizo mal y está comprobado ([Evidencia](#evidencia)). Va como convención propia.

No justifica una convención que una fuente la establezca, que una herramienta pueda comprobarla ni que complete una lista.

### Qué no se escribe

No se escribe lo que no cumple las dos condiciones, ni lo siguiente:

- **Lo que hace cumplir una herramienta:** si una herramienta de «Cumplimiento» hace cumplir entera una parte de una fuente, la página no escribe sus convenciones. Escribe una sola convención que nombra esa parte, con su origen, y dice qué reglas de esa parte no sigue, con su razón. La herramienta va en «Cumplimiento». Lo que la herramienta no cubre se escribe convención por convención.
- **Lo dirigido a otro actor:** no se escriben las obligaciones dirigidas a quienes desarrollan una herramienta que el producto utiliza, como coturn, Uvicorn o un navegador, ni las dirigidas a la otra parte de un protocolo, como el servicio de push de Web Push. Sí se escriben las opciones que la herramienta deja a quien la configura, como los destinos a los que coturn niega relevar.
- **Lo de una función que no se ofrece:** no se escribe. Agregarla obliga a volver a la fuente.
- **Lo de un asunto que sigue a otra fuente:** no se escribe con el origen de esta. Si la fuente de ese asunto no lo resuelve, se escribe como convención propia.
- **Lo repetido:** lo que dicen varias partes de la fuente de un asunto se escribe una sola vez, con todas esas partes.
- **Lo que no se sigue:** no se escribe, salvo en la convención que nombra una parte que hace cumplir una herramienta: ahí se dice qué reglas no se siguen y por qué. Si la página hace otra cosa, escribe lo que hace como convención propia.

### Una convención, una sección

- Cada convención se escribe en una sola sección, de cualquier página.
- Dos convenciones no deben regular lo mismo.

## Fuentes

Una fuente se usa como guía, para que un asunto siga un mismo enfoque: por eso se prefieren pocas fuentes que cubran muchos asuntos. No se busca una fuente para cada convención, ni se recorren las fuentes disponibles para incorporar lo que digan. Una convención no necesita una fuente que la justifique: el origen registra de dónde salió, para ver su coherencia con las demás.

Una fuente se adopta para un asunto porque sus convenciones se acomodan a lo que el producto necesita, no para cubrir decisiones sueltas. Cada decisión se resuelve con una convención de la fuente de su asunto o, si esa fuente no la resuelve o el asunto no tiene fuente, con una convención propia.

### Requisitos

Una fuente debe cumplir los seis requisitos siguientes:

1. **Normativa:** toma posición en uno de los puntos que deben resolverse para la tecnología o ámbito, donde hay más de una forma que funciona: establece cuál se usa y cuál no. Cada convención que se toma de ella debe poder expresarse como «se usa X» o «no se hace Y». No es fuente un documento que explica cómo funciona una tecnología, sea un manual, una visión general, un tutorial o una referencia de API, aunque sea oficial y diga «se debe». De un documento que mezcla las dos cosas cuentan solo las posiciones.
2. **Autoridad:** procede de quien define la tecnología o de un organismo que publica criterios para que otros los adopten: un estándar, una especificación, una guía de estilo oficial, OWASP o NIST. No cuentan los tutoriales, ejemplos de código, proyectos de muestra, blogs, cursos, foros, prácticas de la comunidad ni la popularidad.
3. **De la versión en uso:** corresponde a la versión de la tecnología utilizada. La copia conservada en `fuentes/` fija el texto del que salen las convenciones adoptadas.
4. **Independiente:** las convenciones adoptadas no dependen de la infraestructura de quien publica la fuente.
5. **Cubre:** resuelve la mayoría de las decisiones de los asuntos que regula, considerando conjuntamente todas las páginas, para que esos asuntos sigan su enfoque. En esos asuntos, lo no cubierto debe quedar en minoría. Lo que se contradice o se dirige a otro actor no cuenta como cubierto.
6. **Aporta:** es el origen de al menos tres convenciones, contando todas las páginas. Cuentan también las elecciones y los endurecimientos que la tienen como origen. No cuenta lo que se dirige a otro actor, ni una convención que se propone en la misma revisión.

Para «Cubre» y «Aporta», los documentos de una misma documentación, la que publica quien define una tecnología para una de sus versiones, cuentan juntos: una guía partida en páginas es una sola guía. Cada documento sigue siendo una fuente aparte.

Un documento que no cumple «Cubre» o «Aporta» no es fuente, y lo que se aproveche de él se escribe como convención propia.

### Elección entre fuentes

Entre las fuentes que cumplen los seis requisitos y se acomodan a un asunto, se elige la que se acomoda a más asuntos, contando todas las páginas, siempre que resuelva la mayoría de las decisiones de ese asunto. Para contar, los documentos de un mismo publicador que no se contradicen valen como uno, aunque cada uno sigue siendo una fuente aparte. Si aun así empatan, se elige la de mayor prioridad en la tabla y, a igual prioridad, la que resuelve más decisiones del asunto. El asunto sigue solo a la fuente elegida: las demás no se citan en él, aunque digan lo mismo.

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

### Adopción

Adoptar una fuente es seguir su enfoque en un asunto. La página escribe, cada una con su origen, solo las posiciones de la fuente que cumplen las dos condiciones de [Qué entra en una página](#qué-entra-en-una-página). El resto de la fuente no se escribe, y no hay que justificar por qué. De una fuente rige solo lo que la página escribe.

### Origen

- Una convención adoptada termina con su origen: un enlace a la copia de su fuente en `fuentes/`, con el nombre de la fuente y la sección de la que sale. La sección se nombra por su número, si la fuente las numera, o por su título en cursiva. Por ejemplo: `([RFC 6749 §4.1.3](../fuentes/rfc/rfc6749.txt))` o `([PEP 8, *Imports*](../fuentes/python/pep-0008.rst))`.
- Una convención tiene como origen una sola fuente, y puede nombrar varias de sus secciones.
- Una convención con origen solo dice lo que su origen establece, con su razón cuando la lleva, o la opción que elige o la forma que endurece. Un valor o un comportamiento que la fuente no fija va en otra convención, propia y sin origen.
- Una sección con convenciones adoptadas empieza por un párrafo `Estándar:` o `Estándares:` que nombra, con su enlace, los documentos que son su origen. Es informativo: no adopta nada por sí mismo, y no nombra secciones ni lleva «salvo».

### Verificación

- `scripts/verificar.py --canone` comprueba en CI que:
  - Cada enlace a `fuentes/` apunte a un archivo que existe.
  - Cada sección que nombra un origen exista en su archivo.
  - Cada archivo de `fuentes/` sea el origen de alguna convención, salvo una lista de la que un programa de Canone toma valores.
  - El párrafo `Estándar:` de una sección nombre los mismos documentos que son origen de sus convenciones, y nada más que esos documentos.
  - Cada convención tome su origen de un solo documento de `fuentes/`.

## Convenciones propias

Una convención propia se establece en tres casos:

1. **Elección:** se selecciona una opción o un valor que la fuente permite, como un plazo menor que su máximo. Se escribe solo la opción elegida.
2. **Excepción:** se hace algo distinto de lo que establece una fuente, o se endurece lo que establece. Se escribe lo que se hace; un endurecimiento se escribe solo en su forma endurecida.
3. **Decisión no cubierta:** la fuente de su asunto no resuelve esa decisión, o el asunto no tiene fuente.

Además:

- Los valores predeterminados de una herramienta que ninguna fuente exige rigen mientras la página no establezca otra cosa. Cambiarlos constituye una convención propia, salvo que la fuente de su asunto exija el cambio.
- Un valor predeterminado que exige la fuente de su asunto es una convención adoptada, y se escribe.
- Una convención propia que se apoya en un hecho que no es evidente, como el comportamiento de un navegador, enlaza el documento que lo prueba, en su versión fija cuando el publicador la tiene. Si es una elección, no lleva enlace. El enlace no adopta el resto del documento, y ese documento no se copia en `fuentes/`. La convención no menciona otros documentos, ni siquiera para contradecirlos. Incluye únicamente la convención, cuando corresponda su razón, y ese enlace.
- Una convención que utiliza material de referencia indica de dónde lo obtiene. Enlaza su copia en `fuentes/` si un programa de Canone toma valores de él, y su URL pública si no.

## Redacción

- Cada convención expresa qué se utiliza y cómo queda. No describe procedimientos ni explica cómo hacerlo.
- Las convenciones de una misma página no deben contradecirse. Si una convención modifica el alcance de otra, debe indicar expresamente qué casos quedan fuera.
- Una convención incluye una razón breve únicamente cuando se aparta de una fuente o de otra regla de Canone, o cuando endurece una fuente. La razón de cualquier otra decisión va en su ADR.
- No se añaden comentarios, explicaciones ni ejemplos que no sean necesarios para entender o aplicar la convención.
- En cada sección van primero las convenciones propias, y después las adoptadas. De las propias, primero las que no llevan origen, y después las elecciones y los endurecimientos. Una estructura va después de esas convenciones, y la línea `Plantilla:` cierra la sección.

### Estructuras y distribución

- Las estructuras, como el árbol de directorios, se muestran completas. La estructura completa es la convención que debe seguirse.
- Después de una estructura solo se especifica dónde colocar los elementos que podrían ubicarse en más de un archivo.
- No se repite información que ya queda determinada por el nombre de un archivo u otra sección.

Estos mismos criterios de redacción se aplican a los comentarios incluidos en `plantilla/`.

## Orden de las secciones

Las secciones de una página siguen este orden. Se incluyen únicamente los bloques que correspondan a la tecnología o ámbito documentado.

1. **Proyecto:** la sección `Proyecto`, con el sistema de construcción, las dependencias, la estructura de directorios y las plantillas.
2. **Código:** formato, análisis estático, tipado, organización de paquetes y convenciones de nombres.
3. **Arquitectura:** organización interna de la aplicación y uso de las estructuras o mecanismos propios de la tecnología.
4. **Temas:** convenciones agrupadas por tema, con los temas en orden alfabético.
5. **Pruebas:** la sección `Pruebas`, con herramientas, organización y convenciones de pruebas.
6. **Entrega:** construcción, ejecución y preparación para el despliegue.
7. **Cumplimiento:** herramientas que verifican o imponen las convenciones documentadas.

### Criterios de orden

- En **Código** y **Arquitectura**, las secciones se ordenan según sus dependencias: primero se describe lo necesario para comprender las secciones posteriores.
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
- Si romper una convención ya hace fallar un paso de CI, como el build o `svelte-check`, ese paso es su herramienta: no se agrega un chequeo aparte.

## Revisión

Revisar una página, una sección o una fuente es comprobar que cumple este documento entero, y proponer lo que cambia, lo que sale y lo que falta. Se hacen los cinco pasos, aunque el pedido nombre un solo aspecto. Una revisión propone y no edita: los cambios se hacen cuando el desarrollador los aprueba.

1. **Decisiones:** qué decisiones tiene que resolver lo revisado, según las dos condiciones de [Qué entra en una página](#qué-entra-en-una-página).
2. **Fuentes:** cada fuente, contra [Requisitos](#requisitos) y [Elección entre fuentes](#elección-entre-fuentes). No se propone una fuente nueva para convenciones que ya están escritas, salvo una que, por [Elección entre fuentes](#elección-entre-fuentes), le gana a la que hoy sigue su asunto.
3. **Convenciones:** cada convención, contra las dos condiciones, [Qué no se escribe](#qué-no-se-escribe), «Una convención, una sección» y [Redacción](#redacción). Una convención adoptada se compara con su origen.
4. **Lo que falta:** para cada decisión del paso 1 que no tiene convención se propone una, de la fuente de su asunto o propia. Lo que se propone cumple las dos condiciones igual que lo escrito. Lo que la página no escribe de una fuente no se evalúa: no escribir es lo normal.
5. **Cumplimiento:** cada fila, contra sus [Criterios](#criterios).

Una revisión llega a la página que se escribiría de cero con los criterios de este documento: la página revisada no es punto de partida ni argumento. Ni el código de los proyectos, ni una página anterior, ni los ADR son fuente, ni justifican recomendar una fuente o una convención propia. El código solo sirve para identificar necesidades y casos de uso.

Lo que está mal se corrige en su causa: se rediseña la convención o la sección de la que sale, aunque eso cambie o saque otras partes de la página, y no se le agrega una excepción ni se retoca la redacción para que siga. Si la causa es un criterio de este documento, la revisión propone cambiar el criterio.

En una fuente o una convención que se propone, lo que afirma un hecho se comprueba; sin la comprobación, queda como candidata sin confirmar. Una preferencia se propone como preferencia, y la decide el desarrollador.

Un defecto de `plantilla/`, del CI o de `verificar.py` que aparece al revisar se reporta aparte, después de la tabla: no es una convención.

El resultado se presenta en una tabla, con una fila por cada elemento evaluado, también los que se mantienen. Los elementos seguidos que se quedan pueden ir juntos en una fila:

| Elemento evaluado | Alternativa | Veredicto |
| :--- | :--- | :--- |
| Fuente, convención o fila de cumplimiento, con su ubicación en la página, o decisión sin convención | Lo que se consideró en su lugar, o «Ninguna» | «Se queda», «Cambia», «Sale» o «Entra», con la razón y la evidencia |

Ningún elemento queda fuera de la revisión sin que conste que no fue evaluado.

### Evidencia

- **Comprobado:** se verificó mediante una herramienta o un comando reproducible. Si se comprobó en la revisión, se indica cómo repetir la comprobación; si ya estaba comprobado, dónde consta: la prueba de CI o el ADR.
- **Leído:** se verificó directamente en una fuente. Se indica la sección o el fragmento que lo respalda.
- **Sin confirmar:** no fue posible verificarlo. Se identifica expresamente como tal; no se presenta como un hecho.

Un «Se queda» de una convención propia nombra lo que empeora sin ella, según la segunda condición de [Qué entra en una página](#qué-entra-en-una-página), y uno de una convención adoptada lleva «Leído» con su origen. Lo que la convención afirma como hecho lleva además su evidencia.

Las herramientas que hacen cumplir las convenciones se comprueban mediante experimentos, no de memoria ni por lo que aparentan hacer según su documentación.

Antes de comprobar algo, se busca si ya está comprobado en las pruebas de CI de Canone o en un ADR. Si lo está, se usa su resultado, con sus versiones, y no se repite, salvo que haya cambiado una versión de la que depende. La decisión del ADR no es argumento: solo cuenta el resultado.

### Revisión de stack.md

[stack.md](../stack.md) se revisa con los cinco pasos, y todo lo demás de [Revisión](#revisión) rige igual:

1. **Decisiones:** qué tiene que declarar o instalar cada pieza, según las páginas y los manifiestos y programas de `plantilla/`.
2. **Versiones**, en lugar de las fuentes: cada versión contra el registro de su publicador o los paquetes de Debian 13, según «Versiones» de `stack.md`, con la fecha de la consulta. La que fija otra tecnología, contra esa tecnología. Una versión que se propone se resuelve antes junto con las demás de su pieza.
3. **Contenido:** cada regla como una convención. Cada fila, contra «Qué entra» de `stack.md`, su nota, su enlace de «Para», y si la pieza la necesita o hay una opción mejor.
4. **Lo que falta y lo que sobra:** lo que una página pide o `plantilla/` declara y no tiene fila, y la fila que ninguna pieza usa.
5. **Cumplimiento:** cada fila, con un experimento por cada paquete, acción o contenedor que abarca. Se nombra también cada fila del stack que ninguna herramienta comprueba.

Cada versión se compara además entre `stack.md`, `scripts/verificar.py`, `plantilla/`, los workflows de Canone, las páginas y `fuentes/`.
