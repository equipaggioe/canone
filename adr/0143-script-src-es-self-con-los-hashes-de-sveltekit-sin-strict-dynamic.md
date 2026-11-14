# ADR-0143 · `script-src` es `'self'` con los hashes de SvelteKit, sin `'strict-dynamic'`

- **Estado:** Aceptada
- **Fecha:** 2026-11-14
- **Alcance:** [`plataformas/sveltekit.md`](../plataformas/sveltekit.md), «CSP» y «Cumplimiento»;
  `plantilla/sveltekit/vite.config.ts` y [`scripts/verificar.py`](../scripts/verificar.py)

## Contexto

La plantilla ponía `'strict-dynamic'` en el `script-src` del build, la *Hash-based Strict Policy*
del *CSP Cheat Sheet* de OWASP. SvelteKit arranca cada página con un script incrustado que carga
`start.js` y `app.js` con `import()`. En CSP Level 3, `'strict-dynamic'` deja pasar solo lo que
carga un `<script>` que no insertó el parser, e ignora `'self'`.

Comprobado con SvelteKit 3.1.1 y 3.2.0, Vite 8.3.6 y 8.3.8, `adapter-static` 4.0.1 y el Chromium de
Playwright 1.65.0 y 1.65.1: la portada prerenderizada no hidrata, y el `import()` de `start.js`
lanza un `securitypolicyviolation`. El [ADR-0112](0112-sveltekit-es-la-version-3-y-se-configura-en-vite-config.md)
probó que la plantilla compilaba y llevaba la CSP, no que la página hidratara.

## Decisión

1. **`script-src` es `'self'`, con los hashes que agrega SvelteKit, y no lleva `'strict-dynamic'`**,
   en desarrollo y en el build.
2. `object-src 'none'` y `base-uri 'none'` se quedan.
3. Un formulario de pago incrustado pone los dominios de su pasarela en `script-src`, `frame-src` y
   `connect-src`.
4. `verificar.py` exige `script-src 'self'` en `vite.config.ts`, y la prueba de Playwright de cada
   página falla si vuelve `'strict-dynamic'`.

## Consecuencias

- La página hidrata. Comprobado con SvelteKit 3.2.0, Vite 8.3.8 y Playwright 1.65.1: el botón
  responde, el service worker se registra y no hay ningún `securitypolicyviolation`.
- Puede correr como script cualquier archivo JavaScript del origen. Lo demás no corre: con
  `nosniff`, que Caddy pone en toda respuesta y prueba `scripts/infra/caddy.sh`, una respuesta
  JSON o una imagen no corre como script, ni clásico ni módulo. Comprobado con el Chromium de
  Playwright 1.65.1. Sin `nosniff`, el JSON sí corrió como script clásico.
- Desarrollo y build tienen la misma `script-src`, y `vite.config.ts` deja de distinguirlos.

## Descartado

- **`'strict-dynamic'` con `bundleStrategy: 'inline'`:** cumple la *Strict CSP*, pero cada página
  lleva la app entera. Con Leaflet cargado en una sola página, cada HTML pesa unos 75 KB con gzip,
  frente a 0,9 KB, y el JavaScript no se reutiliza entre páginas. Comprobado con SvelteKit 3.2.0.
- **Nonces:** piden un HTML distinto en cada respuesta, y las páginas son estáticas.
