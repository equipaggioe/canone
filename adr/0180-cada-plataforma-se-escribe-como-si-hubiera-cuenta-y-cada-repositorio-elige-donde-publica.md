# ADR-0180 · Cada plataforma se escribe como si hubiera cuenta, y cada repositorio elige dónde publica

- **Estado:** Aceptada. El usuario pidió escribir las reglas de iOS como si ya hubiera cuenta de
  Apple, que la plataforma de cada repositorio sea un parámetro, también Windows, y aplicar lo
  recomendado (2026-11-18). Los puntos 6 y 7 son *(propuesta)*: el usuario no los respondió uno
  por uno. El punto 5, en lo que esperaba un servicio de firma, lo reemplaza el
  [ADR-0183](0183-windows-va-sin-firmar-y-los-canales-de-flutter-los-crea-su-application.md), y el
  punto 2, el [ADR-0184](0184-la-uri-de-retorno-es-https-donde-se-puede-y-cada-pieza-elige-sus-plataformas.md)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/README.md`](../plataformas/README.md), «Alcance»;
  [`plataformas/transversal.md`](../plataformas/transversal.md), «Distribución»;
  [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Versiones»;
  [`plataformas/flutter.md`](../plataformas/flutter.md), [`plataformas/flet.md`](../plataformas/flet.md)
  y [`plataformas/qt.md`](../plataformas/qt.md), «Entrega»; `plantilla/.github/workflows/`,
  `plantilla/scripts/apple.py`, `plantilla/infra/install.py` y `plantilla/flet/pyproject.toml`

## Contexto

`transversal.md` decía que ninguna app se publica en macOS ni en iOS hasta que haya cuenta de
Apple Developer ([ADR-0174](0174-flet-fija-sus-transitivas-con-pip-constraint-y-construye-sin-flet-build-action.md),
punto 5), y el DMG de Flet esperaba la cuenta ([ADR-0141](0141-la-app-de-flet-genera-sus-modelos-y-se-entrega-con-los-scripts-de-flet.md),
punto 3). Tener la cuenta es una condición de cada producto, no de Canone: un producto puede
tenerla y otro no.

Leído en Flet 1.1.2, *Packaging app for macOS* y *Packaging app for iOS*: `flet build macos
--macos-distribution developer-id` firma, notariza y grapa la app; recomienda un DMG y una llave
de la API de App Store Connect, y sube el `.ipa` con `xcrun altool --upload-package`.

## Decisión

1. **Una página escribe cómo se construye, se firma y se publica en cada plataforma como si el
   producto tuviera las cuentas y los certificados que pide.** En qué plataformas construye y
   publica lo elige cada repositorio.
2. **Cada repositorio declara `RELEASE_ANDROID`, `RELEASE_IOS`, `RELEASE_LINUX`, `RELEASE_MACOS`
   y `RELEASE_WINDOWS`** en sus variables de GitHub Actions, con `true` o `false`, y CI falla si
   falta una o vale otra cosa. Consola las fija.
3. **Una app de iOS va a la App Store**, firmada con el certificado Apple Distribution y el perfil
   de App Store, y el CI la deja en TestFlight.
4. **macOS recibe un DMG**: la app firmada con Developer ID y el runtime endurecido, y el DMG
   firmado, notarizado y con el ticket grapado. También en Qt, con el `.app` de `pyside6-deploy`.
5. **Windows se elige igual que los demás sistemas**, y sus instaladores siguen sin firmar hasta
   que se elija el servicio de firma.
6. *(propuesta)* `scripts/apple.py` instala en el runner el certificado y el perfil desde los
   secretos, arma y notariza el DMG y sube el `.ipa`, sin acciones de GitHub nuevas.
7. *(propuesta)* En Flutter, el target `Runner` firma Release a mano, y `flutter build ipa` exporta
   con `ios/ExportOptions.plist`.

Reemplaza el punto 5 del ADR-0174 y, del punto 3 del ADR-0141, la espera a la cuenta.

## Consecuencias

- Ningún job de Apple corrió: el primer tag que los active es la prueba. Lo que falta comprobar y
  decidir está en [pendientes/firma-y-publicacion.md](../pendientes/firma-y-publicacion.md).
- `install.py --desktop macos` espera `desktop-macos.dmg`.
- Un repositorio sin las cinco variables falla en CI desde su próximo commit.

## Descartado

- **Una variable que falta vale `false`:** un repositorio mal configurado dejaría de publicar en
  una plataforma sin que nadie lo note.
- **Un zip en macOS:** no se puede firmar ni grapar, y el DMG es lo que recomienda Flet.
- **Esperar a la cuenta para escribir las reglas:** ataba Canone a la situación de un producto.
