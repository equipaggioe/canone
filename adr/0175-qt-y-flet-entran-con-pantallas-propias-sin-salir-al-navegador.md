# ADR-0175 · Las apps de escritorio de Qt y de Flet entran con pantallas propias, sin salir al navegador

- **Estado:** Aceptada. El usuario eligió las pantallas propias para el escritorio de Qt y de Flet, y que la app móvil de Flet funcione como la de Flutter (2026-11-17). El punto 1 lo reemplaza el [ADR-0185](0185-una-cuenta-entra-con-passkey-o-contrasena-y-cada-repositorio-elige-cuales-ofrece.md), y el punto 2, el [ADR-0184](0184-la-uri-de-retorno-es-https-donde-se-puede-y-cada-pieza-elige-sus-plataformas.md)
- **Fecha:** 2026-11-17
- **Alcance:** [`plataformas/autenticacion.md`](../plataformas/autenticacion.md), «Código de
  autorización», y [`plataformas/qt.md`](../plataformas/qt.md)

## Contexto

`qt.md` decía desde el 2026-11-13 que la app entraba solo por el navegador del sistema, y el
[ADR-0165](0165-qt-escribe-solo-lo-que-elige-y-se-aplica.md) lo llevó a toda app de escritorio,
también a la de Flet. El usuario no recuerda haberlo decidido, y no le convence que ninguna de las
dos salga al navegador.

Comprobado en la distro WSL `Testing`, con PySide6 6.12.0 y `QT_QPA_PLATFORM=offscreen`: un
`QLineEdit` en `EchoMode.Password` acepta `paste()`, y una acción marcable al final lo pasa a
`EchoMode.Normal` y lo vuelve a `Password`.

## Decisión

1. **Una app de escritorio, de Flet o de Qt, entra con contraseña o con código por SMS, en
   pantallas propias**, y no usa passkeys: ni Flet ni Qt tienen una API oficial. La app móvil de
   Flet sigue la regla de las demás apps: sin API oficial, usa la passkey en el navegador del
   sistema, como la de Flutter.
2. **La URI de retorno de una app es una URI `https` que reclama la app.** Sale la de loopback, que
   solo usaba la app de escritorio de Qt.
3. **El campo de la contraseña de Qt es un `QLineEdit` en `EchoMode.Password`**, con una acción que
   lo muestra.

## Consecuencias

- La app de Qt hace sus pantallas de contraseña, de código por SMS y de recuperación, como las
  apps móviles.
- En escritorio no hay passkey.
- Cómo vuelve el código de autorización a la app móvil de Flet queda por comprobar, en
  [pendientes/flet-mapa-y-codigo-de-autorizacion.md](../pendientes/flet-mapa-y-codigo-de-autorizacion.md).

## Descartado

- **El navegador del sistema:** sale de la app para entrar.
- **Un web-view dentro de la app:** lo prohíbe RFC 8252 §8.12.
- **Vincular el equipo desde la app del teléfono:** pide otro dispositivo con sesión y endpoints
  nuevos. Queda para el producto que tenga equipos compartidos.
