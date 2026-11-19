# ADR-0185 · Una cuenta entra con passkey o con contraseña, y cada repositorio elige cuáles ofrece

- **Estado:** Aceptada. El usuario pidió que Canone defina los métodos disponibles en cada
  plataforma y no cuál usa cada app, confirmó que el código por SMS deja de servir para entrar
  y pidió tratar las cuentas de administración como las demás (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/autenticacion.md`](../plataformas/autenticacion.md), «Código de
  autorización», «Código por SMS», «Cuentas», «Passkeys», «Recuperación» y «Sesión»;
  [`plataformas/flet.md`](../plataformas/flet.md), «Código de autorización»

## Contexto

- `autenticacion.md` decía qué método usaba cada cuenta y cada app: una cuenta de administración
  entraba solo con passkeys que verifican al usuario, la recuperaba otro administrador y su sesión
  vencía antes, y una app de escritorio entraba solo con contraseña o con código por SMS.
- NIST SP 800-63B-4 §3.2.9 clasifica el SMS como autenticador restringido: quien lo acepta para
  entrar debe ofrecer otro que no lo sea y avisar del riesgo. Un código para verificar una dirección
  o recuperar la cuenta no es autenticación (§3.1.3.1).
- La passkey se construye una vez en el servidor y en cada plataforma, y no cuesta nada al entrar.
  Cada inicio de sesión con SMS es un mensaje pagado, y el robo de la línea da la cuenta.
- Comprobado el 2026-11-18 en un Galaxy S10e con Android 12 y Chrome, con Flet 1.1.2: una app abre
  una página en `LaunchMode.IN_APP_BROWSER_VIEW`, la página manda un `POST` que responde 303 a una
  URI `https` que la app declara con `autoVerify`, y la app recibe la ruta con `code` y `state` en
  `on_route_change`. El dominio se aprobó con `pm set-app-links`, sin `assetlinks.json`, y la página
  estaba en otro origen que la URI de retorno.
- Comprobado el 2026-11-18 en el mismo teléfono, con un túnel temporal con HTTPS: con la página, la
  redirección y la URI de retorno en el mismo host, y el dominio verificado por Android con
  `assetlinks.json`, la app también recibe `code` y `state`.

## Decisión

1. **Una cuenta entra con una contraseña o con una passkey.** El código por SMS y el código por
   correo solo verifican el teléfono o la dirección, y recuperan la cuenta.
2. **Canone dice qué métodos tiene cada plataforma, y no cuál usa cada cuenta ni cada app.** El
   servidor acepta los dos en toda cuenta, y cada repositorio elige cuáles ofrece cada pieza.
3. **Una cuenta de administración sigue las mismas reglas que las demás.** Salen que entra solo
   con passkeys, que su passkey exige verificar al usuario, que la recupera otro administrador y que
   su sesión vence a las 24 horas o tras 1 hora sin uso.
4. **La web y las apps de Android, de Flutter y de Flet en el teléfono tienen passkey y contraseña;
   una app de escritorio, de Flet o de Qt, tiene contraseña.**
5. **Un código vale una sola vez** pasa a «Recuperación», como convención propia: su origen era la
   sección de NIST del SMS como autenticador.
6. **La app de Flet en Android abre la petición en `LaunchMode.IN_APP_BROWSER_VIEW` y declara la URI
   de retorno en `[[tool.flet.android.activity.intent_filter]]`, con `autoVerify`.**

Reemplaza el punto 1 del [ADR-0067](0067-la-autenticacion-sigue-a-nist-y-el-bloqueo-cuenta-fallos-consecutivos-con-esperas.md)
en las cuentas de administración, los puntos 11 y 12 del
[ADR-0133](0133-la-autenticacion-tiene-su-pagina-y-el-servidor-comprueba-aparte-lo-que-sus-bibliotecas-no-miran.md)
en el código por SMS, y el punto 1 del
[ADR-0175](0175-qt-y-flet-entran-con-pantallas-propias-sin-salir-al-navegador.md).

## Consecuencias

- Sale la obligación de avisar del riesgo del SMS y de ofrecer otro autenticador al registrar un
  teléfono, y la de contar los fallos del código entre los del teléfono.
- Una cuenta de administración entra, se recupera y mantiene su sesión como cualquier otra.
- Quien cambia de teléfono sin la passkey sincronizada espera las 24 horas de la recuperación de una
  cuenta con passkey.
- Una cuenta creada en el teléfono sin contraseña no entra en una app de escritorio hasta que
  agrega una.

## Descartado

- **El código por SMS como método para entrar:** obliga a las salvedades de un autenticador
  restringido, cuesta un mensaje por inicio de sesión y deja la cuenta a quien roba la línea.
- **El correo como método para entrar:** NIST SP 800-63B-4 §3.1.3.1 lo prohíbe.
