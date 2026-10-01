# ADR-0025 · Los tipos los revisa Pyrefly en modo strict

- **Estado:** Aceptada
- **Fecha:** 2026-10-01
- **Alcance:** [plataformas/python.md](../plataformas/python.md),
  [plataformas/qt.md](../plataformas/qt.md), el `pyproject.toml` de `plantilla/server/`,
  `plantilla/qt/` y `plantilla/flet/`, y `plantilla/.github/workflows/ci.yml`

## Contexto

`python.md` fijaba mypy en modo strict, porque era «el verificador de referencia de la
documentación de typing». La documentación de typing no nombra un verificador de referencia: la
elección es propia.

Se compararon mypy 2.3.1 con el plugin `pydantic.mypy`, Pyright 1.1.414, Pyrefly 1.3.2 y ty
0.0.84, todos en modo strict. Se corrieron sobre `plantilla/server/` y `plantilla/qt/`, y sobre
23 errores escritos a propósito en Pydantic, SQLAlchemy, PySide6 y Python común.

| | mypy | Pyright | Pyrefly | ty |
|---|---|---|---|---|
| Falsos positivos en las plantillas | 0 | 5 | 0 | 2 |
| Tiempo sobre `plantilla/server/` | 23.2 s | 4.1 s | 0.5 s | 0.4 s |
| Alias camelCase mal escrito | no lo ve | por la razón equivocada | sí | por la razón equivocada |

Los falsos positivos de Pyright y ty vienen de no aplicar `alias_generator=to_camel`. Pyright,
además, no sabe que pydantic-settings lee los campos del entorno.

## Decisión

- Pyrefly con `preset = "strict"` en toda pieza en Python. Lo corre CI con `pyrefly check`.
- `enabled-ignores = ["pyrefly"]`: un error se ignora con `# pyrefly: ignore[<código>]`. Pyrefly
  aplica `# type: ignore[<código>]` a toda la línea sin mirar el código.
- Fuera de Qt, `missing-override-decorator` va apagado: `@override` es obligatorio solo en
  `qt.md`.

## Consecuencias

- Revisar un servidor tarda medio segundo y no veinte.
- Un alias camelCase mal escrito en un esquema se detecta antes de correr.
- Pyrefly no marca un campo que el modelo no declara. Pydantic lo descarta al validar, y un
  esquema de entrada lo rechaza con `extra="forbid"`.
- Ninguna herramienta marca un `# pyrefly: ignore` sin código: la regla se cuida al revisar.
- Pyrefly es estable desde mayo de 2026: lleva meses, no años, de uso amplio.
- Ninguno de los cuatro detecta un `connect` o un `emit` de PySide6 con el tipo equivocado.

## Descartado

- **mypy** (la regla anterior): no ve un alias mal escrito cuando lo genera `to_camel`, y tarda 23
  segundos donde Pyrefly tarda medio.
- **Pyright:** 5 falsos positivos en archivos canónicos de Pydantic, que habría que tapar con
  ignores.
- **ty:** 2 falsos positivos con `to_camel`, no exige anotar las funciones y está en beta.
- **basedpyright:** usa el motor de Pyright. No se probó.
