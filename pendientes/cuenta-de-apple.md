# macOS e iOS, con la cuenta de Apple Developer

Tema pendiente: **bloqueado hasta que haya cuenta de Apple Developer**. La decisión ya está tomada ([ADR-0141](../adr/0141-la-app-de-flet-genera-sus-modelos-y-se-entrega-con-los-scripts-de-flet.md)); falta escribirla y construirla.

## Estado (verificado 2026-11-13)

| Pieza | Estado |
| :--- | :--- |
| Flet en macOS: un DMG firmado con Developer ID y notarizado | Decidido; sin escribir en `flet.md` ni en `release.yml` |
| Flet en iOS: `flet build ipa`, a la App Store | Decidido; sin escribir |
| Qt en macOS | Sale del job `desktop` de `release.yml`: sin firma ni notarización, macOS 15 no abre la app |
| `install.py`: `--desktop macos` espera `desktop-macos.zip` | Sin cambiar; cambia con el formato que se elija para Qt |

## Cuándo se retoma

Cuando exista la cuenta. Entonces:

1. Copiar a `fuentes/flet/` las guías de macOS e iOS de Flet 1.1.2 y escribir sus convenciones en «Entrega» de `flet.md`: firma, notarización, DMG y el splash oscuro que pide iOS.
2. Elegir el formato de Qt en macOS: el `.app` de `pyside6-deploy` dentro de un DMG, como en Flet, o en un zip. La recomendación es el DMG, por uniformidad con Flet.
3. Agregar macOS a los jobs de escritorio y un job de iOS, con los certificados en los secretos del CI, y correrlos una vez antes de un tag real.
