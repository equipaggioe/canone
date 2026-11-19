# ADR-0192 · Una app de Qt no declara el dominio de su organización

- **Estado:** Aceptada. El usuario aprobó quitar el dominio de la regla (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/qt.md`](../plataformas/qt.md), «Almacenamiento»

## Contexto

`qt.md` pedía que `main.py` declarara el nombre de la organización, su dominio y el nombre de la
app, con origen en *Basic Usage* de QSettings. Consola no tiene dominio.

- Leído en *Basic Usage*: la fuente sugiere declarar la organización y la app con
  `setOrganizationName()` y `setApplicationName()`. Del dominio solo dice que, si está, macOS lo
  usa en lugar del nombre, y que si falta se deriva uno del nombre. No toma posición sobre él.
- Leído en `qsettings.cpp` de Qt 6.12.0: el constructor por defecto de `QSettings` usa en macOS el
  dominio si no está vacío y si no el nombre de la organización, y en los demás sistemas el
  nombre. Con `IniFormat`, el archivo es `<carpeta del usuario>/<eso>/<app>.ini`. No se leyó
  `qsettings_mac.cpp`.

## Decisión

1. **`main.py` declara el nombre de la organización y el de la app, y no el dominio.**

## Consecuencias

- Con `IniFormat`, la configuración queda en una carpeta con el nombre de la organización en los
  tres sistemas.
- Un producto sin dominio no tiene que inventar uno.

## Descartado

- **Exigir el dominio:** la fuente no lo pide, y su único efecto con `IniFormat` es que la carpeta
  de macOS se llame distinto que en Windows y Linux.
- **El dominio como opcional:** cada repositorio elegiría distinto, por un efecto que solo separa
  la carpeta de macOS.
