# ADR-0174 · Flet fija sus transitivas con `PIP_CONSTRAINT` y construye sin flet-build-action

- **Estado:** Aceptada. El usuario pidió aplicar lo recomendado y correr las pruebas (2026-11-17)
- **Fecha:** 2026-11-17
- **Alcance:** [`plataformas/flet.md`](../plataformas/flet.md), «Proyecto», «Almacenamiento» y
  «Entrega»; [`plataformas/transversal.md`](../plataformas/transversal.md), «Distribución»;
  [`plataformas/qt.md`](../plataformas/qt.md), «Entrega»; `fuentes/flet/` y `plantilla/`

## Contexto

Lo que dejó pendiente el
[ADR-0166](0166-flet-escribe-solo-lo-que-elige.md). Comprobado en la distro WSL `Testing`
(Debian 13), con Flet 1.1.2, Flutter 3.47.9 y uv 0.13.9:

- Dos apps con `flet build linux`: la que corrió con `PIP_CONSTRAINT` empaquetó `idna` 3.7 y
  `certifi` 2024.8.30, las de las restricciones, y la otra, `idna` 3.20 y `certifi` 2026.10.23.
- `uv export --locked --no-dev --no-emit-project --no-hashes` no escribe extras, y pip lo acepta
  como archivo de restricciones.
- Cada app construida guarda `SharedPreferences` en `~/.local/share/<bundle_id>/`: la segunda no
  leyó la clave de la primera.
- El AppImage de `build-appimage.sh`, con appimagetool 1.9.1, abre como usuario sin privilegios con
  `fuse3` y sin libfuse2, y sin `fusermount` no abre.
- Una app con `@ft.component`, `use_state` y `use_effect` pasa `flet test` con `find_by_key`, `tap`
  y `pump_and_settle`.
- `flet build aab` empaquetó para `arm64-v8a` el `idna` 3.7 que fijaba `uv.lock` y el
  `pydantic-core` 2.46.4 del índice de Flet. Con una ruta local en las restricciones, pip falla con
  `Invalid requirement: './paquete'`; `--no-emit-local` la saca.
- Para Android, un paquete local en `dev_packages` como carpeta no se construye: pip no encuentra
  `uv_build` para la plataforma. Como wheel, se empaqueta.

Leído en el `action.yml` de flet-build-action v1: corre `uv run`, sin `--locked`.

## Decisión

1. **`flet build` y `flet test` corren con `PIP_CONSTRAINT`** en el `uv.lock` exportado: pip
   resuelve las transitivas, y sin restricciones toma las últimas del día del build.
2. **Salen la regla del prefijo de las claves y la de `clear()`:** una app construida tiene sus
   propias preferencias. `client-storage.md` queda con dos convenciones y sale de `fuentes/flet/`;
   las dos pasan a propias.
3. **El release construye con `uv run flet build` después de `uv sync --locked`, sin
   flet-build-action:** con un `uv.lock` desfasado, la acción construye igual.
4. **El export lleva `--no-emit-local`, y un paquete local entra por `dev_packages` como wheel.**
5. **Ninguna app se publica en macOS ni en iOS hasta que haya cuenta de Apple Developer**, y eso
   se escribe una vez en `transversal.md`, «Distribución». Sale de `qt.md`.

## Consecuencias

- La clave del modo en `plantilla/flet/theme.py` es `theme`, sin prefijo.
- Una transitiva binaria sin wheel en el índice de Flet para Android en la versión de `uv.lock`
  hace fallar el build de Android.

## Descartado

- **Declarar las transitivas con `==` en `[project]`:** choca con «Toda dependencia declarada se
  usa» de stack.md y con deptry.
- **flet-build-action:** construye sin `--locked`.
