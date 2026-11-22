# ADR-0216 · Un cliente de Qt mide su accesibilidad con una prueba canónica, y cada repositorio da su ventana

- **Estado:** Aceptada. El usuario pidió el 2026-11-21 implementarlo si la evaluación lo respaldaba
- **Fecha:** 2026-11-21
- **Alcance:** `qt.md`, `plantilla/qt/tests/` y `scripts/verificar.py`

## Contexto

«Accesibilidad» de `transversal.md` rige en todos los clientes, y nada lo medía en uno de Qt:
`plantilla/qt/` solo traía `test_theme.py`, que comprueba el estilo. Consola escribió su propia
medición, `desktop/scripts/aa.py`, al cumplir el nivel AA (su ADR-0095), y casi todo lo que hace es
de Qt y no de Consola: el contraste, el tamaño de los objetivos, el recorrido con Tab, las
animaciones sin fin, la ventana al 200 %, los anuncios. Lo propio era poco: cómo abrir la ventana
con contenido, sus bandas, qué detiene lo que se mueve y qué cambia un estado.

Lo que se recomienda:

- W3C dice que una herramienta no comprueba todo y que hace falta el juicio de una persona, y
  recomienda combinar la revisión automática con la manual
  ([Selecting Web Accessibility Evaluation Tools](https://www.w3.org/WAI/test-evaluate/tools/selecting/)).
- El equipo de accesibilidad de GOV.UK probó diez herramientas sobre una página con fallas puestas
  a propósito: entre todas se les escapó cerca del 29 %, y concluyó que rinden más junto con la
  prueba manual
  ([What we found when we tested tools on the world's least-accessible webpage](https://accessibility.blog.gov.uk/2017/02/24/what-we-found-when-we-tested-tools-on-the-worlds-least-accessible-webpage/)).
- Las plataformas ponen esas comprobaciones dentro de las pruebas: Flutter, con `meetsGuideline`
  en `flutter_test` ([Accessibility testing](https://docs.flutter.dev/ui/accessibility/accessibility-testing)),
  y Compose, con `enableAccessibilityChecks()` desde la 1.8.0
  ([Test your app's accessibility](https://developer.android.com/develop/ui/compose/accessibility/testing)).
  Qt Widgets no trae nada parecido.

Comprobado el 2026-11-21 en Consola: la prueba pasa en Windows y en Linux, y falla con cada una de
tres regresiones puestas a propósito (la estrella sin foco, la marca sin anillo de foco y el LED
pulsando con «Animaciones» apagada). Le encontró a la medición anterior dos errores que ocultaban
fallas: comparaba el foco del control con el que empezaba ya enfocado, y medía antes de que la
ventana terminara de acomodarse.

## Decisión

1. `tests/test_accessibility.py` es canónico, se copia sin editar y `verificar.py` lo compara:
   mide en la ventana principal 1.4.3, 1.4.11, 1.4.4, 2.1.1, 2.1.2, 2.2.2, 2.4.3, 2.4.7, 2.5.8
   (24 × 24) y 4.1.3, y corre en CI con las demás pruebas.
2. Cada repositorio da en `tests/conftest.py` el fixture `screen`, que cumple el protocolo `Screen`:
   la ventana abierta con el contenido que se usa, sus bandas en orden de lectura, `stop_motion` y
   `status_changes`. `plantilla/qt/tests/conftest.py` es su punto de partida.
3. Sin pantalla, en Windows la prueba apunta `QT_QPA_FONTDIR` a las fuentes del sistema: sin eso,
   Qt no encuentra otras y cada texto mide el doble de ancho.
4. Lo que una herramienta no ve se sigue comprobando a mano: lo que dice un lector de pantalla, si
   un orden tiene sentido o si un nombre dice lo que hace.

## Consecuencias

- Cada repositorio con `desktop/` copia la prueba y escribe su `screen`: hasta entonces,
  `verificar.py` falla, y sin el fixture, la prueba no corre.
- Una ventana nueva o una parte nueva quedan medidas sin escribir nada; un cambio de estado nuevo
  se agrega a `status_changes`.
- La prueba abre la ventana una vez por cada comprobación: en Consola, unos 15 s más en CI.
- Compose, Flutter, Flet y la web no tienen todavía su equivalente
  ([pendientes/medicion-de-accesibilidad.md](../pendientes/medicion-de-accesibilidad.md)).

## Descartado

- **Que cada repositorio escriba su medición:** repite en cada uno lo mismo, y una copia mal escrita
  da por bueno lo que falla, como le pasó a la primera de Consola.
- **Un script que se corre a mano:** nadie lo corre antes de cada cambio; las plataformas que traen
  comprobaciones las ponen en las pruebas.
- **Una herramienta externa:** no hay una para Qt Widgets que corra en CI sin pantalla.
  Accessibility Insights for Windows y los lectores de pantalla sirven para la revisión manual, no
  para CI.
