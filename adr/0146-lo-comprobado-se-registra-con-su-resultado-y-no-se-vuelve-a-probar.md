# ADR-0146 · Lo comprobado se registra con su resultado y sus versiones, y no se vuelve a probar

- **Estado:** Aceptada
- **Fecha:** 2026-11-14
- **Alcance:** [`documentacion.md`](../documentacion.md), el formato de un ADR, en todos los
  repositorios; [`plataformas/README.md`](../plataformas/README.md), «Evidencia»

## Contexto

Las comprobaciones que sostienen una decisión quedaban en el chat donde se hicieron. Un chat nuevo
no las ve y las repite, también las que piden un VPS o un repositorio en GitHub. De los ADR de
Canone, 33 mencionan una comprobación, pero cuentan lo que se vio, sin el resultado preciso ni las
versiones.

## Decisión

1. **El «Contexto» de un ADR dice qué se comprobó, con su resultado y las versiones de las que
   depende.** No dice cómo se hizo la prueba.
2. **Antes de comprobar algo, se busca si ya está comprobado** en las pruebas de CI de Canone o en
   un ADR. Si lo está, se cita y no se repite, salvo que haya cambiado una versión de la que depende.

## Consecuencias

- Una comprobación vale mientras no cambien sus versiones. Al subir una versión, se sabe qué hay que
  volver a comprobar.
- A un ADR anterior se le puede agregar lo que comprobó y no registró: completar su «Contexto» no
  cambia su decisión.

## Descartado

- **Registrar cómo repetir cada prueba:** no sirve para las que piden un VPS o un repositorio, y lo
  que se necesita para no repetirla es el resultado.
