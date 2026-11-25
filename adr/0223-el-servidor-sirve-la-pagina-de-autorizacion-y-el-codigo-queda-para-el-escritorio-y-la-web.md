# ADR-0223 · El servidor sirve la página de autorización, y el código queda para el escritorio y la web

- **Estado:** Aceptada. El [ADR-0239](0239-verificar-compara-los-archivos-de-las-cuentas.md) reemplaza parte del punto 2.
- **Fecha:** 2026-11-23
- **Alcance:** `plataformas/autenticacion.md`, `fastapi.md`, `plantilla/server/` y los workflows

## Contexto

Con el plugin del [ADR-0222](0222-las-apps-de-flutter-y-flet-usan-la-passkey-con-un-plugin-de-la-plantilla.md),
las apps del teléfono entran con passkey sin el navegador. El código de autorización queda para lo
que no tiene una API de passkeys en la plantilla: las apps de escritorio y las que corren en el
navegador. Un producto puede no tener web, y aun así necesita la página que pide la passkey.

## Decisión

1. El servidor sirve la página de autorización, con su estilo y su script en la misma página.
2. Los clientes son la constante `CLIENTS` de `services/clients.py`: cambian con el código, no con el
   despliegue.
3. La web es el cliente `web`, con una URI de retorno por superficie de `domain`.
4. La página manda la passkey con `fetch` a `POST /api/auth/authorize`, el servidor
   responde la URI de retorno con el código, y la página va a ella. Una passkey que falla deja la
   petición esperando, y el usuario vuelve a intentar sin recargar.
5. La petición espera en Valkey 10 minutos, bajo un id que lleva la página.
6. Un canje reclama el código en Valkey con `SET NX`: dos canjes al mismo tiempo no
   abren dos sesiones.
7. El texto de la página sale del catálogo de Babel, y el CI compila los catálogos
   antes de pytest.

## Consecuencias

- Un producto sin web ofrece passkey en el escritorio.
- El aspecto de la página no sigue a la web: los colores de la marca, desde `brand/tokens/`, quedan
  pendientes.
- `babel` pasa a ser una dependencia del servidor, no solo de desarrollo.

## Descartado

- **La página en la web de SvelteKit.** Obliga a tener una superficie web aunque el producto sea solo
  de escritorio o de teléfono.
- **Un formulario que el servidor responde con un 303 a la URI de retorno.** Una passkey que falla
  dejaría al usuario en una página de error del servidor, sin volver a intentar.
