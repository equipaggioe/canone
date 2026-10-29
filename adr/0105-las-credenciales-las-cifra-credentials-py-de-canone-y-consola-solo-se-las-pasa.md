# ADR-0105 · Las credenciales las cifra credentials.py de canone, y consola solo se las pasa

- **Estado:** Aceptada
- **Fecha:** 2026-10-28
- **Alcance:** «Configuración» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

El punto 3 del ADR-0076 le daba a consola cifrar cada valor en el servidor. Chocaba con el
ADR-0075: consola no escribe nada propio, y lo que no tiene plantilla se agrega primero a canone.
consola tenía que copiar la regla de nombres de `despliegue.md`, como `--name=app_<campo>` y la
carpeta de cada credencial, y una máquina instalada solo con canone dejaba el servidor sin arrancar,
porque a `Settings` le faltaban sus campos, y el respaldo sin contraseña.

## Decisión

1. `plantilla/infra/credentials.py <app>` lee por stdin una línea `campo=valor` por credencial, y
   cifra cada campo de `Settings` en `<app>/` con `--name=app_<campo>`, `restic_password` en
   `<app>-backup/` y `github_token` en `<app>-deploy/`, cada una con su propio nombre. Reemplaza el
   punto 3 del ADR-0076.
2. consola le pasa a `credentials.py` los valores de `.consola/config.env`.
3. `credentials.py` escribe solo los campos que recibe, y reinicia el servidor si corre.
4. `credentials.py` falla sin escribir nada ante una línea que no es `campo=valor`, un valor vacío,
   un campo repetido, o `database_url` o `turn_secret`, que escribe `install.py`. Su mensaje nunca
   lleva el valor.

## Consecuencias

- El servidor se instala y arranca sin consola, como dice el ADR-0075.
- Cambiar un secreto no vuelve a correr `install.py`, que recarga el firewall, reinicia journald y
  recarga `ssh`.
- Los valores no quedan en la línea de comandos ni en el historial de la shell.
- `deploy.sh` y `backup.sh` cifran sus credenciales con `credentials.py`, y no a mano.

## Descartado

- **Que `install.py` lea las credenciales por stdin:** cambiar un secreto volvería a correr toda la
  instalación.
- **Que consola siga cifrando, punto 3 del ADR-0076:** copia una regla de canone sin plantilla.
- **Los valores como argumentos:** quedan en el historial de la shell y en la lista de procesos.
