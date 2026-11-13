# ADR-0140 · La cámara de capturas es de la herramienta que la corre, y canone no fija dónde va

- **Estado:** Aceptada
- **Fecha:** 2026-11-12
- **Alcance:** «Carpetas de primer nivel» de [`repositorio.md`](../repositorio.md) y
  `scripts/verificar.py`
- **Reemplaza a:** [ADR-0137](0137-la-camara-de-capturas-va-en-scripts-screenshots.md)

## Contexto

El ADR-0137 ponía la cámara de capturas en `scripts/screenshots/`, con lo que genera al lado y sin
versionar. Pero la cámara no corre sola: necesita el kit de la herramienta que la corre, que le
levanta el servidor ficticio, la página y el emulador. `repositorio.md` reserva `scripts/` para lo
que es del repositorio entero, y el `README.md`, «Responsabilidades», dice que canone no impone qué
herramienta corre sus programas. Una carpeta que solo sirve con una herramienta es de esa
herramienta.

## Decisión

1. **`repositorio.md` no fija dónde va la cámara de capturas ni lo que genera.** Lo fija la
   herramienta que la corre, en su propia carpeta del repositorio.
2. **`verificar.py` deja de revisar `scripts/screenshots/`.**

## Consecuencias

- Lo que publica una pieza sigue dentro de esa pieza, como pide `repositorio.md` para todo lo de
  una sola pieza.
- Un repositorio que tenga la cámara en `scripts/screenshots/` la mueve a la carpeta de la
  herramienta que la corre.

## Descartado

- **La cámara en `scripts/screenshots/` (ADR-0137).** `scripts/` guardaría un programa que no corre
  sin una herramienta, y lo que genera.
