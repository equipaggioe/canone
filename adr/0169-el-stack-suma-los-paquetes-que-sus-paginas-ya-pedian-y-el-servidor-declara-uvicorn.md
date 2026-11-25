# ADR-0169 · El stack suma los paquetes que sus páginas ya pedían, y el servidor declara Uvicorn sin el extra `standard`

- **Estado:** Aceptada. El usuario pidió implementar las recomendaciones de la revisión de
  `stack.md` (2026-11-16) y, después, cerrar lo abierto con lo recomendado. Los puntos marcados
  *(propuesta)* se definieron al implementar. El punto 8 lo reemplaza el
  [ADR-0170](0170-cada-app-guarda-su-numero-de-build-en-su-manifiesto.md), y lo descartado sobre
  los extras, el [ADR-0244](0244-una-version-se-queda-solo-con-una-razon-sobre-la-ultima.md)
- **Fecha:** 2026-11-16
- **Alcance:** [`stack.md`](../stack.md), `plataformas/`, `plantilla/` y `scripts/verificar.py`

## Contexto

Revisión de `stack.md` contra las páginas de `plataformas/`: se buscó lo que una página pide y el
stack no nombra, y lo que el stack nombra y ningún manifiesto declara.

Comprobado el 2026-11-16:

- **El job `server` de la plantilla, en Debian 13 con PostgreSQL 17.12, Valkey 8.1.1 y uv 0.13.7.**
  Con `fastapi[standard]`, pip-audit falla por dnspython 2.9.0 (CVE-2026-128089), que llega por
  email-validator, del extra. Con `fastapi`, `uvicorn[standard]` y el bloqueo nuevo, pip-audit, ruff,
  Pyrefly, deptry y las 95 pruebas pasan, y `.venv/bin/uvicorn` arranca la app con las opciones de
  su unidad. El bloqueo pierde 25 paquetes, entre ellos fastapi-cli, fastapi-cloud-cli, sentry-sdk,
  httpx2, Jinja2 y el exportador OTLP de OpenTelemetry.
- **FastAPI 0.162.0 sin python-multipart** no declara una ruta con `UploadFile`: falla al
  importarla y pide instalarlo. Con python-multipart 0.0.34, la declara.
- **`gettext` de Python 3.13 no lee un `.po`:** `gettext.translation` falla con «No translation
  file found». Después de `pybabel compile -d src/locales -D pieza`, de Babel 2.18.0, traduce.
- **Flutter 3.47.5, la instalada, y no la 3.47.9 del stack:** una app con flutter_localizations,
  intl 0.20.3, uuid 4.6.0 y package_info_plus 10.2.2 resuelve sus dependencias; `gen-l10n` genera
  `lib/l10n/app_localizations*.dart` desde `app_es.arb`, y lo generado importa `package:intl` y pasa
  `dart format` con `page_width: 99` y `dart analyze --fatal-infos` con el `analysis_options.yaml`
  de la plantilla.

- **`alembic check` con PostGIS:** en la réplica del job `server`, con la extensión creada y sin
  geoalchemy2, falla porque propone borrar `spatial_ref_sys`. Sin la extensión pasa, y con la
  extensión y geoalchemy2 0.21.0 declarado, también: `env.py` solo salta las tablas de PostGIS
  si geoalchemy2 está instalado.

Leído:

- En flet-cli 1.1.2, `flet build` excluye del paquete solo lo oculto del primer nivel, los
  entornos virtuales y los `__pycache__`, y no limpia la app por defecto: los `.mo` de
  `src/locales/` entran.
- firebase-admin 7.8.0 conserva `send_each_async` y sigue pidiendo `httpx[http2]==0.28.1`.
- El `pubspec.yaml` de flutter_localizations en Flutter 3.47.9 pide `intl: ^0.20.3`.
- firebase-admin pide `httpx[http2]==0.28.1`.
- stripe 17.0.0 pide requests, y su extra `async`, httpx; los métodos `_async` van por httpx, y
  `construct_event` verifica la firma en tiempo constante, con 300 segundos de tolerancia.
- `@stripe/stripe-js` 10.3.0 carga Stripe.js desde `js.stripe.com` al importarse, y
  `@stripe/stripe-js/pure`, al llamar a `loadStripe`.
- La última versión de cada paquete que entra, en PyPI, pub.dev, npm y Maven Central.

## Decisión

1. **El servidor declara `fastapi` sin el extra `standard`, y `uvicorn[standard]`.** La unidad
   corre `uvicorn`, y el stack fija su versión: sin declararlo, ningún manifiesto la seguía.
2. **Entra python-multipart en el bloque de FastAPI.** Lo declara el servidor que recibe un
   archivo o un formulario. La plantilla no lo declara: no tiene ninguno.
3. **Con Stripe, el servidor usa `stripe` con el extra `async`, y la web, `@stripe/stripe-js`.**
   Flutter y Android ya tenían su SDK.
4. *(propuesta)* **La web importa `loadStripe` de `@stripe/stripe-js/pure`**, y el formulario
   incrustado es el Payment Element.
5. **Flutter suma flutter_localizations e intl**, para los textos de la app.
6. *(propuesta)* **Los textos de Flutter van en ARB en `lib/l10n/`, con `app_es.arb` de plantilla,
   y lo que genera `gen-l10n` no se versiona.**
7. **Flutter suma uuid**, para el id que el cliente genera al crear un recurso, **y
   package_info_plus**, para la versión del `User-Agent`.
8. **Android suma `kotlinx-coroutines-android`:** el código lo importa.
9. **Flet suma Babel, en el grupo `dev`, para compilar el `.mo`.** Cierra lo que el
   [ADR-0166](0166-flet-escribe-solo-lo-que-elige.md) dejó sin elegir.
10. *(propuesta)* **El CI y el `release.yml` de la plantilla compilan el `.mo` de Flet** antes de
    `flet test` y de `flet build`.
11. **El servidor llama a otro servicio con un solo `httpx.AsyncClient`.** firebase-admin ya obliga
    a instalar httpx 0.28.1, y es el cliente de las pruebas y de Flet: httpx2 sería un tercer
    cliente HTTP en el servidor.
12. **firebase-admin pasa a la 7.8.0**, la última.
13. **El CI de la plantilla crea la extensión PostGIS en un paso aparte**, solo para el servidor
    que guarda geografía y declara geoalchemy2.

## Consecuencias

- Un servidor que recibe archivos o formularios declara python-multipart, que antes llegaba con el
  extra.
- `fastapi dev` y `fastapi run` dejan de estar instalados. La unidad ya corría `uvicorn`.
- Un servidor que guarda geografía conserva el paso de PostGIS de su `ci.yml`, y los demás lo
  borran.
- Sin confirmar: los pasos nuevos de los workflows, que no corrieron en GitHub Actions, y los
  paquetes de Flutter con la 3.47.9.
- Sin confirmar: que `buildHealth` falle por `kotlinx-coroutines-android` sin declarar. La regla
  sale de «Qué entra» de `stack.md`.
- Quedan sin actualizar dieciséis paquetes con una versión más nueva en su registro: cada uno pide
  volver a comprobar los enlaces con versión de las páginas y volver a descargar sus fuentes.

## Descartado

- **JDK 21 en Android:** el JDK con el que corre Gradle solo construye, y no corre en el servidor.
- **Mover httpx y Pydantic fuera del bloque de Python:** ninguna regla de `stack.md` dice dónde va
  un paquete que comparten varias plataformas, y `verificar.py` solo revisa el que una pieza
  declara.
- **Nombrar en el stack el extra de cada paquete:** no lo pide ninguna regla.
- **web_socket_channel en Flutter:** `dart:io` ya trae `WebSocket`.
- **Coil, un paquete de iconos y WebRTC en los clientes:** ninguna página escribe hoy esas
  funciones.
- **httpx2 como cliente HTTP saliente del servidor:** es de Pydantic y se presenta como la
  siguiente generación de httpx, pero firebase-admin fija httpx 0.28.1, y el servidor tendría los
  dos.
- **Saltar `spatial_ref_sys` en `env.py` aunque falte geoalchemy2:** un servidor sin geografía no
  crea la extensión.
