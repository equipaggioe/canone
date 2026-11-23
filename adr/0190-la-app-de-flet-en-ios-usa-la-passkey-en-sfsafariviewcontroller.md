# ADR-0190 · La app de Flet en iOS usa la passkey en `SFSafariViewController` y recibe el retorno en un esquema propio

- **Estado:** Reemplazada por [ADR-0222](0222-las-apps-de-flutter-y-flet-usan-la-passkey-con-un-plugin-de-la-plantilla.md)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/flet.md`](../plataformas/flet.md), «Código de autorización», y
  [`plataformas/autenticacion.md`](../plataformas/autenticacion.md), «Cuentas»

## Contexto

- Leído en url_launcher_ios 6.4.2, que usa Flet 1.1.2: `LaunchMode.IN_APP_BROWSER_VIEW` abre un
  `SFSafariViewController`, y `close_in_app_web_view()` lo cierra.
- WebKit: WebAuthn con Face ID y Touch ID funciona en Safari, `SFSafariViewController` y
  `ASWebAuthenticationSession`. El RFC 8252, apéndice B.1, admite `SFSafariViewController` como
  pestaña del navegador dentro de la app, con retorno a un esquema propio o a un Universal Link.
- Apple: un Universal Link del mismo dominio que la página que se navega se abre en Safari, y no en
  la app.
- No se probó en un iPhone.

## Decisión

1. **La app de Flet abre la petición de autorización en `IN_APP_BROWSER_VIEW` también en iOS**, y
   usa ahí la passkey.
2. **En iOS, el retorno llega a un esquema propio con el dominio al revés**, en
   `[tool.flet.ios.deep_linking]`.
3. **Al recibir el retorno, la app cierra la pestaña con `close_in_app_web_view()`.**
4. La tabla de `autenticacion.md` da passkey a la app de Flet en el teléfono, en Android y en iOS.

## Consecuencias

- El servidor registra para la app de Flet en iOS su propia URI de retorno.
- Si la prueba en un iPhone falla, se cambia la regla.

## Descartado

- **Un Universal Link en iOS:** la página de autorización está en el mismo dominio, y Safari lo abre
  sin pasar a la app.
- **Dejar a Flet en iOS sin passkey hasta probarlo:** la documentación ya dice que funciona.
