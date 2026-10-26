# ADR-0087 · La cuenta que administra no es una cuenta de la app

- **Estado:** Aceptada
- **Fecha:** 2026-10-26
- **Alcance:** «Proyecto» y «SSH» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/install.py`

## Contexto

`<app>` nombraba rutas, unidades, cuentas y roles, pero ninguna regla decía de dónde salía. consola
usa el nombre del repositorio, y también lo propone para la cuenta que administra.

`install.py` crea la cuenta que administra antes de correr `systemd-sysusers`, y `systemd-sysusers`
conserva una cuenta que ya existe. Con `--admin` igual a `<app>`, el servidor corre con la cuenta
del grupo `sudo`, que entra por `ssh`.

## Decisión

1. `<app>` es el nombre del repositorio del producto.
2. `install.py` falla si la cuenta que administra es `<app>`, `<app>_owner` o `<app>-receiver`.

## Consecuencias

- consola tiene que dejar de proponer el nombre del repositorio para la cuenta que administra.
- Comprobado en Debian 13 con systemd 257: una cuenta del grupo `sudo` llamada como la app sigue
  en `sudo` después de `systemd-sysusers`, e `install.py` rechaza `--admin` o `SUDO_USER` con el
  nombre de la app, del dueño o de la receptora.
