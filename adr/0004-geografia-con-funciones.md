# ADR-0004 · Una columna geográfica se declara con una función, no con un Annotated

- **Estado:** Propuesta
- **Fecha:** 2026-09-22
- **Alcance:** `server/app/models/`, repositorios con PostGIS

## Contexto

El resto de los alias de `models/base.py` son `Annotated[tipo, mapped_column(...)]`, y funciona
porque los tipos de SQLAlchemy son inmutables. `Geography` de geoalchemy2 no lo es: guarda
`nullable` **en la instancia del tipo** y la muta al crear cada columna.

Un `Annotated` comparte una única instancia de `Geography` entre todas las columnas que lo usan, así
que la última columna procesada le impone su `nullable` a todas las demás. No hay error: se nota al
generar la migración, o no se nota.

Cinco repositorios tienen la forma con `Annotated`. concordia tiene la forma con funciones.

## Decisión

1. `GeoPoint` y `GeoLine` son alias de tipo puros (`WKBElement`), solo para la anotación
   `Mapped[...]`.
2. La columna se declara con `geo_point(nullable=...)` o `geo_line(nullable=...)`, que crean una
   instancia nueva de `Geography` por columna.
3. `Geography`, no `Geometry`, con `srid=4326`: las distancias salen en metros sin proyectar.
4. `spatial_index=False` en la declaración; el índice GiST se crea en la migración.

## Consecuencias

- Cada columna tiene su propio `nullable` y el acoplamiento desaparece.
- La declaración es dos líneas en vez de una anotación, y es la excepción del archivo: lleva el
  comentario que explica por qué.

## Descartado

- **Declarar `Geography` inline en cada modelo:** funciona, pero repite `srid=4326` y
  `spatial_index=False` en cada columna, y la primera que los olvide crea un índice de más.
