# ADR-0152 · El entorno del servidor se instala con el bytecode compilado y sin modo editable

- **Estado:** Aceptada
- **Fecha:** 2026-11-15
- **Alcance:** [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Versiones»; `deploy.py` de `plantilla/infra/`

## Contexto

`deploy.py` creaba el entorno con `uv sync --locked --no-dev`, y uv no compila el bytecode al
instalar: lo deja a Python, que lo guarda la primera vez que importa cada módulo. Las unidades no
pueden escribir en el entorno, por `ProtectSystem=strict`, así que cada proceso volvía a compilar
lo que importa. En el VPS de concordia, el 2026-11-15, `src/` tenía 3 archivos `.pyc`, y una vuelta
de `python -m app.tasks safety` gastaba entre 1,65 y 1,94 s de CPU; con el bytecode compilado,
entre 1,11 y 1,36 s. La documentación de uv dice que compilar es «typically desirable for
production images as it tends to improve startup time».

## Decisión

1. `deploy.py` corre `uv sync --locked --no-dev --no-editable --compile-bytecode`.
2. La app va sin modo editable, dentro del entorno: así su código también queda compilado.

## Consecuencias

- Cada proceso de Python de la app arranca más rápido: el servidor, las migraciones y cada tarea.
- Instalar una versión tarda unos 10 s más, y su entorno ocupa unos 100 MB más: de 585 MB a
  682 MB en concordia, medido en el VPS.
- Lo que importa la app sale del entorno, no de `src/`: un archivo que se lee con una ruta relativa
  a `__file__` tiene que ir dentro del paquete.
