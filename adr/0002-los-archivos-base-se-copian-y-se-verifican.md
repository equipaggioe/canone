# ADR-0002 · Los archivos base se copian y un script verifica la copia

- **Estado:** Propuesta
- **Fecha:** 2026-09-22
- **Alcance:** `server/app/models/base.py`, `server/app/schemas/base.py`

## Contexto

`schemas/base.py` es idéntico byte a byte en los seis repositorios. `models/base.py` empezó igual y
hoy tiene cinco contenidos distintos en seis copias: dos repositorios arreglaron el CHECK de los enums, uno arregló
las columnas geográficas y uno agregó tipos de importe propios. Las mejoras quedaron encerradas en
el repositorio donde se descubrieron.

Hay dos formas de que dejen de divergir: un paquete de Python compartido, o una copia verificada.

## Decisión

1. Los archivos base son **archivos canónicos** de `canone/plantilla/`, se copian sin editar y
   quedan excluidos de `ruff`.
2. `canone/scripts/verificar.py` compara la copia de cada repositorio con la canónica y falla si
   difieren. Corre en el CI de cada repositorio.
3. Un repositorio que necesita un tipo propio (`Amount`, `TaxRate` en vettore) lo declara en otro
   archivo, no dentro del canónico.
4. Una mejora descubierta en un repositorio se sube primero a `canone` y desde ahí baja a todos.

## Consecuencias

- Cada repositorio sigue siendo autónomo: se clona y corre sin instalar nada de `canone`.
- La divergencia deja de ser silenciosa, que es lo que la hizo cara.
- Bajar una mejora es un commit por repositorio, a mano. Con seis repositorios es aceptable; con
  veinte no lo sería.

## Descartado

- **Un paquete de Python compartido (`canone-py`, instalado desde git):** es la solución más limpia
  para la duplicación, y es la que habría que elegir si la cantidad de repositorios creciera. Se
  descarta hoy porque agrega un paso de publicación y de versionado entre piezas que hoy se
  despliegan juntas, y porque `base.py` cambia unas pocas veces al año. **Si el script de
  verificación empieza a fallar seguido, esta es la respuesta.**
- **Un submódulo de git:** arrastra el repositorio entero a cada clon y se olvida de actualizar.
