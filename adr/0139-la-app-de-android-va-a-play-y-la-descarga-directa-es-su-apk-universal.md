# ADR-0139 · La app de Android va a Play, y la descarga directa es el APK universal que Play genera

- **Estado:** Aceptada
- **Fecha:** 2026-11-12
- **Alcance:** «Distribución» de [`plataformas/transversal.md`](../plataformas/transversal.md),
  «Entrega» de [`plataformas/flutter.md`](../plataformas/flutter.md) y de
  [`plataformas/android.md`](../plataformas/android.md), «Versiones» de
  [`plataformas/despliegue.md`](../plataformas/despliegue.md), `release.yml`, `scripts/play.py`,
  `install.py` y `scripts/verificar.py`

## Contexto

Canone publicaba en el release los instaladores de `desktop/` y dejaba fuera los de `mobile/`. Un
producto puede ofrecer su app de Android en Google Play y también como descarga directa desde su
landing. Si cada vía lleva su propia firma, una app instalada por una no se actualiza por la otra,
y el SMS lleva un hash por firma (`autenticacion.md`, «Código por SMS»). Además, desde 2027 Google
pide que una app instalada fuera de Play esté registrada con su llave por un desarrollador
verificado, y una app que está en Play se registra desde Play Console.

## Decisión

1. Una app de Android se publica en Google Play con Play App Signing: Play genera y guarda la llave
   que firma la app, y cada versión llega firmada con la llave de subida.
2. La descarga directa es el APK universal que Play genera de la misma versión, con la misma firma
   que la tienda.
3. Flutter compila con `flutter build appbundle --release` y Kotlin con `./gradlew bundleRelease`,
   y los dos firman con la llave de subida que nombra `key.properties`, que git ignora.
4. El CI sube cada app de `mobile/` del tag a la pista interna de Play con `scripts/play.py`,
   canónico, y adjunta al release su APK universal como `<pieza>.apk`. `install.py --mobile
   <pieza>` hace que `deploy.py` lo publique en `/srv/<app>/downloads/`, como los de escritorio.
5. La versión pasa a producción en Play Console.

## Consecuencias

- La llave que firma la app no vive en ninguna máquina de quien despliega: perder la llave de
  subida se resuelve pidiéndole a Play que la reemplace.
- Una sola firma por app: un solo hash para el SMS, y la descarga directa actualiza lo instalado
  desde la tienda.
- Un repositorio con apps de Android necesita una cuenta de Play, una cuenta de servicio con acceso
  a la API de publicación y los secretos de la llave de subida en GitHub.
- La primera versión de cada app se sube a mano en Play Console: la API no crea la app.
- `release.yml` y `scripts/play.py` no corrieron nunca contra Play: queda en
  [pendientes/](../pendientes/play-y-apk-universal.md).

## Descartado

- **Firmar el APK directo con una llave propia en el CI.** La llave quedaría en un secreto de
  GitHub, que no se puede volver a leer, y su pérdida impediría actualizar las apps instaladas.
- **Subir a Play una llave propia y firmar con ella las dos vías.** Conserva la misma firma, pero
  devuelve a quien despliega la custodia de la llave que firma la app.
- **Meter los APK en el build de la landing.** Cada versión guardada en `releases/` cargaría los
  APK, y la landing no compilaría sin ellos.
