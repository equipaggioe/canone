# Plantilla

Los archivos que se copian a un repositorio. No es un proyecto que corra, y **no es una lista de lo que un repositorio debe tener**: se copia solo lo de las plataformas que el producto use.

Cada archivo sale de una convención de [repositorio.md](../repositorio.md) o de una página de [plataformas/](../plataformas/), y esa página lo nombra. Un archivo **canónico** se copia sin editar y `scripts/verificar.py` comprueba que la copia no se haya separado. Un **punto de partida** se copia y después es del repositorio. Un archivo que **se instala** no se copia al repositorio: un script de Canone lo instala en el servidor con los datos de cada app. Un archivo **en desarrollo** todavía no se copia.

Un archivo canónico tiene una única versión aquí. Toda modificación se hace primero aquí y después se propaga a los repositorios que lo usan; una copia de un repositorio no sirve de origen para actualizar las demás. Lo que se instala se mantiene y se actualiza aquí, sin implementaciones paralelas en los repositorios.

| Archivo | Destino | Tipo | Página |
| :--- | :--- | :--- | :--- |
| `.gitattributes` | Raíz | Canónico | [repositorio.md](../repositorio.md) |
| `.gitignore` | Raíz | Punto de partida | [repositorio.md](../repositorio.md) |
| `.github/workflows/ci.yml` | Raíz | Punto de partida: se quitan los jobs de las piezas que no hay, `PIEZA` toma el nombre de la carpeta y `PRODUCTO`, el del repositorio | [repositorio.md](../repositorio.md), [python.md](../plataformas/python.md) |
| `.github/workflows/release.yml` | Raíz | Punto de partida: se quitan los jobs y los pasos de las piezas que no hay, `PIEZA` toma el nombre de la carpeta, `PAQUETE`, el identificador de la app en Play, y `PIEZA_JAVA` y `CLASE`, la carpeta de una pieza en Java y su clase con `main` | [despliegue.md](../plataformas/despliegue.md) |
| `infra/` | El servidor | Se instala: `authorize.py`, `packages.py`, `swap.py`, `uv.py`, `install.py`, `credentials.py`, `deploy.py`, `database.py` y `uninstall.py` corren en el servidor e instalan las unidades, los sitios y la configuración de la carpeta, con los datos de cada app. Qué hace y qué recibe cada uno está en [despliegue.md](../plataformas/despliegue.md) | [despliegue.md](../plataformas/despliegue.md), [java.md](../plataformas/java.md) |
| `receiver/` | La receptora de los respaldos | No se copia: corre en la receptora, `backup.ps1` en Windows y `backup.sh` en Linux | [despliegue.md](../plataformas/despliegue.md#respaldos) |
| `scripts/play.py` | `scripts/` | Canónico, con una app de `mobile/` | [despliegue.md](../plataformas/despliegue.md) |
| `scripts/apple.py` | `scripts/` | Canónico, con una versión de iOS o de macOS | [despliegue.md](../plataformas/despliegue.md) |
| `scripts/java.py` | `scripts/` | Canónico, con una pieza en Java | [java.md](../plataformas/java.md) |
| `scripts/tokens.py` | `scripts/` | Canónico, con un cliente | [transversal.md](../plataformas/transversal.md) |
| `brand/tokens/` | `brand/tokens/` | Punto de partida, con un cliente | [transversal.md](../plataformas/transversal.md) |
| `python/.gitignore` | Cada pieza Python | Punto de partida | [repositorio.md](../repositorio.md), [python.md](../plataformas/python.md) |
| `server/pyproject.toml` | `server/` | Punto de partida | [python.md](../plataformas/python.md), [fastapi.md](../plataformas/fastapi.md) |
| `server/alembic.ini`<br>`alembic/README`<br>`alembic/env.py`<br>`alembic/script.py.mako` | `server/` | Canónico | [fastapi.md](../plataformas/fastapi.md) |
| `server/src/app/database.py`<br>`openapi.py`<br>`store.py`<br>`tracing.py`<br>`models/base.py`<br>`models/ruff.toml`<br>`routers/problems.py`<br>`schemas/base.py`<br>`schemas/page.py`<br>`services/files.py`<br>cada `__init__.py` | `server/src/app/` | Canónico | [fastapi.md](../plataformas/fastapi.md), [postgres.md](../plataformas/postgres.md) |
| `server/tests/__init__.py`<br>`test_conventions.py`<br>`test_events.py`<br>`test_files.py`<br>`test_tasks.py` | `server/tests/` | Canónico | [fastapi.md](../plataformas/fastapi.md), [postgres.md](../plataformas/postgres.md) |
| `server/` (el resto) | `server/` | Punto de partida | [fastapi.md](../plataformas/fastapi.md) |
| `qt/pyproject.toml`<br>`pysidedeploy.spec` | `desktop/` | Punto de partida | [python.md](../plataformas/python.md), [qt.md](../plataformas/qt.md) |
| `qt/src/app/api/ruff.toml`<br>`services/ruff.toml` | `desktop/src/app/` | Canónico | [qt.md](../plataformas/qt.md) |
| `qt/theme.py` | `desktop/src/app/` | Punto de partida | [qt.md](../plataformas/qt.md) |
| `qt/tests/test_theme.py`<br>`test_accessibility.py` | `desktop/tests/` | Canónico | [qt.md](../plataformas/qt.md) |
| `qt/tests/conftest.py` | `desktop/tests/` | Punto de partida: el fixture `screen` con la ventana y las bandas de la app | [qt.md](../plataformas/qt.md) |
| `flet/pyproject.toml`<br>`installer.iss`<br>`build-appimage.sh` | La pieza Flet | Punto de partida | [python.md](../plataformas/python.md), [flet.md](../plataformas/flet.md) |
| `flet/src/api/ruff.toml` | `src/` de la pieza | Canónico | [flet.md](../plataformas/flet.md) |
| `flet/theme.py` | `src/` de la pieza | Punto de partida | [flet.md](../plataformas/flet.md) |
| `flet/tests/test_theme.py` | `tests/` de la pieza | Canónico | [flet.md](../plataformas/flet.md) |
| `packages/sms/` | `packages/sms/`, si una app de Flet lee el código por SMS | Canónico | [flet.md](../plataformas/flet.md#código-por-sms) |
| `packages/passkey/` | `packages/passkey/`, si una app de Flutter o de Flet usa la passkey en el teléfono, en Windows o en macOS | Canónico | [autenticacion.md](../plataformas/autenticacion.md#passkeys), [flutter.md](../plataformas/flutter.md#passkeys), [flet.md](../plataformas/flet.md#passkeys) |
| `sveltekit/.prettierrc`<br>`knip.json`<br>`pnpm-workspace.yaml`<br>`static/theme.js`<br>`src/lib/version.ts` | Cada superficie SvelteKit | Canónico | [sveltekit.md](../plataformas/sveltekit.md) |
| `sveltekit/.gitignore` | Cada superficie SvelteKit | Punto de partida | [repositorio.md](../repositorio.md), [sveltekit.md](../plataformas/sveltekit.md) |
| `sveltekit/.prettierignore`<br>`eslint.config.js`<br>`vite.config.ts`<br>`playwright.config.ts`<br>`uno.config.ts`<br>`src/lib/theme.ts` | Cada superficie SvelteKit | Punto de partida | [sveltekit.md](../plataformas/sveltekit.md) |
| `flutter/analysis_options.yaml` | Cada app Flutter | Canónico | [flutter.md](../plataformas/flutter.md) |
| `flutter/.gitignore` | Cada app Flutter | Punto de partida | [repositorio.md](../repositorio.md), [flutter.md](../plataformas/flutter.md) |
| `android/.editorconfig` | `mobile/` | Canónico | [android.md](../plataformas/android.md) |
| `android/gradle/wrapper/gradle-wrapper.properties` | `mobile/gradle/wrapper/` y `android/gradle/wrapper/` de cada app Flutter | Canónico | [android.md](../plataformas/android.md), [flutter.md](../plataformas/flutter.md) |
| `android/.gitignore` | `mobile/` | Punto de partida | [repositorio.md](../repositorio.md), [android.md](../plataformas/android.md) |
