# ADR-0243 · `verificar.py` lee las versiones de `stack.md`, y `stack.md` se revisa con los cinco pasos

- **Estado:** Aceptada. Lo confirmó el usuario el 2026-11-25, al pedir la revisión repetible y que se
  aplicaran las recomendaciones sin una razón registrada en contra. Los puntos marcados *(propuesta)*
  se eligieron al implementar
- **Fecha:** 2026-11-25
- **Alcance:** [`stack.md`](../stack.md), [`plataformas/README.md`](../plataformas/README.md),
  [`plataformas/android.md`](../plataformas/android.md),
  [`plataformas/despliegue.md`](../plataformas/despliegue.md), `scripts/verificar.py`,
  `.github/workflows/` y `plantilla/`

## Contexto

Con el [ADR-0148](0148-el-stack-se-fija-en-stack-md-y-la-ruta-de-lectura-va-por-pagina.md),
`verificar.py` repetía las versiones de `stack.md`. Comprobado el 2026-11-25 con un repositorio que
declara mal cada versión: pasaban Playwright en el servidor, oauth2, url_launcher, web, el SDK de
Dart, cuatro plugins y las 29 bibliotecas de Android, las API de Android, ktlint y el contenedor
`debian`. Una versión cambiada solo en `stack.md` también pasaba, y `play.py` declaraba google-auth
2.62.2.

Comprobado el 2026-11-25 con las versiones nuevas:

- **Servidor**, en Debian 13 con uv 0.13.10 y Babel 2.19.0: `uv lock --check`, ruff, Pyrefly,
  deptry y pip-audit pasan, y pytest da 448 pruebas pasadas y 1 saltada.
- **Qt y Flet:** datamodel-code-generator 0.102.0 genera lo mismo que la 0.100.0.
- **SvelteKit**, con Node 26.13.1 y pnpm 12.23.0, en `landing/` y `panel/` de un repositorio:
  instalación, build, `svelte-check`, lint y knip pasan. pnpm agrega a `minimumReleaseAgeExclude`, en
  `pnpm-workspace.yaml`, una versión con menos de un día.
- **Flutter** 3.47.5: los paquetes resuelven, y swagger_parser 2.4.0 genera desde el `openapi.json`,
  compila y rechaza un campo y un valor de enum desconocidos.
- **Android**, con el JDK 25.0.5, Gradle 9.9.2, AGP 9.5.2, el BOM de Compose 2026.11.01 y Lifecycle
  2.11.1: las pruebas, lint, ktlint, `buildHealth` y el APK de depuración pasan, y compila un
  `NavDisplay` de Navigation 3 1.2.2. `ui-test-junit4` trae `espresso-core` 3.5.0 con el BOM
  2026.09.00, y 3.7.0 con el 2026.11.01. Sin `constraints`, llegan `core-ktx` 1.18.0 y 1.19.1, y
  Gradle elige la segunda.
- **rest-server 0.15.0:** `scripts/infra/backup.sh` pasa en un Debian 13 arrancado con
  `systemd-nspawn`, igual que con la 0.14.0.

## Decisión

1. **`verificar.py` lee las versiones de las tablas de `stack.md`**, y falla si falta una fila que
   nombra.
2. **Comprueba también** Playwright en `pyproject.toml`, cada paquete de Flutter y Dart en
   `pubspec.yaml`, los plugins, las bibliotecas, las API y ktlint de Android, y cada contenedor.
3. **`stack.md` se revisa con los cinco pasos**, adaptados en «Revisión de stack.md».
4. **Sale de «Qué entra» la lista de páginas:** cada una ya enlaza la regla.
5. **`despliegue.md` no repite las versiones de rest-server y restic.**
6. **Entra appimagetool**, con la versión del script de Flet.
7. **Suben a la última estable** uv, Babel, datamodel-code-generator, pnpm, vite-plugin-svelte,
   typescript-eslint, maplibre_gl, swagger_parser, Gradle, AGP, el BOM de Compose, Lifecycle,
   Navigation 3, rest-server y setup-uv.
8. *(propuesta)* **`@types/node`, `@axe-core/playwright` y `@stripe/stripe-js` no suben hoy:** sus
   versiones nuevas tienen menos de un día, y con ellas pnpm edita `pnpm-workspace.yaml`, que es
   canónico.
9. *(propuesta)* **`--canone` compara además la plantilla y los scripts de Canone** con `stack.md`,
   y `fuentes.yml` corre cuando cambian.
10. *(propuesta)* **`espresso-core` sale** de `stack.md` y de `android.md`: con el BOM nuevo llega en
    la 3.7.0, y el código no lo importa.
11. *(propuesta)* **`play.py` declara `google-auth[requests]`** y no requests, que su código no
    importa.
12. *(propuesta)* **Flutter y Flet toman del bloque de Android el `androidx.credentials` de
    `packages/passkey/`**, sin repetir la fila.

## Consecuencias

- Subir una versión es cambiar `stack.md`, la plantilla y los manifiestos.
- Un repositorio falla en `verificar.py`, y por lo tanto en CI, hasta declarar las versiones nuevas, y
  uv 0.13.9 deja de correr en el que ya pida la 0.13.10.
- Una biblioteca nueva de Android en `stack.md` se agrega también a `BIBLIOTECAS`.
- Sin confirmar: Flutter 3.47.9, la prueba instrumentada de Android, setup-uv v10.4.0 en GitHub
  Actions y `backup.ps1` con rest-server 0.15.0.

## Descartado

- **Nombrar requests en `stack.md`:** llega dentro de google-auth y el código no lo importa.
- **Una fila por cada paquete que instala `packages.py`:** la lista está en «Máquina» de
  `despliegue.md`, y su versión es la de Debian.
