# ADR-0137 · La cámara de capturas va en `scripts/screenshots/`, y lo que genera no se versiona

- **Estado:** Aceptada
- **Fecha:** 2026-11-12
- **Alcance:** «Carpetas de primer nivel» de [`repositorio.md`](../repositorio.md) y
  `scripts/verificar.py`

## Contexto

Un producto saca las capturas que publica —en la landing, en las tiendas, para la prensa— con un
script que recorre sus pantallas sobre un escenario de datos de ejemplo. Canone no decía dónde va
ese script ni qué pasa con lo que genera, y `verificar.py` marcaba cualquier carpeta propia como
«no es un nombre de pieza».

Lo que hace la cámara decide dónde va:

| Qué | Qué es |
| :--- | :--- |
| La cámara | Código que se ejecuta en desarrollo y recorre varias piezas |
| El escenario | Datos que solo lee la cámara |
| Las capturas crudas y las de las tiendas y la prensa | Lo genera la cámara, y se vuelve a sacar con ella |
| Las capturas que publica una pieza, como la landing | Las usa el build de esa pieza |

## Decisión

1. La cámara y su escenario van en `scripts/screenshots/`: son del repositorio entero, porque
   recorren varias piezas.
2. Lo que genera la cámara no se versiona, salvo lo que publica una pieza, que va dentro de esa
   pieza.
3. `verificar.py` falla si `scripts/screenshots/` versiona una imagen.

## Consecuencias

- Una cámara nueva no abre otra carpeta de primer nivel.
- Las capturas de las tiendas y la prensa no quedan en el historial: se vuelven a sacar.

## Descartado

- **`brand/`:** guarda el logo y los colores, que no corren en ningún lado y leen las piezas. La
  cámara corre, y ninguna pieza la lee.
- **Una carpeta fija `demo/`:** junta en un nivel propio código que se ejecuta con lo que
  genera, y `scripts/` ya es el lugar de lo que es del repositorio entero.
- **Dentro de una pieza:** la cámara recorre varias.
