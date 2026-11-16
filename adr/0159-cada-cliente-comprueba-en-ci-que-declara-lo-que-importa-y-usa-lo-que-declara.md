# ADR-0159 · Cada cliente comprueba en CI que declara lo que importa y usa lo que declara

- **Estado:** Aceptada
- **Fecha:** 2026-11-16
- **Alcance:** «Proyecto» y «Cumplimiento» de [`flutter.md`](../plataformas/flutter.md), [`sveltekit.md`](../plataformas/sveltekit.md) y [`android.md`](../plataformas/android.md); [`stack.md`](../stack.md); `plantilla/.github/workflows/ci.yml`; `plantilla/sveltekit/knip.json`; `scripts/verificar.py`

## Contexto

[`python.md`](../plataformas/python.md) pide declarar todo paquete que el código importa, aunque
otro lo traiga, y usar toda dependencia declarada, y deptry lo comprueba. Flutter, SvelteKit y
Android no tenían la regla, y Flutter declaraba `riverpod`, que llega con flutter_riverpod.

Comprobado el 2026-11-16, cada herramienta sobre un proyecto mínimo:

- **dependency_validator 5.1.0**, con Flutter 3.47.5: sale con 1 ante `riverpod` declarado y sin
  importar, y ante `collection` importado y sin declarar. Reconoce como usados los builders
  (freezed, json_serializable, riverpod_generator) y los paquetes con ejecutables (build_runner,
  swagger_parser). Sin `allow_pins: true`, también sale con 1 por cada versión exacta.
- **knip 6.45.1**, con SvelteKit 3: con `--dependencies`, sale con 1 ante una dependencia sin usar
  y ante un import sin declarar. Toma por paquete sin declarar el `$app/tsconfig` que extiende el
  `tsconfig.json`, y sin `.svelte-kit/` no resuelve los `./$types`.
- **`com.autonomousapps.dependency-analysis` 3.20.3**, con AGP 9.5.1 y Gradle 9.9.1: `buildHealth`
  falla ante una dependencia sin usar y ante un import de una transitiva. Aplicado solo en el
  `build.gradle.kts` raíz, no analiza `app`. Marca como no usado `espresso-core`, declarado junto a
  `ui-test-junit4` con el BOM de Compose 2026.09.00, y `onUnusedDependencies { exclude(...) }` lo
  saca.

## Decisión

1. Flutter, SvelteKit y Android llevan la regla de Python: se declara lo que se importa, y lo
   declarado se usa. Android admite además la dependencia que se declara para cambiar la versión
   que trae otra.
2. Flutter la comprueba con `dart run dependency_validator`, con `allow_pins: true` en
   `pubspec.yaml`, y deja de declarar `riverpod`.
3. SvelteKit la comprueba con `pnpm exec knip --dependencies`, después de `pnpm build`, con un
   `knip.json` que ignora los paquetes sin declarar de `tsconfig.json`.
4. Android la comprueba con `./gradlew buildHealth`, con el plugin en el raíz y en `app`. Cada
   aviso hace fallar el build, salvo `espresso-core` entre los no usados.

## Consecuencias

- Un paquete sin declarar o sin usar rompe CI en los tres clientes, como en Python.
- `knip.json` es igual en cada superficie, y `verificar.py` lo compara con la plantilla.

## Descartado

- **depcheck en SvelteKit:** sin versiones desde octubre de 2023.
- **Solo `depend_on_referenced_packages` en Flutter:** marca lo importado sin declarar, no lo
  declarado sin usar.
- **Escribir la regla sin herramienta:** una regla que no rompe CI es una sugerencia.
