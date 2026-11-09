# ADR-0129 · La página escribe cada convención que rige, y la adoptada lleva su origen

- **Estado:** Aceptada, salvo el punto 9, que es propuesta
- **Fecha:** 2026-11-09
- **Alcance:** `plataformas/`, `fuentes/README.md`, `principios.md` y `scripts/verificar.py`

## Contexto

Citar una fuente adoptaba sus convenciones sin escribirlas. Lo que regía no estaba escrito en
ninguna parte: había que buscarlo en 125 fuentes y filtrar a mano lo que se dejaba sin efecto, lo
que regía en otra sección y lo dirigido a otro actor. Contadas las fuentes, ni siquiera se sabía
cuántas convenciones de NIST SP 800-63B-4 se adoptaban: el techo era de 251.

## Decisión

1. La página escribe cada convención que rige. Lo que no escribe no rige.
2. Una convención adoptada termina con su origen: un enlace a la copia de su fuente en `fuentes/`,
   con el nombre de la fuente y su sección, por número o por título en cursiva. Una convención que
   sale de varias fuentes lleva todos sus orígenes. Una convención propia no lleva origen.
3. Sale el párrafo `Estándar:`, y con él la cita entera, por partes o por entradas, la columna
   «Cita» de `fuentes/README.md`, «salvo» y «rige en otra sección».
4. No se escribe:
   - lo que una herramienta de «Cumplimiento» hace cumplir entero: la página escribe una sola
     convención que nombra esa parte de la fuente, con su origen;
   - lo dirigido a otro actor;
   - lo de una función que no se ofrece: una línea dice que no se ofrece;
   - lo repetido: se escribe una vez, con todos sus orígenes;
   - lo que no se sigue. Si la página hace otra cosa, escribe lo que hace como convención propia,
     sin «Contradice X», y con su razón solo si no es evidente.
5. Sale el requisito «Acotada»: ya no hace falta leer la fuente para escribir código.
6. Quedan «Cubre» y «Aporta», como criterio para que un documento sea fuente: resuelve la mayoría
   de los asuntos que regula, para que sigan su enfoque, y es el origen de al menos tres
   convenciones.
7. Una o dos convenciones de un documento se escriben como propias. Enlazan el documento, en su
   versión fija y sin copia en `fuentes/`, solo si se apoyan en un hecho que no es evidente, como
   el comportamiento de un navegador. Una elección no lleva enlace.
8. `verificar.py --canone` comprueba que cada enlace a `fuentes/` apunte a un archivo que existe,
   que la sección que nombra un origen exista en su archivo, y que cada archivo de `fuentes/` sea
   el origen de alguna convención, salvo una lista de la que un programa toma valores.
9. *(propuesta)* Una sección que todavía tiene un párrafo `Estándar:` adopta lo que cita hasta que
   se reescriba, y al escribir su código se lee la fuente, como decía «Leer las fuentes».

Reemplaza el punto 7 del ADR-0018; el punto 2 y el 9 del ADR-0030; el punto 6 del ADR-0056; el
punto 4 del ADR-0063; los puntos 1, 3, 4, 5, 7 y 8 del ADR-0108; el punto 1 del ADR-0109; el punto
2 del ADR-0115, en que lo que escribe la página es propia; el punto 1 del ADR-0120, y los ADR-0117
y ADR-0121.

## Consecuencias

- Lo que rige se lee en la página, y cada convención adoptada se puede comprobar contra su origen.
- Una paráfrasis puede equivocarse: el origen con su sección permite revisarla.
- Cada cambio de versión de una fuente se pasa a mano a las convenciones que la tienen como origen.
- Hay que reescribir todas las páginas. Se empieza por una página nueva de autenticación, que junta
  NIST, OAuth, la sesión, las contraseñas y las passkeys del servidor, hoy repartidas entre
  `fastapi.md` y `transversal.md`. Las demás fuentes se quedan en la página que las cita.
- Una revisión comprueba también lo que la página no escribe: tiene que caer en un caso del
  punto 4. Ahí se encuentra una convención olvidada.

## Descartado

- **Separar las secciones por fuente:** un mismo tema quedaría repartido entre varias, y una
  convención que dicen dos fuentes no tendría sección propia.
- **Copiar en `fuentes/` todo documento del que sale una convención:** para una o dos convenciones
  cuesta la descarga y su mantenimiento, y no aporta un enfoque.
- **Seguir con el párrafo `Estándar:` además del origen de cada convención:** repetiría lo que ya
  dicen los orígenes.
