# ADR-0242 · `copiar.py` hace la copia de los archivos canónicos

- **Estado:** Aceptada
- **Fecha:** 2026-11-25
- **Alcance:** `scripts/copiar.py`, `scripts/verificar.py` y `plantilla/README.md`

## Contexto

Los archivos canónicos se copiaban a mano. Un servidor con cuentas copia 95, y cada cambio de la
plantilla se vuelve a copiar en cada repositorio. La lista está solo en `verificar.py`.

## Decisión

1. El programa que copia está en Canone, y quien lo corre, como Consola, no tiene una lista propia.
2. `copias` de `verificar.py` da los archivos canónicos de un repositorio: los que `verificar.py`
   compara son los que `copiar.py` copia.
3. Sin `--aplicar` solo nombra lo que crearía y lo que reemplazaría.
4. `--cuentas` copia los archivos de las cuentas a un servidor sin `models/account/`.
5. Si reemplazaría un archivo cuyo contenido no está en el último commit, no copia nada.

## Consecuencias

- Un archivo canónico nuevo en `verificar.py` se copia sin tocar `copiar.py`.
- Un repositorio que no sigue la plantilla deja de funcionar al copiar sus archivos hasta completar
  los demás: la copia reemplaza su `database.py` o su `alembic/env.py`.

## Descartado

- **Copiar desde Consola:** su lista sería una segunda copia que se desincroniza.
