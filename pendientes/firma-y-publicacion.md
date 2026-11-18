# Firma y publicación en iOS, macOS y Windows

Tema pendiente: Canone escribe cómo se publica en iOS y en macOS como si hubiera cuenta de Apple Developer ([ADR-0180](../adr/0180-cada-plataforma-se-escribe-como-si-hubiera-cuenta-y-cada-repositorio-elige-donde-publica.md)), pero nada de eso corrió nunca, y quedan decisiones abiertas.

## Estado (verificado 2026-11-18)

| Pieza | Estado |
| :--- | :--- |
| [transversal.md](../plataformas/transversal.md#distribución): las variables `RELEASE_*`, iOS en la App Store y el DMG de macOS | Escrito |
| `ci.yml`: el job `canone` falla si falta una variable `RELEASE_*`, y el job `ios` corre solo con `RELEASE_IOS` en `true` | Escrito; **nunca corrió** |
| `release.yml`: `desktop` y `flet-desktop` arman su matriz con los sistemas que se publican; `mobile-ios` y `flet-ios`; el DMG de Qt y de Flet | Escrito; **nunca corrió**. Solo se comprobó que el YAML se lee |
| [plantilla/scripts/apple.py](../plantilla/scripts/apple.py) | Escrito; pasa `ruff check` y `ruff format`. **Nunca corrió**: necesita macOS y una cuenta |
| [flutter.md](../plataformas/flutter.md#entrega): la firma manual del target `Runner` y `ios/ExportOptions.plist` | Escrito; sin comprobar que `flutter build ipa` firme así en un runner |
| `codesign --deep` sobre el `.app` de `pyside6-deploy` | Sin comprobar: Apple recomienda firmar de adentro hacia afuera, y no se sabe si Nuitka deja algo que `--deep` no cubre |
| Los ajustes de iOS ofrecen elegir el idioma de la app porque Xcode declara sus *Localizations* | Sin confirmar |

## Sin decidir

| Decisión | Opciones | Recomendación |
| :--- | :--- | :--- |
| **Cómo se firman los instaladores de Windows.** Hoy van sin firmar, y elegir el servicio es una decisión del stack | 1. Azure Artifact Signing, de Microsoft, con el `signtool` del runner. 2. Un certificado OV en un HSM en la nube, como DigiCert KeyLocker o SSL.com eSigner. 3. Seguir sin firmar | **La 1**, si admite al país de quien firma (**sin confirmar**): es de Microsoft y la más barata. Si no lo admite, la 2 |
| **El login de Flutter en iOS con la URI `https` de retorno.** flutter_appauth 13.0.0 usa AppAuth-iOS 3.0.0, que abre `ASWebAuthenticationSession` con `callbackURLScheme` (leído en `OIDExternalUserAgentIOS.m`). Esa API recibe un esquema, no una URI `https`, así que el retorno no llegaría a la app (**sin confirmar** en ejecución) | 1. Un esquema propio solo en iOS, lo que cambia [autenticacion.md](../plataformas/autenticacion.md#código-de-autorización). 2. Un plugin propio con el retorno `https` de `ASWebAuthenticationSession`, desde iOS 17.4. 3. Esperar a que AppAuth lo admita | **La 1**: `ASWebAuthenticationSession` devuelve el retorno solo a la app que abrió la sesión, así que otra app no puede robarlo aunque registre el mismo esquema (**sin confirmar**) |
| **Los canales de notificación en Flutter en Android.** El manifiesto puede nombrar un canal por defecto, pero algo tiene que crearlo | 1. Código de Kotlin en `MainActivity` que crea los canales. 2. flutter_local_notifications, un paquete más en el stack | **La 1**: no suma un paquete |
| **El perfil de App Store en CI** | 1. Un secreto por app, como hoy. 2. Bajarlo en cada corrida con la API de App Store Connect y `apple-actions/download-provisioning-profiles`, como recomienda Flet: es una acción más en el stack | **La 1**, mientras haya una app por repositorio: regenerar el perfil obliga a actualizar el secreto |
| **El idioma por app en Android antes de la API 33.** Sin AppCompat, Android no tiene ajuste de idioma por app hasta la API 33, y la app sigue el del sistema | 1. Aceptarlo. 2. Un selector dentro de la app | **La 1**: el usuario elige igual, con el idioma del sistema |

## Para cerrar el tema

1. El primer tag de un repositorio con `RELEASE_IOS` o `RELEASE_MACOS` en `true` prueba los jobs. Lo que falle se corrige en la plantilla.
2. Cada decisión de la tabla se escribe en su página y en un ADR.
3. Este documento se borra en el commit que deje todo comprobado y decidido.
