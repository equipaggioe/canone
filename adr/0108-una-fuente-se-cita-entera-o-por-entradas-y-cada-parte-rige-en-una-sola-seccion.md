# ADR-0108 · Una fuente se cita entera o por entradas, y cada parte de una fuente entera rige en una sola sección

- **Estado:** Aceptada
- **Fecha:** 2026-10-30
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

El [ADR-0030](0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md)
dejaba citar una fuente entera o solo una parte que se adoptara en su mayoría. Las páginas citaban
secciones sueltas de una misma fuente: el *WebSocket Security Cheat Sheet* de OWASP se cita por
secciones en `despliegue.md`, `fastapi.md` y `transversal.md`, y ninguna dice qué pasa con las que
no cita nadie. Se podía tomar lo cómodo y callar lo que molestaba. La documentación de referencia
de una herramienta tampoco encajaba: de `systemd.exec` se citaba la sección *Sandboxing*, aunque
describe opciones y no trae un enfoque que adoptar.

## Decisión

1. Una fuente se cita entera, cuando trae un enfoque sobre un asunto, o por entradas, cuando es una
   referencia de opciones independientes, como `systemd.exec` o `sshd_config`. La columna «Cita»
   de `fuentes/README.md` dice cuál de las dos.
2. La unidad es el documento que se publica por separado, como una cheat sheet, una AIP o un PEP, y
   no el organismo que lo publica.
3. Citar adopta todas las convenciones explícitas de lo citado: la fuente entera, o cada entrada
   que se usa.
4. Una fuente entera se reparte entre las secciones de cualquier página. Cada sección nombra las
   partes que la rigen, y eso es lo que se lee al escribir su código. Una parte es un título del
   texto de la fuente, con todo lo que tiene debajo, nombrado con el que lo contiene si su nombre
   se repite, o un párrafo cuando un título regula asuntos de dos secciones.
5. Cada parte con convenciones rige en una sola sección. Una parte que no se sigue se deja sin
   efecto, con su razón, en la sección a la que pertenece.
6. Si dos fuentes chocan en un asunto, se cita solo la que mejor se adapta, o se deja sin efecto lo
   que choca en una de ellas.
7. Una fuente que se cita entera cumple un séptimo requisito, «Cubre»: responde la mayoría de lo
   que tienen que decidir los asuntos que regula, sumando lo que citan todas las páginas, y las
   reglas propias de esos asuntos quedan en minoría. Lo que se contradice o se deja sin efecto no
   cuenta como cubierto. Una fuente que no cubre no se cita, y sus convenciones se escriben como
   reglas propias.
8. Los requisitos se miden sobre la fuente y no sobre «la parte citada»: «Acotada» es que lo que
   una sección cita se puede leer entero al escribir su código, e «Independiente», que lo que se
   adopta no depende de la infraestructura de quien la publica.

Reemplaza los puntos 1, 5 y 6 del ADR-0030 y la primera frase de su punto 2, y los puntos 1 y 2 del
[ADR-0063](0063-una-fuente-cumple-siete-requisitos-y-su-texto-se-lee-al-escribir-codigo.md): los
siete requisitos son normativa, decide algo, autoridad, acotada, de la versión en uso,
independiente y cubre.

## Consecuencias

- Lo que no se sigue de una fuente citada queda escrito, con su razón, en la sección de su asunto.
- Una fuente de conocimiento general, como PEP 8, también se reparte entera, aunque «Acotada» no
  le pida leerla al escribir código.
- El requisito «Cubre» evita lo que el ADR-0030 descartaba al citar una fuente con excepciones: que
  la lista de lo dejado sin efecto sea más larga que lo adoptado.
- Las páginas citan hoy secciones sueltas sin repartir el resto. Cada una se revisa contra esta
  regla, y al revisarla se llena la columna «Cita» de sus fuentes, que hoy tienen solo las de
  `despliegue.md`.

## Descartado

- **Citar solo la parte que se adopta en su mayoría:** deja callar el resto de la fuente.
- **Citar entera también la documentación de referencia:** obligaría a repartir o dejar sin efecto
  cada opción de la herramienta, aunque nadie la use.
- **Que una parte sea solo un título sin subtítulos:** el texto de un título antes de su primer
  subtítulo no quedaba en ninguna parte, y sus convenciones no regían en ninguna sección, como el
  «should only» de *bcrypt* en el *Password Storage Cheat Sheet*.
- **Medir «Cubre» en cada sección:** una fuente que se reparte entre varias páginas no cubre sola
  ninguna de sus secciones.
