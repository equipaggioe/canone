# ADR-0118 · Cada página fija la versión de sus tecnologías, y la plantilla y las fuentes la siguen

- **Estado:** Aceptada. El punto 2 lo reemplaza el [ADR-0119](0119-lo-que-corre-en-el-servidor-usa-la-version-de-debian-13-y-lo-demas-la-ultima-estable.md)
- **Fecha:** 2026-11-04
- **Alcance:** `plataformas/`, `repositorio.md`, `plantilla/` y `fuentes/`

## Contexto

`fuentes/README.md` pide descargar cada fuente de la versión que se usa, pero muchas tecnologías no
tenían una versión escrita en su página. Sus copias salían de `main` o `dev`, y la plantilla declaraba
mínimos, como `pyside6>=6.11`, que ninguna página estipulaba. Comparadas con su versión, algunas
copias traían texto que esa versión no tiene: la de `pyside6-deploy` describía una sección ausente
en 6.11.

## Decisión

1. Cada página fija en «Proyecto» la versión de sus tecnologías. La plantilla y las fuentes dependen
   de ella: primero se escribe en la página, y después se ajustan.
2. Se fija la última versión estable, sin `dev` ni `beta`. Lo que sale de los paquetes de Debian 13
   conserva la versión de Debian 13.
3. Node es el 26.13.0, la última LTS, y deja de ser el de Debian 13, el 20.19.2. SvelteKit 3.1.1 pide
   `>=22.17`, y Vitest 5.1.0, `^22.12 || ^24 || >=26`. Node solo se usa para construir, así que no
   llega al servidor.
4. TypeScript es la 6.0.3, y no la última, porque es la que genera sv 1.3.0. Flet construye con el
   Flutter que fija su versión, y no con el de `flutter.md`. En Flet, Pydantic es la 2.13.4
   y no la de `python.md`, porque el índice de Flet para Android trae `pydantic-core` hasta la
   2.47.0: Pydantic 2.13.5 pide la 2.46.5, y la 2.14, la 2.50.
5. Las versiones de las acciones y los contenedores de CI van en `repositorio.md`.
6. `pyproject.toml` declara con `>=` la versión que fija la página, y `uv.lock` fija la exacta. En
   Flet, las dependencias de `[project]` van con `==`, porque `flet build` no lee `uv.lock`.

## Consecuencias

- Las fuentes con un tag de la versión fijada se descargan de ese tag. Quedan en un commit fijo las
  de Paraglide, Flutter, Dart y Kotlin, cuyos repositorios no tienen ese tag, y su texto no queda
  ligado a una versión exacta.
- Una versión nueva se adopta a mano, y cada cambio pide revisar las reglas que citan su fuente.
- Comprobado en el registro de npm: los requisitos de Node de SvelteKit y Vitest.
- Sin confirmar: que las combinaciones de versiones funcionen juntas, como Gradle 9.8.2, AGP 9.5.0 y
  Kotlin 2.4.21.

## Descartado

- **Fijar solo un commit en cada fuente:** hace reproducible la descarga, pero no liga el texto con
  la versión que se usa.
- **Declarar las versiones en la plantilla:** la plantilla se deriva de las páginas, no al revés.
- **Conservar el Node de Debian 13:** obliga a quedarse en versiones antiguas de SvelteKit y Vitest
  por una herramienta que no corre en el servidor.
