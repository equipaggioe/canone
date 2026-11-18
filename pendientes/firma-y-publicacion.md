# Firma y publicación en iOS y macOS

Tema pendiente: Canone escribe cómo se publica en iOS y en macOS como si hubiera cuenta de Apple Developer ([ADR-0180](../adr/0180-cada-plataforma-se-escribe-como-si-hubiera-cuenta-y-cada-repositorio-elige-donde-publica.md)), pero nada de eso corrió nunca.

## Estado (verificado 2026-11-18)

| Pieza | Estado |
| :--- | :--- |
| [transversal.md](../plataformas/transversal.md#distribución): las variables `RELEASE_<PIEZA>_<PLATAFORMA>`, iOS en la App Store y el DMG de macOS | Escrito |
| `verificar.py --variables`: falla si falta una variable de una pieza, si vale otra cosa o si sobra | Comprobado con un repositorio de prueba con una app de Flutter |
| `ci.yml`: el job `canone` le pasa las variables a `verificar.py`, y el job `ios` corre solo con `RELEASE_<PIEZA>_IOS` en `true` | Escrito; **nunca corrió** |
| `release.yml`: `desktop` y `flet-desktop` arman su matriz con los sistemas que se publican; `mobile-ios` y `flet-ios`; el DMG de Qt y de Flet | Escrito; **nunca corrió**. Solo se comprobó que el YAML se lee |
| [plantilla/scripts/apple.py](../plantilla/scripts/apple.py) | Escrito; pasa `ruff check` y `ruff format`. **Nunca corrió**: necesita macOS y una cuenta |
| [flutter.md](../plataformas/flutter.md#entrega): la firma manual del target `Runner` y `ios/ExportOptions.plist` | Escrito; sin comprobar que `flutter build ipa` firme así en un runner |
| `codesign --deep` sobre el `.app` de `pyside6-deploy` | Sin comprobar: Apple recomienda firmar de adentro hacia afuera, y no se sabe si Nuitka deja algo que `--deep` no cubre |
| Los ajustes de iOS ofrecen elegir el idioma de la app porque Xcode declara sus *Localizations* | Sin confirmar |

## Para cerrar el tema

1. El primer tag de un repositorio con una variable de iOS o de macOS en `true` prueba los jobs. Lo que falle se corrige en la plantilla.
2. Este documento se borra en el commit que deje todo comprobado.
