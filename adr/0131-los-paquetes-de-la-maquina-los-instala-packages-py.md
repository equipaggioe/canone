# ADR-0131 · Los paquetes de la máquina los instala `packages.py`, que también los nombra sin instalarlos

- **Estado:** Aceptada; los puntos 2 a 5 son propuesta
- **Fecha:** 2026-11-09
- **Alcance:** «Máquina» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

«Máquina» de `despliegue.md` nombraba los paquetes y dejaba que los pusiera quien prepara la
máquina. Consola los instalaba con una copia propia de la lista, que podía separarse de la de
Canone sin que nada lo avisara. El `README.md` de Canone dice que, cuando una convención exige un
mecanismo en una máquina, Canone da también el programa que lo implementa, y que la interfaz de sus
programas son sus argumentos y `stdin` ([ADR-0107](0107-canone-fija-la-interfaz-de-sus-programas-y-no-la-herramienta-que-los-corre.md)).

## Decisión

1. La lista de paquetes de la máquina vive solo en Canone, y quien despliega la toma de ahí.
2. `plantilla/infra/packages.py` instala con `apt-get` los paquetes de la máquina, antes de
   `install.py`, y falla si no corre como `root`.
3. Recibe `--extension`, `--turn` y `--logs`, con el mismo sentido que en `install.py`. Una
   extensión que el paquete `postgresql` ya trae no agrega ninguno.
4. `packages.py --list` imprime los paquetes, uno por línea, sin instalar nada, y corre en
   cualquier sistema: quien despliega muestra qué se va a instalar antes de entrar a la máquina.
   `--all` vale por todas las opciones, así que `--list --all` nombra todo lo que puede instalar.
5. El CI instala con `packages.py` todos los paquetes en un Debian 13, así que un nombre que
   Debian 13 no tiene falla ahí.

## Consecuencias

- Consola deja de tener la lista: corre `packages.py` en la máquina y `packages.py --list` en la
  suya.
- `packages.py` corre con el `python3` de la máquina, que es uno de los paquetes que instala: una
  imagen sin `python3` lo necesita antes.
- La lista sigue escrita también en «Máquina», como convención; `packages.py` la implementa y se
  mantiene sincronizado con ella.
- El swap sigue a cargo de quien prepara la máquina.

## Descartado

- **Un archivo de datos con la lista, que leen `install.py` y Consola:** la interfaz de los
  programas de Canone son sus argumentos y `stdin`, y un formato de archivo leído desde afuera
  sería una interfaz más.
- **Que `install.py` instale los paquetes:** importa `pwd`, que no existe en Windows, así que no
  podría nombrarlos sin instalarlos desde la computadora de quien despliega; y lo que comprueba de
  la máquina, como `sudo` o `unattended-upgrades`, lo comprueba porque otro lo puso antes.
