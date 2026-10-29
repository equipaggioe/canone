# plantilla

Los archivos que se copian a un repositorio. No es un proyecto que corra, y **no es una lista de lo
que un repositorio debe tener**: se copia solo lo de las plataformas que el producto use.

Cada archivo sale de una regla de [plataformas/](../plataformas/), y la página lo nombra. Un
archivo **canónico** se copia sin editar y `scripts/verificar.py` comprueba que la copia no se haya
separado ([ADR-0002](../adr/0002-los-archivos-base-se-copian-y-se-verifican.md)). Un **punto de
partida** se copia y después es del repositorio. Un archivo que **se instala** no se copia al
repositorio: un script de canone lo instala en el servidor con los datos de cada app
([ADR-0069](../adr/0069-el-servidor-se-instala-desde-plantilla-infra-y-sus-cabeceras-no-frenan-a-las-apps.md)).

| Archivo | Destino | Tipo | Página |
|---|---|---|---|
| `.gitattributes` | Raíz | Canónico | [repositorio.md](../repositorio.md) |
| `.gitignore` | Raíz | Punto de partida | [repositorio.md](../repositorio.md) |
| `.github/workflows/ci.yml` | Raíz | Punto de partida: se quitan los jobs de las piezas que no hay y `PIEZA` toma el nombre de la carpeta | [repositorio.md](../repositorio.md), [python.md](../plataformas/python.md) |
| `.github/workflows/release.yml` | Raíz | Punto de partida: se quitan los jobs de las piezas que no hay y `PIEZA` toma el nombre de la carpeta | [despliegue.md](../plataformas/despliegue.md) |
| `scripts/deploy.py` | `scripts/` | Punto de partida: `PRODUCTO` y `OWNER` toman los nombres del repositorio, y se ajustan `TOKEN`, `UNITS` y `DESKTOP` | [despliegue.md](../plataformas/despliegue.md#versiones) |
| `infra/` | El servidor | Se instala: `install.py <app> <dominio> <memoria>` corre la primera vez como `root` con `--admin`, dos `--key` y dos `--signer`, y crea la cuenta que administra la máquina con esas llaves y la contraseña de `sudo` que pide; después corre con `sudo` desde esa cuenta. Crea el usuario de la app, el de su dueño y el de su receptora, su base con sus dos roles y sus dos `database_url`, su instancia de Valkey con ese `maxmemory`, sus sitios de Caddy el acceso de la receptora por `ssh` y el firewall de nftables, agrega cada `--signer` a las llaves que firman los releases, enciende `unattended-upgrades` con el reinicio de las 04:00, deja `ssh` solo con llaves y sin `root`, bloquea la contraseña de `root`, y falla si la máquina tiene menos swap que memoria, si no tiene `sudo` o `unattended-upgrades`, si `systemd-timesyncd` no está habilitado, si es nueva y no recibe dos `--signer`, si recibe `--turn` y no tiene coturn, si una llave no es válida, si no recibe `--admin` y no lo lanza `sudo` desde una cuenta con llave, o si la cuenta es una de la app; `--without` quita `sweep`, `web`, `panel` o `landing` si la app no los tiene, `--allow` permite cada función de `Permissions-Policy` que usa, `--extension` crea cada extensión de PostgreSQL que necesita, y `--turn` instala coturn con su secreto y abre sus puertos, con `--turn-ip` si la IP pública le llega por NAT. `credentials.py <app>` cifra las credenciales que lee por stdin, una línea `campo=valor` por credencial, cada una en la carpeta y con el nombre que carga su unidad, y reinicia el servidor si corre | [despliegue.md](../plataformas/despliegue.md#procesos) |
| `receiver/` | La receptora de los respaldos | No se copia: corre en la receptora, `backup.ps1` en Windows y `backup.sh` en Linux | [despliegue.md](../plataformas/despliegue.md#respaldos) |
| `scripts/tokens.py` | `scripts/` | Canónico | [transversal.md](../plataformas/transversal.md) |
| `brand/tokens/` | `brand/tokens/` | Punto de partida | [transversal.md](../plataformas/transversal.md) |
| `python/.gitignore` | Cada pieza Python | Punto de partida | [python.md](../plataformas/python.md) |
| `server/pyproject.toml` | `server/` | Punto de partida | [python.md](../plataformas/python.md), [fastapi.md](../plataformas/fastapi.md) |
| `server/alembic.ini`, `alembic/README`, `alembic/env.py`, `alembic/script.py.mako` | `server/` | Canónico | [fastapi.md](../plataformas/fastapi.md) |
| `server/src/app/database.py`, `tracing.py`, `models/__init__.py`, `models/base.py`, `models/ruff.toml`, `routers/problems.py`, `schemas/base.py`, `schemas/page.py` | `server/src/app/` | Canónico | [fastapi.md](../plataformas/fastapi.md), [postgres.md](../plataformas/postgres.md) |
| `server/src/app/` (el resto) | `server/src/app/` | Punto de partida | [fastapi.md](../plataformas/fastapi.md) |
| `server/tests/test_conventions.py` | `server/tests/` | Canónico | [fastapi.md](../plataformas/fastapi.md), [postgres.md](../plataformas/postgres.md) |
| `server/tests/conftest.py`, `__init__.py` | `server/tests/` | Punto de partida | [fastapi.md](../plataformas/fastapi.md) |
| `qt/pyproject.toml` | `desktop/` | Punto de partida | [python.md](../plataformas/python.md), [qt.md](../plataformas/qt.md) |
| `qt/theme.py` | `desktop/src/app/` | Punto de partida | [qt.md](../plataformas/qt.md) |
| `qt/tests/test_theme.py` | `desktop/tests/` | Canónico | [qt.md](../plataformas/qt.md) |
| `flet/pyproject.toml` | La pieza Flet | Punto de partida | [python.md](../plataformas/python.md), [flet.md](../plataformas/flet.md) |
| `flet/theme.py` | `src/` de la pieza | Punto de partida | [flet.md](../plataformas/flet.md) |
| `flet/tests/test_theme.py` | `tests/` de la pieza | Canónico | [flet.md](../plataformas/flet.md) |
| `sveltekit/.prettierrc` | Cada superficie SvelteKit | Canónico | [sveltekit.md](../plataformas/sveltekit.md) |
| `sveltekit/.gitignore`, `svelte.config.js`, `uno.config.ts` | Cada superficie SvelteKit | Punto de partida | [sveltekit.md](../plataformas/sveltekit.md) |
| `flutter/analysis_options.yaml` | Cada app Flutter | Canónico | [flutter.md](../plataformas/flutter.md) |
| `flutter/.gitignore` | Cada app Flutter | Punto de partida | [repositorio.md](../repositorio.md) |
| `android/.editorconfig` | `mobile/` | Canónico | [android.md](../plataformas/android.md) |
| `android/gradle/wrapper/gradle-wrapper.properties` | `mobile/gradle/wrapper/` y `android/gradle/wrapper/` de cada app Flutter | Canónico | [android.md](../plataformas/android.md), [flutter.md](../plataformas/flutter.md) |
| `android/.gitignore` | `mobile/` | Punto de partida | [repositorio.md](../repositorio.md) |
