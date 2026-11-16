# ADR-0153 · Un script de `sh` con `set -e` no niega un comando con `!`

- **Estado:** Aceptada
- **Fecha:** 2026-11-15
- **Alcance:** [`repositorio.md`](../repositorio.md), «Scripts de shell»; `scripts/verificar.py`; `scripts/infra/`

## Contexto

POSIX ignora `-e` en un comando que empieza con `!`. Comprobado el 2026-11-15 con `sh -ec '! true;
echo sigue'`, que imprime `sigue`. Siete comprobaciones de `packages.sh`, `swap.sh` y
`uninstall.sh` eran `! <comando>`: nunca podían fallar.

## Decisión

1. Se niega con `if <comando>; then exit 1; fi`. Las pruebas de `scripts/infra/` lo hacen con una
   función `not`.
2. `scripts/verificar.py` falla con una línea que empieza con `!` en un script de `sh` con `set -e`,
   en canone y en cada repositorio.
