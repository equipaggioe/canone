# ADR-0229 · Un separador se agarra en una franja de 24 px puesta encima de su línea

- **Estado:** Aceptada. El usuario la pidió el 2026-11-23, en Consola, en lugar de exceptuar los separadores. Los puntos 2 y 4 los reemplaza el [ADR-0230](0230-un-separador-se-agarra-en-5-px.md)
- **Fecha:** 2026-11-23
- **Alcance:** `transversal.md`, `qt.md` y `plantilla/qt/tests/test_accessibility.py`

## Contexto

El ADR-0227 dejó que un separador fuera más fino que 24 × 24 si se movía con el teclado, por
debajo de WCAG 2.5.8. Venía de dos salidas que no servían: un separador de 1 px, que Qt agarra en
5, no mide lo que pide la norma, y uno de 24 px con la línea en el medio abre un margen de 24
entre los paneles, que el usuario rechazó.

El problema era que la misma pieza, el `QSplitterHandle`, dibujaba la línea y recibía el
arrastre. Un handle siempre ocupa su ancho en el layout: no puede medir 24 px sin apartar 24 px
los paneles.

## Decisión

1. El handle de un `QSplitter` es una línea de 1 px que dibuja y no recibe el puntero ni el
   foco.
2. Lo que se agarra es otro widget, una franja transparente de 24 px puesta encima de la línea,
   que recibe el arrastre, Tab y las flechas, y solo dibuja el foco.
3. Lo que queda debajo de la franja le deja ese lugar: una barra de desplazamiento no va bajo
   ella.
4. No hay excepción para los separadores, y `test_accessibility.py` vuelve a medirlos.

## Consecuencias

- Reemplaza el punto 2 del ADR-0227, y su punto 3 en lo que no medía de un `QSplitterHandle`.
- Vuelve al nivel AA de WCAG sin excepciones propias.
- La franja tapa 12 px de cada panel: un clic ahí arrastra. Por eso lo de abajo le deja el lugar
  libre, y donde no hace falta, como en la cabecera de una sección, se pierde ese borde.

## Descartado

- **Exceptuar los separadores (ADR-0227, punto 2):** queda por debajo de WCAG, y el teclado no
  cuenta como alternativa para el puntero.
- **Un handle de 24 px:** aparta los paneles 24 px.
