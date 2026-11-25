# ADR-0222 · Las apps de Flutter y de Flet usan la passkey en el teléfono con un plugin de la plantilla

- **Estado:** Aceptada
- **Fecha:** 2026-11-23
- **Alcance:** `plataformas/autenticacion.md`, `flutter.md`, `flet.md`, `stack.md`,
  `plantilla/packages/passkey/` y `scripts/verificar.py`

## Contexto

Con la regla del [ADR-0054](0054-las-passkeys-son-un-contrato-de-transversal-y-una-app-usa-la-api-de-su-sistema.md),
una app usaba la API de passkeys de su sistema solo si su framework la ofrecía de forma oficial.
Flutter y Flet no la ofrecen, así que en el teléfono abrían una pestaña del navegador, cargaban la
página de autorización y volvían con un código. Con Credential Manager, en cambio, la passkey se
elige en una hoja del sistema sobre la app, sin navegador.

En pub.dev no hay un paquete de passkeys de Google ni del equipo de Flutter (revisado el
2026-11-23). El más usado, `passkeys` de Corbado, no dice en su README que use Credential Manager ni
AuthenticationServices. El usuario pidió construir uno propio, embebido en cada app.

Se compiló el plugin en Android, en una app de prueba con Flutter 3.47.5 y `androidx.credentials`
1.6.0. La parte de iOS no se compiló: no hay macOS ni Xcode en la máquina de trabajo. Ninguna parte
se probó en un teléfono.

## Decisión

1. La plantilla trae en `packages/passkey/` el plugin `passkey` de Flutter, que llama a Credential
   Manager en Android y a AuthenticationServices en iOS, y la extensión `flet_passkey` de Flet, que
   lo envuelve. Se copian sin editar, y `verificar.py` compara la copia.
2. Una app de Flutter o de Flet usa la passkey en el teléfono con ese plugin, y no hace el código
   de autorización. Una app de escritorio sigue usando el navegador del sistema. Reemplaza el punto
   4 del ADR-0054 en el teléfono, el ADR-0190 entero, el punto 2 del
   [ADR-0184](0184-la-uri-de-retorno-es-https-donde-se-puede-y-cada-pieza-elige-sus-plataformas.md)
   y, del [ADR-0133](0133-la-autenticacion-tiene-su-pagina-y-el-servidor-comprueba-aparte-lo-que-sus-bibliotecas-no-miran.md),
   el flutter_appauth del punto 10.
3. El plugin recibe las opciones de WebAuthn en JSON y devuelve la respuesta en JSON, la misma que
   da el navegador, y el servidor la verifica como cualquier otra.
4. Una app de iOS declara `webcredentials:<dominio>`, y la landing sirve
   `apple-app-site-association` con el app ID de cada app de iOS.
5. El plugin pide `minSdk` 28, y en iOS, la versión 16, la de las passkeys que se
   sincronizan.

## Consecuencias

- En el teléfono, entrar con passkey es una hoja del sistema, sin pestaña ni página.
- Salen flutter_appauth, la URI de retorno de las apps del teléfono y la pestaña del navegador de
  Flet.
- El plugin es código propio en Kotlin y Swift que hay que mantener con Credential Manager y
  AuthenticationServices.
- Falta probarlo en un teléfono Android y en un iPhone, con el dominio sirviendo `assetlinks.json`
  y `apple-app-site-association`.

## Descartado

- **`passkeys` de Corbado.** No está claro que use las APIs nativas, y es un paquete de un tercero
  sobre algo que toca la autenticación.
- **Seguir con la pestaña del navegador.** Saca al usuario de la app para algo que el sistema
  resuelve en una hoja sobre ella.
