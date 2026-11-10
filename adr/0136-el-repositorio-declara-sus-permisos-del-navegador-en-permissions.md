# ADR-0136 · El repositorio declara las funciones de `Permissions-Policy` que usa en `permissions`

- **Estado:** Aceptada
- **Fecha:** 2026-11-10
- **Alcance:** «Archivos del raíz» de [`repositorio.md`](../repositorio.md), «Caddy» de
  [`plataformas/despliegue.md`](../plataformas/despliegue.md) y `scripts/verificar.py`

## Contexto

`install.py --allow` permite cada función de `Permissions-Policy` que usa la app, y Canone no decía
de dónde salen. Quien desplegaba las escribía en su propia configuración, fuera del repositorio:
la lista no se versionaba con el código que usa la cámara o la ubicación, y nada revisaba los
nombres antes de llegar a la máquina.

## Decisión

1. El archivo `permissions` del raíz del repositorio lleva las funciones que usa la app, una por
   línea, con el nombre que acepta `install.py --allow`. Sin el archivo, la app no permite ninguna.
2. Quien despliega pasa cada línea a `install.py --allow`.
3. `verificar.py` falla si una línea no es una función de `FEATURES` de `install.py`.

## Consecuencias

- Una función nueva entra en el mismo commit que el código que la usa.
- Que la máquina la permita pide volver a correr `install.py`.
- La política es una sola para las tres superficies.

## Descartado

- **Que el archivo viaje en el release y `deploy.py` escriba la cabecera en Caddy:** aplica el
  cambio al desplegar y permite una política por superficie, pero suma `release.yml`, `deploy.py`,
  la recarga de Caddy y la vuelta a la versión anterior para una lista que cambia muy poco.
- **Una línea `Permisos:` en el `README.md`:** mezcla un dato que lee un programa con el texto
  para personas.
- **Deducirlas del código**, buscando llamadas como `getUserMedia`: no ve lo que usan las
  bibliotecas.
