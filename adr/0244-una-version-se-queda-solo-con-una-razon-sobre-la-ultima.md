# ADR-0244 · Una versión se queda solo con una razón sobre la última, y el stack nombra los extras

- **Estado:** Aceptada. El usuario pidió el 2026-11-25 reevaluar cada razón por la que una versión no
  sube, según describa o no las versiones actuales, y registrarla, y confirmó el punto
  10, que se eligió al implementar
- **Fecha:** 2026-11-25
- **Alcance:** [`stack.md`](../stack.md), [`plataformas/README.md`](../plataformas/README.md),
  [`flutter.md`](../plataformas/flutter.md), [`flet.md`](../plataformas/flet.md),
  [`sveltekit.md`](../plataformas/sveltekit.md), [`python.md`](../plataformas/python.md) y
  `scripts/verificar.py`

## Contexto

Las razones por las que una versión no subía estaban en las sesiones de trabajo o en ADR sobre
versiones anteriores:

- **Flutter 3.47.9.** El 2026-11-12 se quedó porque «publicar una versión no la adopta», y el
  2026-11-05, porque Flet pide su propia serie. Ninguna describe la 3.50.1.
- **Extras.** El [ADR-0169](0169-el-stack-suma-los-paquetes-que-sus-paginas-ya-pedian-y-el-servidor-declara-uvicorn.md)
  los descartó porque «no lo pide ninguna regla». El stack ya nombraba los de stripe y
  datamodel-code-generator.
- **sudo, unattended-upgrades y ca-certificates.** El
  [ADR-0131](0131-los-paquetes-de-la-maquina-los-instala-packages-py.md) dice quién los instala, y no
  habla de versiones.
- **Inno Setup.** El 2026-11-13 se eligió porque el runner de Windows lo trae. La versión no se
  escribió.
- **Enlaces con versión.** El 2026-11-23 quedaron en la versión anterior, donde se comprobó cada
  hecho.
- **`compileSdk` 36 del plugin de passkeys.** Salió de la plantilla de `flutter create`, sin una
  razón.
- **`python.md`.** El 2026-11-19 pasó a repetir la regla de «Qué entra», que el
  [ADR-0161](0161-cada-regla-queda-en-una-sola-pagina-y-plugins-deja-de-ser-una-carpeta-de-primer-nivel.md)
  define una sola vez.

Comprobado el 2026-11-25:

- **Flutter 3.50.1** con los paquetes de `stack.md`, el JDK 25.0.5, Gradle 9.9.2, AGP 9.5.2 y Kotlin
  2.4.21: resuelve, genera, pasa las pruebas y construye el APK de depuración con el plugin
  `passkey`. `dart analyze --fatal-infos` falla con `deprecated_member_use` en el import de
  `package:flutter/material.dart`. Con material_ui 1.11.1, esa falla desaparece.
- **Sin su extra:** Uvicorn 0.54.0 no tiene WebSocket y no avisa (`AutoWebSocketsProtocol` es `None`);
  SQLAlchemy 2.1.9 falla sin greenlet; pwdlib 0.4.2 falla sin argon2.
- **npm:** pnpm 12.23.0 agrega `@types/node` 26.6.10, con dos horas de publicada, a
  `minimumReleaseAgeExclude` de `pnpm-workspace.yaml`.
- **Enlaces:** de los archivos que cambian entre la versión anterior y la nueva de Flet, stripe,
  swagger_parser, maplibre_gl y Gradle, ninguno cambia lo que afirma su página. `stripe[async]` 17.1.0
  sigue instalando httpx.

Leído: `flet build` 1.1.3 usa AGP 8.13.2, el mismo con que sms_autofill no construyó en la API 37
([ADR-0193](0193-flet-lee-el-codigo-por-sms-con-una-extension-de-la-plantilla.md)). `setup-java` v6
toma la compilación más nueva que cumple la versión pedida, y `25.0.5` da la 25.0.5.1. El runner de
Windows trae Inno Setup 6.7.1. flet-secure-storage 1.1.3 usa flutter_secure_storage 10.3.1.

## Decisión

1. **Una versión que no sube lleva su razón en la página de su plataforma, y la razón vale solo si se
   comprobó con la última versión.** Va en «Versiones» de `stack.md` y en «Revisión de stack.md».
2. **Una versión nueva se adopta a mano, en una revisión de `stack.md`.** Lo decía solo el
   [ADR-0118](0118-cada-pagina-fija-la-version-de-sus-tecnologias-y-la-plantilla-y-las-fuentes-la-siguen.md).
3. **Flutter se queda en la 3.47.9:** la 3.50 obliga a pasar a material_ui, que no está en el stack.
4. **El stack nombra los extras que una pieza declara**, y `verificar.py` los exige. Reemplaza lo
   descartado sobre los extras en el ADR-0169.
5. **Una versión de npm entra cuando lleva más de un día publicada.** Por eso se quedan
   `@types/node` 26.6.6, `@axe-core/playwright` 4.14.0 y `@stripe/stripe-js` 10.3.0.
6. **Entran sudo, unattended-upgrades y ca-certificates**, y la fila de systemd nombra
   systemd-timesyncd y systemd-journal-remote: son lo que instala `packages.py`.
7. **Entra Inno Setup 6**, con la nota de que lo fija el runner.
8. **Un enlace pasa a la versión nueva cuando lo que afirma se comprueba en ella**, y si no, conserva
   la anterior.
9. **El plugin `passkey` se queda en `compileSdk` 36**, con su razón en `flet.md`.
10. **`python.md` escribe solo la herramienta**, deptry, como las páginas de los demás
    clientes.

El JDK se queda en 25.0.5, `json_serializable` sin «Para» y los enlaces de flutter_secure_storage
10.3.1 en `flet.md`: sus razones valen para las versiones actuales.

## Consecuencias

- Pasar a Flutter 3.50 pide decidir material_ui y cupertino_ui, y revisar «Idiomas» de `flutter.md`,
  porque los delegados de las traducciones cambian de paquete.
- Un repositorio sin el extra falla en `verificar.py`.

## Descartado

- **Subir Flutter sin material_ui, apagando `deprecated_member_use`:** esconde la única forma de
  Material que sigue.
- **Nombrar el extra solo en la página:** lo que declara el manifiesto se lee en el stack.
