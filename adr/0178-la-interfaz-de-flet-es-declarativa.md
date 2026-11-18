# ADR-0178 · La interfaz de Flet es declarativa

- **Estado:** Aceptada. El usuario eligió el estilo declarativo (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/flet.md`](../plataformas/flet.md), «Componentes», «Async» y
  «Navegación», y `fuentes/flet/`

## Contexto

Flet 1.1.2 es imperativo por defecto y ofrece además componentes, hooks, observables y `Router`.
Comprobado en la distro WSL `Testing` con `flet test`, Flet 1.1.2 y Flutter 3.47.9: una app con
`Router` y `manage_views=True`, una ruta de layout que manda al inicio de sesión, `use_route_params`,
`use_effect` con un setup `async`, `use_dialog`, un `@ft.observable` que redibuja otra pantalla y
`not_found` pasa la prueba. Con un `not_found` que devuelve una `View`, Flutter falla al dibujar
una `View` dentro de otra.

## Decisión

1. **La interfaz es declarativa:** componentes `@ft.component`, el estado compartido en
   `@ft.observable` y el de cada vista en hooks.
2. **La navegación usa `ft.Router` con `manage_views=True`.**
3. **Un diálogo sale del estado, con `ft.use_dialog()`.**
4. **El trabajo de fondo de un componente va en `ft.use_effect`**, que lo cancela al desmontarse.
5. **`custom-controls.md` sale de `fuentes/flet/`**, y entran `declarative-vs-imperative.md` y
   `router.md`.

## Consecuencias

- Salen las convenciones de los controles propios, de `page.views` armado en `on_route_change`,
  de `TemplateRoute`, de `pop_views_until()` y del handler que hace `yield`.
- `can_pop` y `on_confirm_pop` con `Router` no se probaron.

## Descartado

- **El estilo imperativo:** cada handler mantiene la pantalla al día a mano, y un `update()`
  olvidado deja el estado y la pantalla distintos sin aviso.
