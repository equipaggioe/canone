# ADR-0095 · Una lista de nombres que toma una regla no es una fuente

- **Estado:** Aceptada
- **Fecha:** 2026-10-27
- **Alcance:** «Qué implica citar» de [`plataformas/README.md`](../plataformas/README.md), «Caddy»
  de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y `fuentes/`

## Contexto

`Permissions-Policy` no tiene una forma de negar todo: cada función se niega por su nombre, y la
que no se nombra queda permitida. `install.py` toma los nombres del registro de funciones del W3C,
y la página no lo decía. El registro no puede ser fuente: no dice qué hacer, solo lista nombres. Y
una regla propia no nombraba nada que la página no citara.

## Decisión

1. Una lista de nombres que una regla toma de otro, como los de un registro, no es una fuente: la
   regla dice de dónde la toma y enlaza su copia en `fuentes/`, aunque no se cite.
2. «Caddy» dice que `Permissions-Policy` nombra cada función de *Standardized Features* del
   registro del W3C, y `publickey-credentials-create` de Web Authentication Level 3.
3. `fuentes/w3c/permissions-policy-features.md` es el registro en el commit 2939804, el que usa
   `install.py`.

## Consecuencias

- Quien actualiza la lista sabe de dónde salen los nombres y con qué versión compararla.
- Comprobado: las 50 funciones de *Standardized Features* de la copia son las de `FEATURES` en
  `install.py`, que suma `publickey-credentials-create`.

## Descartado

- **Nombrar el registro solo en un comentario de `install.py`:** la página no diría de dónde sale
  la lista.
- **Negar solo unas pocas funciones, como el ejemplo de OWASP:** las demás, y las nuevas, quedarían
  permitidas.
