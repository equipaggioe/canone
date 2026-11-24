# ADR-0227 · Un objetivo más chico que 24 × 24 vale si su círculo de 24 no toca otro, y un separador puede ser más fino

- **Estado:** Aceptada. El usuario pidió el 2026-11-23, en Consola, el punto 1 al ver controles demasiado grandes para el escritorio, y el 2 al rechazar los separadores de 24 px
- **Fecha:** 2026-11-23
- **Alcance:** `transversal.md`, `qt.md` y `plantilla/qt/tests/test_accessibility.py`

## Contexto

El ADR-0217 fijó 24 × 24 en una app que solo se usa con el puntero, con la sola salvedad de un
enlace dentro de una frase, y `test_accessibility.py` medía el tamaño sin más. WCAG 2.5.8 trae
otras salvedades, y la primera es la de espaciado: un objetivo de menos de 24 × 24 cumple si un
círculo de 24 px de diámetro centrado en él no toca otro objetivo ni el círculo de otro objetivo
chico ([WCAG 2.2 §2.5.8](../fuentes/w3c/wcag22.html)).

En Consola, lo que se veía grande no venía de la regla: eran botones de 34 px, ítems de menú de
32 y campos de 28, que se bajaron a 24–28 sin salir de ella. Lo que la regla sí impedía era un
icono chico con aire alrededor, como una X o una estrella sueltas, y los separadores de 1 px
entre paneles, que Qt agarra en 5. Un separador de 24 px abre un margen de 24 entre los
paneles; se probó entre la consola y su columna derecha, y el usuario lo rechazó.

## Decisión

1. En una app que solo se usa con el puntero, un objetivo mide al menos 24 × 24, salvo un enlace
   dentro de una frase, o es más chico y un círculo de 24 px de diámetro centrado en él no toca
   otro objetivo ni el círculo de otro objetivo chico.
2. Un separador que cambia el tamaño de dos paneles puede ser más fino, si también se mueve con
   el teclado.
3. `test_accessibility.py` mide los objetivos con la ventana como está y al 200 % (`crowded`),
   y no mide el tamaño de un `QSplitterHandle`.

## Consecuencias

- Reemplaza el punto 2 del ADR-0217. El 48 × 48 táctil no cambia: la salvedad es de 2.5.8, que
  pide 24.
- El punto 1 sigue en el nivel AA de WCAG: es la excepción de la norma.
- El punto 2 queda por debajo de WCAG 2.5.8: la norma no exceptúa un separador, y el teclado no
  cuenta como alternativa para el puntero. Quien no apunta con precisión lo mueve con Tab y las
  flechas.
- Cada repositorio de Qt vuelve a copiar `test_accessibility.py`.

## Descartado

- **Separadores de 24 px con la línea en el medio:** abren un margen de 24 px entre los paneles;
  el usuario lo rechazó al verlo en Consola.
- **Bajar el mínimo a 20 × 20, el de macOS:** queda por debajo de WCAG, el estándar de la sección
  (ya descartado en el ADR-0217).
- **Una excepción solo en Consola:** obliga a bifurcar la prueba canónica, y Consola sigue a
  Canone como cualquier repositorio.
