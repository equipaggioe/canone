# ADR-0189 · Lo que no es código de una app de Qt va en `src/app/assets/`

- **Estado:** Aceptada. El usuario eligió lo recomendado (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/qt.md`](../plataformas/qt.md), «Proyecto»; `scripts/verificar.py`

## Contexto

Con el árbol comprobado ([ADR-0188](0188-verificar-comprueba-el-arbol-de-qt-y-flet-y-ruff-deja-http-solo-en-api.md)),
`qt.md` no tenía lugar para lo que no es código. Consola tiene imágenes de la interfaz, un logo y
la flecha de una lista, y el kit de su cámara, un módulo de Node que la app corre desde el disco.
`flet.md` ya tiene `assets/`.

## Decisión

1. **Lo que no es código va en `src/app/assets/`**, con subcarpetas si hace falta.
2. **Las imágenes de `assets/` entran en `resources.qrc`**, como el icono y las traducciones.
3. Un archivo que otro programa lee del disco, como un módulo de Node, se queda como archivo: no
   puede leerlo desde un `.qrc`.

## Consecuencias

- `verificar.py` admite cualquier archivo bajo `src/app/assets/`.
- Una app empaquetada lleva los archivos del punto 3 aparte de los recursos compilados.

## Descartado

- **Una carpeta por tipo, como `images/` y `kits/`:** más carpetas en el árbol para lo que una sola
  resuelve.
- **Las imágenes leídas del disco, sin `resources.qrc`:** `qt.md` ya junta el icono y las
  traducciones en él.
