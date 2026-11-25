# ADR-0241 · El plugin de passkeys pide macOS 13

- **Estado:** Aceptada
- **Fecha:** 2026-11-25
- **Alcance:** `flutter.md`, `flet.md` y `plantilla/packages/passkey/`

## Contexto

El [ADR-0222](0222-las-apps-de-flutter-y-flet-usan-la-passkey-con-un-plugin-de-la-plantilla.md) pide iOS
16, la versión de las passkeys que se sincronizan, y el plugin aceptaba macOS 12, la primera con la
API. Apple dice que las passkeys piden iOS 16, iPadOS 16, macOS Ventura o tvOS 16, o una versión
posterior ([guía del iPhone](https://support.apple.com/guide/iphone/passkeys-passwords-devices-iph82d6721b2/16.0/ios/16.0)). Ventura es macOS 13. Revisado el 2026-11-25.

## Decisión

1. El plugin pide macOS 13.

## Consecuencias

- Una app de macOS con passkeys pide macOS 13 o una versión mayor.

## Descartado

- **macOS 12.** Sus passkeys no se sincronizan: se pierden con la máquina.
