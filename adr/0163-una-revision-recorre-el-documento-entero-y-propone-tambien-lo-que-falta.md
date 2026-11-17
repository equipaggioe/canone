# ADR-0163 · Una revisión recorre el documento entero y propone también lo que falta

- **Estado:** Aceptada. El usuario pidió aplicar la propuesta (2026-11-16)
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/README.md`](../plataformas/README.md)

## Contexto

Al pedir la revisión de una página, un asistente revisó un solo aspecto. Leído en «Revisión», sin
experimento que lo confirme como causa:

- No decía que revisar es comprobar contra todo el documento, y los criterios estaban repartidos en
  seis secciones sin una lista que recorrer.
- Los veredictos eran «Se queda», «Cambia» y «Sale»: no había lugar para lo que falta.
- Una convención nueva solo se proponía «con su efecto comprobado», y una preferencia no se
  comprueba con un experimento.

El mismo documento decía una idea en varios lugares, usaba «cómo se usa» en dos sentidos y colgaba
las fuentes de «Función de las páginas» y las convenciones propias de «Adopción de fuentes».

## Decisión

1. **Revisar una página, una sección o una fuente es comprobar que cumple el documento entero**, en
   cinco pasos: decisiones, fuentes, convenciones, lo que falta y cumplimiento. Se hacen todos
   aunque el pedido nombre un solo aspecto.
2. **Lo que falta se busca desde las decisiones que hay que resolver**, no desde lo que la fuente
   dice y la página no escribe. La tabla de resultados gana el veredicto «Entra».
3. **Lo que afirma un hecho se comprueba; una preferencia se propone como preferencia**, y la decide
   el desarrollador.
4. **Una revisión propone y no edita.**
5. **Una convención lleva su razón solo cuando se aparta de una fuente o de otra regla de Canone, o
   cuando endurece una fuente.** La razón de cualquier otra decisión va en su ADR.
6. **Los requisitos «Normativa» y «Decide algo» son uno solo**: una fuente cumple seis requisitos.
7. **De una fuente rige solo lo que la página escribe**, en lugar de «lo que la página no escribe no
   rige»: los valores predeterminados de una herramienta rigen sin estar escritos.
8. «Elección» y «Endurecimiento» entran en «Terminología», como las convenciones propias que llevan
   origen.
9. El documento se ordena en: páginas y alcance, qué entra en una página, fuentes, convenciones
   propias, redacción, orden de las secciones, cumplimiento y revisión. «Base de las convenciones»
   pasa a «Revisión».
10. **Una revisión no propone una fuente nueva para convenciones que ya están escritas**, y una
    convención que se propone en la misma revisión no cuenta para «Aporta».
11. **Lo que se propone cumple las dos condiciones igual que lo escrito.** Un defecto de
    `plantilla/`, del CI o de `verificar.py` se reporta aparte: no es una convención.
12. **Una preferencia de la fuente entre dos formas, como «prefer X to Y», es una posición y se
    adopta tal cual.** El endurecimiento queda para lo que la fuente sugiere considerar, ofrece como
    opción o condiciona a que sea posible.
13. **El enlace que prueba un hecho va en su versión fija cuando el publicador la tiene.**

Los puntos 10 a 13 salen de dos revisiones de prueba, de `qt.md` y de `android.md`, hechas por un
asistente en una sesión nueva con el pedido «revisa plataformas/<página>». La primera propuso una
fuente para tres convenciones ya escritas y mezcló defectos de la plantilla con convenciones; la
segunda encontró que cada «prefer» de una guía de estilo exigía una razón, y que
developer.android.com no tiene versiones fijas.

Reemplaza el punto 3 del [ADR-0145](0145-una-convencion-entra-por-lo-que-empeora-sin-ella.md) en «con
su efecto comprobado».

## Consecuencias

- Las páginas no se revisaron con el punto 5: las que explican una elección en la convención siguen
  así hasta su revisión.
- Los ADR anteriores nombran secciones que ya no existen, como «Función de las páginas».

## Descartado

- **Dejar la búsqueda de lo que falta fuera de la revisión:** el pedido de una revisión incluye
  proponer adiciones.
