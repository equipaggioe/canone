# ADR-0191 · La primera cuenta de administración se registra con el código de instalación

- **Estado:** Aceptada. El usuario pidió un código fijo para cada repositorio, definido en Consola,
  con el que se registra la primera cuenta de administración (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/autenticacion.md`](../plataformas/autenticacion.md), «Cuentas»

## Contexto

Canone no decía cómo nace la primera cuenta de administración de una instalación. Un seeder corre
en cada despliegue sin entrada y no puede pedir una contraseña, y una contraseña inicial en las
credenciales quedaría como credencial para siempre.

## Decisión

1. **Mientras no hay una cuenta de administración, el registro acepta el código de instalación**,
   el campo `setup_code` de `Settings`, y la cuenta que se registra con él es de administración.
2. **Con la primera cuenta de administración, el registro deja de aceptar el código.**
3. El valor lo define Consola para cada repositorio, el mismo en todas sus instalaciones, y llega al
   servidor por `credentials.py`, como cualquier credencial.

## Consecuencias

- La cuenta nace por el registro normal, con su correo o su teléfono verificado, y agrega su passkey
  o su contraseña como cualquier otra.
- Si otra persona registra la primera cuenta, se reinstala.
- Sale `pendientes/primera-cuenta-de-administrador.md`.

## Descartado

- **Una tarea con la contraseña por la terminal:** pide entrar a la máquina, y la cuenta nace con
  contraseña.
- **Un seeder con el correo en `Settings` y la recuperación:** pide una regla de recuperación para
  una cuenta sin autenticadores.
