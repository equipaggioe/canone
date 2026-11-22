# La medición de la accesibilidad en los clientes que no son de Qt

Tema pendiente: que cada cliente mida en CI lo que una herramienta puede medir de «Accesibilidad»
de [transversal.md](../plataformas/transversal.md#accesibilidad), como ya lo hace uno de Qt.

## Estado (verificado 2026-11-21)

Un cliente de Qt la mide con `tests/test_accessibility.py`, canónico, y cada repositorio da su
ventana en `tests/conftest.py`
([ADR-0216](../adr/0216-un-cliente-de-qt-mide-su-accesibilidad-con-una-prueba-canonica.md)). Los
demás clientes no miden nada.

| Cliente | Lo que trae la plataforma | Qué cubre |
| :--- | :--- | :--- |
| Flutter | `meetsGuideline`, de `flutter_test`, en una prueba de widget ([Accessibility testing](https://docs.flutter.dev/ui/accessibility/accessibility-testing)) | El contraste del texto, el tamaño de los objetivos y que tengan nombre. No cubre el teclado, el orden del foco, el movimiento ni los anuncios |
| Compose | `enableAccessibilityChecks()`, de `ui-test-junit4-accessibility`, desde Compose 1.8.0 ([Test your app's accessibility](https://developer.android.com/develop/ui/compose/accessibility/testing)) | Las comprobaciones del Accessibility Test Framework. Pide la API 34 y no corre en Robolectric |
| Web | Nada en `plantilla/sveltekit/`. axe-core es la herramienta que se usa para esto con Playwright | Sin evaluar |
| Flet | Nada: sus pruebas son de Python y no ven los widgets de Flutter | Sin evaluar |

Lo que una herramienta no ve se comprueba a mano en todos: W3C y GOV.UK lo recomiendan, y en la
prueba de GOV.UK diez herramientas juntas dejaron pasar cerca del 29 % de las fallas (los enlaces
están en el ADR-0216).

## Cuándo se retoma

Con cada cliente: se decide qué comprobaciones corre en CI, con la herramienta de su plataforma y
lo que esta no cubre escrito aparte, en un ADR como el 0216.
