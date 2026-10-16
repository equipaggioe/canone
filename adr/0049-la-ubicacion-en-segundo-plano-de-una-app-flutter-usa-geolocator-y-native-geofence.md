# ADR-0049 · La ubicación en segundo plano de una app Flutter usa geolocator con servicio en primer plano y native_geofence

- **Estado:** Propuesta
- **Fecha:** 2026-10-12
- **Alcance:** una sección nueva «Ubicación» de [`plataformas/flutter.md`](../plataformas/flutter.md)

## Contexto

Una app que sigue al usuario con la app cerrada (cadenza: desde que pide la cita hasta que sale de la inspección) necesita posiciones en segundo plano y saber cuándo cruza un área. Se consideró `flutter_background_geolocation`, que exige una licencia pagada para publicar en Android. vettore ya lo resuelve sin ella, y funciona con la app cerrada ([ADR-0011 de vettore](../../vettore/docs/adr/0011-capacidades-en-segundo-plano.md), [vettore mobile 14](../../vettore/docs/arquitectura/mobile/14_ubicacion.md)). Esta propuesta recoge lo que vettore muestra.

## Decisión

1. **Posiciones continuas: `geolocator`**, sostenido en Android por su servicio en primer plano, con su notificación persistente. El manifiesto declara `ACCESS_FINE_LOCATION`, `ACCESS_BACKGROUND_LOCATION`, `FOREGROUND_SERVICE` y `FOREGROUND_SERVICE_LOCATION`.
2. **El cruce de un área lo detecta el sistema con `native_geofence`**, también con la app cerrada:
   1. El receptor de transiciones, el de reinicio (`BOOT_COMPLETED`) y el servicio del plugin se declaran en el manifiesto de la app. El plugin no los declara: sin el receptor, `addGeofences` responde que registró la región, pero el cruce nunca se entrega, y no hay error.
   2. La región se registra siempre con `{enter, exit}`, y el sentido pedido se filtra en el callback. Android solo actualiza su estado «dentro o fuera» con las transiciones suscritas: suscrita solo a `exit`, avisa el primer cruce y nunca más.
   3. El callback corre en un isolate de segundo plano y hace el trabajo ahí mismo (guardar y enviar el cruce), con `WAKE_LOCK`, sin esperar a que la app vuelva a primer plano.
   4. Un polígono se vigila con dos círculos del sistema, el envolvente y el inscrito. Entre los dos, la app muestrea la posición y guarda de qué lado quedó, porque el cruce siguiente se afirma contra el lado anterior.
3. **Un flujo de posiciones que nace en un isolate de segundo plano** (por ejemplo, desde un push) vive en un servicio nativo con su propio `FlutterEngine`, publicado como plugin local del `pubspec`. Si no, muere con el isolate que lo arrancó. Va como plugin porque solo los plugins se registran en todos los engines.
4. **Cadencia:** un punto por desplazamiento (20 m) con un piso de 5 s entre puntos, más un latido cada 60 s que repite la última posición. El latido distingue «quieto» de «sin señal o sin app». Los 20 m están a prueba: quedan debajo de la precisión del GPS en la ciudad.
5. **iOS:** `UIBackgroundModes` con `location`, más `NSLocationWhenInUseUsageDescription` y `NSLocationAlwaysAndWhenInUseUsageDescription`. Un flujo no se puede arrancar desde segundo plano: la orden queda pendiente hasta que la app vuelve a primer plano.
6. **Lo que el segundo plano necesita leer del almacenamiento seguro** se guarda con `KeychainAccessibility.first_unlock_this_device`. Con `when_unlocked`, no se puede leer con el teléfono bloqueado.

## Consecuencias

- No hace falta una biblioteca de pago.
- La notificación persistente es obligatoria en Android mientras se envían posiciones.
- La app pide el permiso de ubicación «siempre», con lo que eso exige en cada tienda.
- El plugin local del punto 3 es código Kotlin propio que hay que mantener, solo si hace falta arrancar el flujo desde segundo plano.
- La fuente de `geolocator` y la de `native_geofence` se copian a `fuentes/pub/`.

## Descartado

- **`flutter_background_geolocation`.** Exige licencia pagada para Android, y lo que agrega (detección de movimiento, geocercas) ya lo cubren el sistema y `geolocator`.
- **Muestrear por reloj.** Con el teléfono quieto produce puntos idénticos que hay que enviar, guardar y dibujar.
- **Registrar la geocerca solo con el sentido pedido.** Android deja de avisar después del primer cruce.
