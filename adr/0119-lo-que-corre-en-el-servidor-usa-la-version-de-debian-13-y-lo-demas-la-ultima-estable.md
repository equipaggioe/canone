# ADR-0119 · Lo que corre en el servidor usa la versión de Debian 13, y lo demás la última estable

- **Estado:** Aceptada
- **Fecha:** 2026-11-05
- **Alcance:** `plataformas/`, `plantilla/` y `scripts/verificar.py`

## Contexto

El [ADR-0118](0118-cada-pagina-fija-la-version-de-sus-tecnologias-y-la-plantilla-y-las-fuentes-la-siguen.md)
conservaba la versión de Debian 13 en lo que sale de sus paquetes. Ese criterio mira si hay un paquete,
y no si el programa se usa en el servidor: dejaba al JDK en el 21, aunque solo construye. Además, la
regla estaba solo en el ADR, que no es norma, y `verificar.py` no comprobaba la mayoría de las versiones.

## Decisión

1. Lo que corre en el servidor usa la versión de Debian 13, también en desarrollo y en CI: Python,
   PostgreSQL con PostGIS, Valkey y los programas de la máquina.
2. Lo que no corre en el servidor usa la última versión estable, o la última LTS si la tecnología las
   publica. El JDK pasa al 25.0.5.
3. La regla va en «Versiones» de `plataformas/README.md`.
4. `verificar.py` comprueba las versiones de cada página en los manifiestos y los workflows de cada
   repositorio, y `--canone`, en la plantilla y en los workflows de Canone.

## Consecuencias

- Qt y Flet siguen en Python 3.13, aunque no corren en el servidor: un solo intérprete y una sola
  versión de las fuentes de Python, sin una falla que resolver.
- Con el JDK 25, Android Lint agota 512 MB de Metaspace: `gradle.properties` lleva 2 GB.
- Un repositorio que no migró falla en `verificar.py`, y por lo tanto en CI, hasta actualizarse.
- Comprobado en `equipaggio/mobile` con el JDK 25: el APK, lint, las pruebas unitarias y ktlint.
- Sin confirmar: el JDK 25 en el CI de la plantilla.

## Descartado

- **Python 3.14 en Qt y Flet:** sus pruebas pasan, pero separa las piezas sin resolver una falla.
- **Conservar el JDK 21:** funciona, pero el JDK no corre en el servidor.
