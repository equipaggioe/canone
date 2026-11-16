# ADR-0156 · Una imagen que se muestra en varios tamaños se guarda una vez por tamaño, en la carpeta de su fila

- **Estado:** Aceptada
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md), «Archivos»; `services/files.py`, `tests/test_files.py` y `tests/test_tasks.py` de `plantilla/server/`

## Contexto

`fastapi.md` guardaba un archivo por fila, con el nombre del ID de la fila, y volvía a codificar
cada imagen una vez. Una app que muestra la misma imagen en una lista de tarjetas y en grande
servía el mismo archivo en las dos: una pantalla de tarjetas bajaba la imagen entera de cada una.
Concordia ya guardaba tres tamaños por foto, fuera de la convención. Servir varios tamaños de una
imagen es lo que recomienda la web (MDN, *Responsive images*).

## Decisión

1. **Una imagen que se muestra en más de un tamaño se guarda una vez por tamaño**, en WebP, en la
   carpeta del ID de su fila: `<id>/<tamaño>.webp`. El lado mayor de cada tamaño es una constante
   del recurso, y el original no se guarda.
2. **`files.sizes`** decodifica la imagen una vez y codifica cada tamaño derecho y sin metadatos;
   **`files.store_sizes`** los escribe.
3. **El barrido** borra también la carpeta de tamaños sin fila.

## Consecuencias

- Una imagen de un solo tamaño sigue siendo un archivo con el nombre del ID de su fila.
- Cada subida codifica una vez por tamaño: más CPU al subir, menos bytes en cada pantalla.
