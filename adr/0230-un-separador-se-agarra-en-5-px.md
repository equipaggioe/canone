# ADR-0230 · Un separador se agarra en 5 px

- **Estado:** Aceptada. El usuario la pidió el 2026-11-23, en Consola, si no aparecía una fuente mejor
- **Fecha:** 2026-11-23
- **Alcance:** `transversal.md`, `qt.md` y `plantilla/qt/tests/test_accessibility.py`

## Contexto

El ADR-0229 agarraba un separador en una franja de 24 px, lo que pide WCAG 2.5.8 a todo objetivo.
El usuario lo rechazó: ninguna app de escritorio agarra un separador así. Se buscó una fuente
que fijara cuánto mide lo que se agarra de un separador en el escritorio, y no hay ninguna
normativa:

- W3C pide 24 × 24 a todo puntero, también al ratón, y no nombra separadores ni asas de arrastre
  ([Understanding 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)).
- VS Code agarra un separador en 4 px, y en 20 en iOS; el usuario lo sube hasta 20 con
  `workbench.sash.size`, que describe: «súbelo si te cuesta cambiar el tamaño de las vistas con
  el ratón» ([`sash.contribution.ts`](https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/sash/browser/sash.contribution.ts)).
- Apple dibuja el separador fino de 1 pt y lo agarra un poco más ancho que la línea
  ([Split views](https://developer.apple.com/design/human-interface-guidelines/split-views) y
  [`splitView(_:effectiveRect:forDrawnRect:ofDividerAt:)`](https://developer.apple.com/documentation/appkit/nssplitviewdelegate/splitview(_:effectiverect:fordrawnrect:ofdividerat:))).
- Qt agarra en 5 px un handle de 1 px, y GTK daba 5 px a `handle-size`, según un informe de 2014
  ([GNOME bug 735009](https://bugzilla.gnome.org/show_bug.cgi?id=735009)).

Lo común es una zona de 4 a 7 px.

## Decisión

1. La franja de un separador mide al menos 5 px a lo ancho de su línea.
2. `test_accessibility.py` pide `GRIP`, 5 px, a lo que lleva el cursor de un separador, y 24 a lo
   demás.

## Consecuencias

- Reemplaza los puntos 2 y 4 del ADR-0229: la franja sigue encima de la línea, pero mide 5 px.
- Los separadores quedan por debajo de WCAG 2.5.8. Quien no apunta con precisión los mueve con
  Tab y las flechas.
- Lo que queda debajo de la franja le deja libre la mitad de sus píxeles.

## Descartado

- **24 px siempre (ADR-0229):** ninguna app de escritorio lo hace, y el usuario lo rechazó.
- **4 px, como VS Code:** 5 es lo que Qt ya agarra en un handle de 1 px y lo que daba GTK.
- **La excepción «Equivalente», con otro control de 24 px que cambie el ancho:** un control que
  nadie usaría, solo para cumplir.
- **Una opción que agrande la franja a 24 px, como `workbench.sash.size` de VS Code:** ninguna
  app de Canone tiene hoy un usuario que la necesite, y el usuario la rechazó.
