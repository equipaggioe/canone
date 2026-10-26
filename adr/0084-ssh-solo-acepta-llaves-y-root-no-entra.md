# ADR-0084 · `ssh` solo acepta llaves, y `root` no entra

- **Estado:** Aceptada
- **Fecha:** 2026-10-25
- **Alcance:** «SSH» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

El proveedor entrega el VPS con `root` y una contraseña, y nada cerraba ese acceso después: consola
crea una cuenta con `sudo` y llave, pero `root` seguía entrando con contraseña.

## Decisión

1. `root` no entra por `ssh`, ni con contraseña ni con llave: se entra con la cuenta que administra
   la máquina y `sudo`.
2. Ninguna cuenta entra por `ssh` con contraseña.
3. `install.py` crea esa cuenta con `--admin` y `--key`, en el grupo `sudo`, con la contraseña que
   pide al crearla. La primera vez corre como `root`.
4. `sudo` pide la contraseña de la cuenta, y consola la pide en cada operación con privilegios, sin
   guardarla.
5. `install.py` bloquea la contraseña de `root`.
6. La cuenta nace con dos llaves, y `install.py` falla con una sola.
7. La regla de `sshd` va en `/etc/ssh/sshd_config.d/00-<app>.conf`, que se lee antes
   que los archivos del proveedor.
8. `install.py` falla si la máquina no tiene `sudo`, si `ssh-keygen` no lee una llave,
   o si no recibe `--admin` y no lo lanza `sudo` desde una cuenta con llave.

## Consecuencias

- Una llave robada no da `root` de inmediato: le falta la contraseña de `sudo`, que solo consigue
  si deja una trampa en la cuenta y espera a que se escriba.
- La misma corrida crea la entrada nueva y cierra la de `root`, y una sola máquina se arma con un
  solo script.
- consola deja de crear la cuenta en `vps_setup.py`. La primera vez entra como `root` con lo que da
  el proveedor y lanza `install.py` con `--admin` y `--key`; desde entonces entra con la cuenta.
- Sin la computadora, se entra por `ssh` con la segunda llave, o por la consola web del proveedor
  con la cuenta y su contraseña. Sin llaves ni contraseña, queda el modo rescate del proveedor.
- Una llave mal copiada en `--key` deja fuera por `ssh`: `ssh-keygen` solo comprueba que es una
  llave, no que se tenga la privada.
- Comprobado en Debian 13 con OpenSSH 10.0: la cuenta nace en `sudo` con `/bin/bash`, `.ssh` en
  0700 y `authorized_keys` en 0600; `sudo -n` responde «a password is required» y `sudo -S` con la
  contraseña pasa; entra con la segunda llave, sin llave da `Permission denied (publickey)`, y
  `root` con su llave también, aunque un `50-cloud-init.conf` permita contraseñas y `root`. Sin
  `00-<app>.conf`, `root` entra. Correr de nuevo agrega solo las llaves que faltan.

## Descartado

- **`root` con llave, `PermitRootLogin prohibit-password`:** una llave robada da `root`, y todo
  corre como `root`, también lo que no lo necesita.
- **`sudo` sin contraseña, como en las imágenes cloud:** una llave robada da `root`, igual que
  `root` con llave.
- **`sudo` sin contraseña solo para `deploy.py`:** con una llave robada se despliega código propio,
  que se queda con la app y su base.
- **Que consola cree la cuenta:** la entrada nueva y el cierre de `root` quedaban en dos pasos, y
  `install.py` solo podía suponer que la cuenta existía.
- **Llamar al archivo `<app>.conf`:** se lee después de `50-cloud-init.conf`, y `sshd` se queda con
  el primer valor de cada opción.
