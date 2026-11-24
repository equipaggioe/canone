# ADR-0225 · Equipaggio y consola son instrumentos de Canone

- **Estado:** Aceptada
- **Fecha:** 2026-11-23
- **Alcance:** `README.md`, `fastapi.md` y `plantilla/server/`

## Contexto

`fastapi.md` manda el correo y el SMS por la API de Equipaggio, y `despliegue.md` envía el journal a su
registro central, sin una condición. El README dice que Canone responde «si se usa X, ¿cómo se usa?», y
`plataformas/README.md` deja fuera de las páginas qué se usa: así leído, nombrar a Equipaggio dictaba el
producto de un tercero. Equipaggio y consola no son terceros: se construyen para servir a Canone.

## Decisión

1. El README nombra a Equipaggio y a consola como instrumentos de Canone, en «Instrumentos».
2. Una página nombra a un instrumento como nombra a Canone, sin «Con …».
3. La URL de la API de Equipaggio es una constante del código, la misma en todo despliegue, y la clave
   del cliente es `equipaggio_key` de `Settings`.
4. Consola no es obligatoria: quien despliega elige con qué corre los programas de Canone
   ([ADR-0107](0107-canone-fija-la-interfaz-de-sus-programas-y-no-la-herramienta-que-los-corre.md)).

## Consecuencias

- La plantilla del servidor manda el correo y el SMS sin una capa para otro proveedor.
- La constante `API` de `services/messages.py` vale `https://equipaggio.net/api`, que sale del URI de
  los tipos de problema de Equipaggio y de la regla de `/api`; no se probó contra el servicio.

## Descartado

- **Equipaggio como opción, «Con Equipaggio, …», como Stripe.** Lo trataría como el producto de un
  tercero, y no lo es.
- **Una interfaz sin implementación que cada repositorio completa.** La plantilla no enviaría nada y no
  se probaría entera.
