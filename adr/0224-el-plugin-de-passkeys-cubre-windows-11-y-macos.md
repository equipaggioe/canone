# ADR-0224 · El plugin de passkeys cubre Windows 11 y macOS, y el navegador queda para Linux y Qt

- **Estado:** Aceptada
- **Fecha:** 2026-11-23
- **Alcance:** `plataformas/autenticacion.md`, `flutter.md`, `flet.md`, `plantilla/packages/passkey/`
  y `scripts/verificar.py`

## Contexto

El usuario pidió que el plugin del
[ADR-0222](0222-las-apps-de-flutter-y-flet-usan-la-passkey-con-un-plugin-de-la-plantilla.md) cubra
también Windows y macOS si las passkeys funcionan en Windows 10 y 11. La documentación de
Microsoft confirma Windows 11: la gestión de passkeys llega en 22H2 con KB5030310, y el permiso de
privacidad en 24H2. De Windows 10 dice solo que las passkeys se usan en «todas las versiones
soportadas», y no da versión mínima de `WebAuthNAuthenticatorGetAssertion` ni de
`WebAuthNAuthenticatorMakeCredential`. Apple da macOS 12 para
`ASAuthorizationPlatformPublicKeyCredentialProvider` (revisado el 2026-11-23). El usuario pidió
extenderlo a Windows 11 y macOS.

En la máquina de trabajo no hay Visual Studio con C++ ni macOS: la parte de Windows y la de macOS no
se compilaron. La capa de Dart de Windows se probó con el canal simulado, en Windows.

El 2026-11-24, con Visual Studio Build Tools 2022 17.14, la parte de Windows compiló en una app de
prueba, en Windows 10 22H2. Ahí `webauthn.dll` da la versión 2 de su API y dice que hay un
autenticador del sistema con verificación del usuario. No se creó ni se usó una passkey.

## Decisión

1. El plugin `passkey` llama a la API de WebAuthn de Windows y a AuthenticationServices en macOS. La
   parte de Swift es la misma que la de iOS, en `darwin/`.
2. Una app de Flutter o de Flet en Windows o en macOS usa la passkey con el plugin, y una de Linux o
   de Qt, en el navegador.
3. En Windows, la app escribe el `clientDataJSON` con el origin `https://<dominio>`, y
   el plugin usa la primera versión de las estructuras de la API, que lee todo Windows que la tiene.
4. Una app de macOS declara `webcredentials:<dominio>`.

## Consecuencias

- El navegador queda para Linux, para Qt y para la web.
- Windows 10 queda sin confirmar: hay que probarlo en una máquina con Windows 10.
- La documentación de Microsoft no dice si Windows comprueba que la app pertenezca al dominio.

## Descartado

- **Dejar el escritorio con el navegador.** El usuario pidió la hoja del sistema donde exista.
