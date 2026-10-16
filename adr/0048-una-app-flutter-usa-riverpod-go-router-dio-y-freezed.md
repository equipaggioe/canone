# ADR-0048 · Una app Flutter usa Riverpod, go_router, Dio y Freezed

- **Estado:** Propuesta
- **Fecha:** 2026-10-12
- **Alcance:** las secciones «Arquitectura» y «Estado» de [`plataformas/flutter.md`](../plataformas/flutter.md)

## Contexto

[`flutter.md`](../plataformas/flutter.md) fija `provider` con `ChangeNotifier` para el estado y
`package:http` para la red. Al construir la app de usuario de cadenza se eligió otro stack, por
mérito técnico, para una app que lee todo del API, se refresca sola, renueva la sesión ante un 401 y
después envía su posición en segundo plano.

## Decisión

1. **Estado e inyección de dependencias: Riverpod 3 con `riverpod_generator`.** Un proveedor por
   recurso del API; la pantalla lee un `AsyncValue` (carga, error y datos). Refrescar es invalidar el
   proveedor. Las pruebas reemplazan el repositorio con un *override* del `ProviderScope`. No se
   suma get_it ni injectable: Riverpod ya inyecta dependencias.
2. **Navegación: `go_router` con `go_router_builder`.** Las rutas son tipadas y la redirección por
   sesión vive en un solo `redirect`.
3. **Red: Dio**, dentro del único servicio del cliente de la API. La renovación de la sesión es un
   `QueuedInterceptor`: ante un 401 refresca una sola vez aunque fallen varias peticiones a la vez,
   y reintenta una sola vez.
4. **Modelos: Freezed con `json_serializable`.** Sin cambio respecto de la página.
5. **La ubicación en segundo plano** va en su propio registro: [ADR-0049](0049-la-ubicacion-en-segundo-plano-de-una-app-flutter-usa-geolocator-y-native-geofence.md).

## Consecuencias

- `build_runner` es obligatorio en toda app Flutter: genera los proveedores, las rutas y los modelos.
- Se reescriben las secciones «Arquitectura» (el árbol: `providers` junto a cada función en lugar de
  `view_models/`) y «Estado» de `flutter.md`.
- Las fuentes de Riverpod, go_router_builder y Dio se copian a `fuentes/pub/`, y la de `provider`
  se retira.

## Descartado

- **`provider` con `ChangeNotifier`.** Cada pantalla escribe a mano su estado de carga y de error, y
  el reemplazo en las pruebas es menos directo.
- **`package:http`.** La renovación única ante varios 401 simultáneos, los tiempos de espera y la
  cancelación se escriben a mano.
- **get_it con injectable junto a Riverpod.** Dos mecanismos de inyección para lo mismo.
