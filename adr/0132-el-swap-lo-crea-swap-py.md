# ADR-0132 · El swap de la máquina lo crea `swap.py`

- **Estado:** Aceptada
- **Fecha:** 2026-11-09
- **Alcance:** «Máquina» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

`install.py` falla si la máquina tiene menos swap que memoria, y «Máquina» dejaba el swap a quien
prepara la máquina: Consola lo creaba con un script propio. El `README.md` de Canone dice que,
cuando una convención exige un mecanismo en una máquina, Canone da también el programa que lo
implementa. El [ADR-0131](0131-los-paquetes-de-la-maquina-los-instala-packages-py.md) dejaba el
swap fuera; este lo trae a Canone.

## Decisión

1. `plantilla/infra/swap.py` crea `/swapfile` con lo que le falta al swap para llegar a la memoria,
   y lo agrega una sola vez a `/etc/fstab`. Corre como `root`.
2. Un `/swapfile` que no alcanza lo vuelve a crear, y con tanto swap como memoria no cambia nada.
3. Quien despliega lo corre antes de `install.py`, igual que `packages.py`. Canone no lo corre.
4. El CI lo prueba en el runner de GitHub y no en un contenedor: `swapon` necesita el kernel de una
   máquina.

## Consecuencias

- Consola deja de tener el script del swap: sube `swap.py` y lo corre.
- `swap.py` corre con el `python3` de la máquina, como `packages.py`.

## Descartado

- **Que `install.py` cree el swap:** falla si falta, como comprobación de lo que otro puso antes, y
  así queda una sola cosa que hace cada programa.
