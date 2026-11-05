# ADR-0120 · Una convención propia puede enlazar el documento en el que se basa

- **Estado:** Aceptada
- **Fecha:** 2026-11-05
- **Alcance:** `plataformas/README.md`, `plataformas/` y `fuentes/`

## Contexto

El [ADR-0117](0117-una-fuente-se-cita-si-evita-escribir-al-menos-tres-convenciones.md) saca de las citas
la fuente que evita escribir menos de tres convenciones, y esas convenciones pasan a propias. Una propia
no podía mencionar una fuente que la página no cita: se perdía de dónde salía, y al cambiar de versión
nada indicaba que había que revisarla.

## Decisión

1. Una convención propia puede enlazar el documento en el que se basa, en su versión fija, cuando dice
   lo mismo que el documento.
2. El enlace no adopta el resto del documento, no cuenta para «Aporta» y no lleva copia en `fuentes/`.
3. Salen 35 fuentes que no cumplían los requisitos, y lo que decidían queda escrito en su página.

## Consecuencias

- Buscar una versión, como `svelte@5.57.3`, muestra las propias que hay que revisar al cambiarla.
- Cada cambio de versión obliga a actualizar esos enlaces.
- `scripts/verificar.py` no revisa los enlaces externos, y sin copia el texto de una página web sin
  versiones puede cambiar sin que se note.
- Las propias que ya existían reciben su enlace cuando se revise su página.

## Descartado

- **Bajar el umbral de «Aporta» a dos:** salvaba 5 fuentes, a cambio de mantener una copia completa por
  cada dos frases.
- **Propias sin enlace:** no se vería de dónde sale cada una, ni qué revisar al cambiar de versión.
