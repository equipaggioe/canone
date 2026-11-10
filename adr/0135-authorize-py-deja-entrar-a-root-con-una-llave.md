# ADR-0135 · `authorize.py` deja entrar a `root` con una llave antes de `install.py`

- **Estado:** Aceptada
- **Fecha:** 2026-11-09
- **Alcance:** «SSH» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

`packages.py`, `swap.py` e `install.py` corren como `root` en una máquina a la que se entra con
una llave. Una máquina nueva del proveedor puede aceptar solo la contraseña de `root`, y Canone no
traía nada para poner la llave: quien preparaba la máquina la copiaba a mano, o Consola editaba
`authorized_keys` por su cuenta, y lo que deja un cambio permanente en la máquina lo hace un
programa de Canone.

## Decisión

1. `plantilla/infra/authorize.py '<llave pública>'` corre como `root` y agrega la llave a su
   `authorized_keys`, una sola vez, con modos 700 y 600.
2. Falla sin escribir nada si la línea no es una llave que `ssh-keygen` lea.
3. Quien prepara la máquina lo sube y lo corre entrando una vez con la contraseña de `root`. Canone
   no lo corre.

## Consecuencias

- Una máquina nueva se prepara con su IP y la contraseña de `root`, sin copiar la llave a mano.
- Después de `install.py`, `root` no entra y la llave de su `authorized_keys` deja de servir.

## Descartado

- **Que `install.py` ponga la llave de `root`:** corre después de entrar, y bloquea `root`.
- **Dejarlo a `ssh-copy-id`:** no está en el OpenSSH de Windows.
