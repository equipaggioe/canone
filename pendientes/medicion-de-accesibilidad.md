# La medición de la accesibilidad de un cliente de Qt

Tema pendiente: que canone dé la medición de lo que pide «Accesibilidad» de
[transversal.md](../plataformas/transversal.md#accesibilidad), en vez de que cada repositorio escriba
la suya.

## Estado (verificado 2026-11-21)

Consola escribió la suya: `desktop/scripts/aa.py`. Abre la ventana sin pantalla, con contenido, y
escribe lo que falla de 1.4.3, 1.4.4, 1.4.11, 2.1.1, 2.1.2, 2.2.2, 2.4.3, 2.4.7, 2.5.8 y 4.1.3. Corre
igual en Windows y en Linux. Canone no tiene nada parecido: `plantilla/qt/` no trae ninguna prueba
de accesibilidad, y `test_theme.py` comprueba el estilo, no la ventana.

| Parte | Qué hace | De quién es |
| :--- | :--- | :--- |
| Contraste del texto (1.4.3) y de los glifos e iconos (1.4.11) | Toma el color que más cubre el control, dibujado con lo que tiene debajo, contra su texto o el píxel que más contrasta | Qt, de cualquier repositorio |
| Objetivos de 24 × 24 (2.5.8) | Lo que responde al ratón, por su rol accesible o por el cursor que pone | Qt |
| Teclado (2.1.1), trampas (2.1.2) y foco visible (2.4.7) | Recorre la ventana con Tab y compara cada control antes y después del foco | Qt |
| Orden del foco (2.4.3) | Que Tab vaya banda por banda y, en cada una, por líneas | Qt, salvo qué bandas tiene la ventana |
| Lo que se mueve (2.2.2) | Los `QTimer` repetidos y las animaciones sin fin, antes y después de detenerlos | Qt, salvo con qué se detienen |
| Texto al 200 % (1.4.4) | La ventana a 960 × 500 px de Qt, lo que deja 1920 × 1080 al 200 %, y lo que se corta | Qt |
| Mensajes de estado (4.1.3) | Graba los `QAccessibleAnnouncementEvent` mientras dispara cambios de estado | Qt, salvo qué cambios se disparan |
| Fuentes sin pantalla | En Windows apunta `QT_QPA_FONTDIR` a las del sistema: sin eso, cada texto mide el doble de ancho y todo tamaño sale mal | Qt |

Lo propio de cada repositorio es poco: cómo abrir la ventana con contenido, qué bandas forman el
orden de lectura, qué detiene lo que se mueve y qué cambios de estado se anuncian.

Lo que el script no ve se probó a mano en Consola: con teclas reales enviadas desde otro proceso y
con un cliente de UI Automation, que recibió las notificaciones. Ningún lector concreto (NVDA o
Narrador) se escuchó.

## Propuesta

- La parte de Qt va en `plantilla/qt/` como archivo canónico, que se copia sin editar, como
  `test_theme.py`, y `scripts/verificar.py` lo compara.
- Lo propio de cada repositorio va en un módulo chico que el canónico importa: abre la ventana y
  devuelve sus bandas, las acciones que detienen lo que se mueve y los casos de los mensajes de
  estado.
- Falta decidir si es una prueba de `pytest`, que corre en CI, o un script que se corre a mano. En
  Consola tarda unos segundos sin pantalla.
- Compose, Flutter, Flet y la web necesitan su equivalente; ninguno lo tiene.

## Cuándo se retoma

Cuando se decida la propuesta: va en un ADR, y Consola reemplaza su `aa.py` por el canónico y su
módulo propio.
