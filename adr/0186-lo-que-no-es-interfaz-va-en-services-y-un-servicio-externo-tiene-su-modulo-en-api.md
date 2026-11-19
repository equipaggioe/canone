# ADR-0186 · Lo que no es interfaz va en `services/`, y un servicio externo tiene su módulo en `api/`

- **Estado:** Aceptada. El usuario eligió lo recomendado para dónde va el código que no es de Qt y
  para el cliente de una API externa, con sus dos puntos: el campo que no se conoce y los
  reintentos (2026-11-18). Su consecuencia de que ninguna herramienta comprueba el árbol la deja
  atrás el [ADR-0188](0188-verificar-comprueba-el-arbol-de-qt-y-flet-y-ruff-deja-http-solo-en-api.md)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/qt.md`](../plataformas/qt.md), «Proyecto» y «Red»;
  [`plataformas/flet.md`](../plataformas/flet.md), «Proyecto» y «Red»;
  [`plataformas/transversal.md`](../plataformas/transversal.md), «OpenAPI y clientes» y
  «Reintentos»

## Contexto

- Consola, el primer repositorio con `desktop/`, no cabía en el árbol de `qt.md`: el árbol solo
  tenía lugar para la interfaz y para el cliente del servidor propio, y una estructura se muestra
  completa porque es la convención ([plataformas/README.md](../plataformas/README.md), «Estructuras
  y distribución»). Consola tiene la lógica de sus tareas, el almacenamiento sobre `QSettings` y
  dos `QThread`. `flet.md` tenía el mismo hueco.
- Consola no tiene servidor propio: lee la API de Cloudflare y el índice de versiones de Flutter.
  `transversal.md` pedía fallar ante cualquier campo desconocido, con una razón que solo vale para
  el servidor propio: cliente y servidor salen del mismo contrato.
- Ninguna fuente de Qt ni de Flet dice dónde va el código que no es interfaz: es una convención
  propia.

## Decisión

1. **`qt.md` y `flet.md` agregan `services/`: lo que no es interfaz ni HTTP.** Es el nombre que
   usa `fastapi.md` para la lógica.
2. **`api/` reúne todo lo que habla HTTP:** `client.py` y `models.py` para el servidor propio, y
   `api/<servicio>.py` para cada servicio externo, con sus llamadas y sus modelos.
3. **La respuesta de un servicio externo se lee con modelos escritos a mano, que validan los campos
   que el cliente lee e ignoran los que no conoce.** Fallar ante un campo desconocido queda para
   las respuestas del servidor propio.
4. **El cliente reintenta también con un servicio externo**, con las reglas de «Reintentos».

## Consecuencias

- Consola renombra `core/` a `services/` y pasa a `api/` las llamadas a Cloudflare y al índice de
  Flutter, que hoy están en sus tareas.
- Los reintentos de Flet se escriben en `api/`, no solo en `client.py`.
- Ninguna herramienta comprueba el árbol.

## Descartado

- **`domain/` y `data/`, como `flutter.md`:** son las capas de la guía de Flutter, y agregan dos
  carpetas donde una basta.
- **Un árbol que fija lo obligatorio y admite otros paquetes:** cada repositorio nombraría distinto
  lo mismo.
- **Que Consola conserve `core/`:** un repositorio no se leería como los demás.
- **Los clientes externos en `services/`:** mezcla la lógica con lo que habla HTTP.
- **Fallar también ante un campo desconocido de un servicio externo:** la tarea se rompe por un
  campo que no usa, cada vez que el servicio agrega uno.
- **Reintentar solo con el servidor propio:** un servicio externo que se reinicia falla por la misma
  causa.
