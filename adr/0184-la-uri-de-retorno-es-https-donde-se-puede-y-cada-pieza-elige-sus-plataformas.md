# ADR-0184 · La URI de retorno es `https` donde se puede, y cada pieza elige sus plataformas

- **Estado:** Aceptada. El usuario pidió aplicar lo recomendado para el login de Flutter en iOS, si
  no era un parche, y para lo demás que quedaba abierto (2026-11-18). El punto 1, en las apps de escritorio, lo reemplaza el [ADR-0194](0194-el-sms-sirve-para-entrar-y-el-escritorio-y-la-web-de-flutter-y-flet-tienen-passkey.md)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/autenticacion.md`](../plataformas/autenticacion.md), «Código de
  autorización»; [`plataformas/flutter.md`](../plataformas/flutter.md);
  [`plataformas/transversal.md`](../plataformas/transversal.md), «Distribución»;
  `scripts/verificar.py` y `plantilla/.github/workflows/`

## Contexto

- El [ADR-0175](0175-qt-y-flet-entran-con-pantallas-propias-sin-salir-al-navegador.md) dejó la URI
  de retorno de toda app en `https`. El RFC 8252 pide la URI `https` donde se pueda (§7.2) y admite
  un esquema propio con el dominio al revés (§7.1), cuya intercepción cubre PKCE (§8.1). La regla
  de Canone endurecía ese «donde se pueda» sin mirar cada sistema.
- Leído en AppAuth-iOS 3.0.0, que usa flutter_appauth 13.0.0: abre `ASWebAuthenticationSession`
  con `callbackURLScheme` igual al esquema de la URI de retorno, y con `https` la sesión no recibe
  el retorno. Usar el retorno `https` que Apple agregó en iOS 17.4 es el pedido abierto #847 de
  AppAuth-iOS. No se probó en un iPhone.
- El [ADR-0180](0180-cada-plataforma-se-escribe-como-si-hubiera-cuenta-y-cada-repositorio-elige-donde-publica.md)
  puso una variable por plataforma. Con dos apps, `RELEASE_IOS` valía para las dos, y un
  repositorio sin escritorio tenía que declarar tres variables que no usa.
- Comprobado con un repositorio de prueba con una app de Flutter: `verificar.py --variables` falla
  con la variable de iOS que falta y con una que no es de ninguna pieza.

## Decisión

1. **Una app recibe el retorno en una URI `https` que reclama, donde su sistema y su biblioteca
   lo permiten, y si no, en un esquema propio con su dominio al revés.**
2. **La app de Flutter recibe el retorno en `https` en Android y en un esquema propio en iOS.**
3. **Cada pieza declara una variable por plataforma, `RELEASE_<PIEZA>_<PLATAFORMA>`.** Una app en
   Flutter o en Flet lleva `ANDROID` e `IOS`; una en Kotlin, `ANDROID`, y `desktop/`, `LINUX`,
   `MACOS` y `WINDOWS`. `verificar.py --variables`, en CI, falla si falta una, si vale otra cosa o
   si no es de ninguna pieza.
4. **El perfil de App Store de cada app va en un secreto del repositorio.**
5. **Antes de la API 33, la app de Android sigue el idioma del sistema.**

Reemplaza el punto 2 del ADR-0175 y el punto 2 del ADR-0180.

## Consecuencias

- El servidor registra para la app de iOS su propia URI de retorno.
- Regenerar el perfil de App Store obliga a actualizar su secreto.

## Descartado

- **Un plugin propio con el retorno `https` de iOS 17.4:** código nativo propio que mantener, y
  pide iOS 17.4 como mínimo, para una garantía que PKCE ya da.
- **Esperar al #847 de AppAuth-iOS:** el login de iOS no funciona mientras tanto.
- **Bajar el perfil en cada corrida con `apple-actions/download-provisioning-profiles`:** es una
  acción más en el stack, para un perfil que cambia poco.
- **Un selector de idioma dentro de la app:** repite lo que el sistema ya ofrece desde la API 33.
