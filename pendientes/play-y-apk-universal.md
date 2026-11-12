# La subida a Play y el APK universal

Tema pendiente: la convención está escrita y la plantilla la sigue, pero **nada corrió todavía
contra Google Play**.

## Estado (verificado 2026-11-12)

| Pieza | Estado |
| :--- | :--- |
| `transversal.md`, «Distribución»; «Entrega» de `flutter.md` y `android.md`; «Versiones» de `despliegue.md` | Escrito |
| `install.py --mobile <pieza>` agrega `<pieza>.apk` a lo que `deploy.py` publica | Hecho; `scripts/infra/deploy.sh` lo prueba con `mobile-customer`, sin correr todavía en `infra.yml` |
| `scripts/verificar.py`: `scripts/play.py` igual al de la plantilla | Hecho |
| `plantilla/scripts/play.py` | Escrito; `uv run --script` resuelve sus dependencias. **Nunca corrió contra Play** |
| Jobs `mobile` y `android` de `release.yml` | Escritos; **nunca corrieron** |

## Qué falta comprobar

- Que `play.py` sube un AAB a la pista interna y que Play genera el APK universal de esa versión
  sin pasarla a producción.
- Cuánto tarda Play en generarlo: `play.py` espera hasta 15 minutos.
- Que el APK universal se instala encima de la versión de la tienda, y al revés.
- Que `flutter build appbundle` lee `android/key.properties` con la ruta absoluta que escribe el
  job.

## Fuentes

- [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)
- [Download generated APKs](https://developers.google.com/android-publisher/download-apks)
- [Android developer verification](https://developer.android.com/developer-verification/guides)
