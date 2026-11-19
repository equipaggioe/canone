# ADR-0195 · Un widget de Qt que flota sobre otros se ubica sin layout, con el tamaño de su `sizeHint()`

- **Estado:** Aceptada. El usuario pidió aplicar la recomendación si era la más conveniente para
  cualquier app de Qt y coherente con Canone (2026-11-19)
- **Fecha:** 2026-11-19
- **Alcance:** [`plataformas/qt.md`](../plataformas/qt.md), «Layouts»

## Contexto

`qt.md` pide que los widgets se ubiquen con layouts, con el contrato de accesibilidad de
`transversal.md`: un widget ubicado a mano con un tamaño fijo no crece con el texto. Consola tiene
tres widgets que flotan sobre otros del mismo padre: la búsqueda que aparece sobre el log de la
consola, la lista que se despliega bajo el buscador de acciones y los bordes con los que se
redimensiona una ventana sin marco. Los tres van con `setGeometry()`.

Comprobado con PySide6 6.12.0, sin pantalla: un `QStackedLayout` en modo `StackAll` sí superpone
dos widgets, pero el de arriba ocupa toda el área y recibe los clics que iban al de abajo. Si se le
pone `WA_TransparentForMouseEvents`, tampoco sus hijos los reciben, y la búsqueda deja de poder
usarse con el mouse.

La búsqueda de la consola tenía un alto fijo de 28 px, y no crecía con la letra.

## Decisión

1. **Un widget que flota encima de otros se ubica con `setGeometry()`, sin layout, y su tamaño sale
   de su `sizeHint()`**, acotado por el lugar que hay.

## Consecuencias

- Una barra superpuesta, una lista desplegada o un borde de redimensionar no obligan a un layout
  que no los puede ubicar.
- El tamaño del que flota sigue a su contenido, como el de un widget en un layout: crece con el
  texto.

## Descartado

- **Superponer con un `QStackedLayout` en modo `StackAll`:** el widget de arriba le quita los clics
  al de abajo.
- **Ubicarlo a mano con un tamaño fijo:** recorta el texto cuando crece.
- **Extender a los menús la regla de `open()`:** la nota de Qt que pide `open()` en lugar de
  `exec()` está en `QDialog::exec()`, y la documentación de `QMenu::exec()` lo da como su uso común
  ([Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/widgets/qmenu.cpp)).
  Un `QMenu` no es un diálogo, y la regla de «Diálogos» ya no lo alcanza.
