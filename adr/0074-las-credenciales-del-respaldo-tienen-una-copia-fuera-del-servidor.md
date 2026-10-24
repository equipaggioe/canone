# ADR-0074 · Las credenciales del respaldo tienen una copia fuera del servidor

- **Estado:** Propuesta
- **Fecha:** 2026-10-23
- **Alcance:** «Configuración» de [`plataformas/despliegue.md`](../plataformas/despliegue.md)

## Contexto

Las credenciales de `<app>-backup/` vivían solo en el credstore, cifradas con `systemd-creds`.
Comprobado en Debian 13 con systemd 257: una credencial cifrada con la llave de una máquina falla
en otra con «Decryption failed (incorrect key?)», y restic 0.18.0 con otra contraseña responde
«wrong password or no key found». Perder el servidor era perder el respaldo.

## Decisión

1. «Configuración» cita la sección 2.9 del *Secrets Management Cheat Sheet* de OWASP.
2. Cada credencial de `<app>-backup/` tiene una copia en el gestor de contraseñas de quien
   despliega.
3. Cada mes, quien despliega abre el repositorio con esa copia, con `restic snapshots`, desde su
   máquina.

## Consecuencias

- El respaldo se restaura en una máquina nueva sin la llave de la vieja.
- La prueba mensual es manual: nada la hace cumplir.
- La 2.9 pide además vigilar el acceso al lugar de la copia; en un gestor de contraseñas lo hace
  el gestor.

## Descartado

- **Cifrar con `systemd-creds --with-key=null`:** deja la credencial en claro en el disco, contra
  «Configuración».
- **Una segunda copia del credstore en el propio repositorio de restic:** se cifra con la misma
  contraseña que hay que recuperar.
