# Despliegue

**La convención es cómo tiene que quedar el despliegue, no cómo se llega a él.** Quién lo ejecute
—una herramienta, un pipeline o una persona a mano— no cambia nada de lo de abajo: todo se comprueba
en el servidor terminado.

Cómo está instalado hoy un producto concreto va en su `docs/arquitectura/00_sistema.md`, no aquí.

## Lo que da la cara a internet

| Debe quedar así | Por qué |
|---|---|
| **Un solo proceso escucha en una interfaz pública: el proxy inverso** | Cada puerto abierto de más es superficie que nadie revisa |
| **El firewall deniega por defecto** y abre solo lo que el proxy publica | Lo de arriba es una afirmación sobre la configuración; el firewall es lo que la sostiene el día que alguien deja un servicio escuchando de más |
| **TLS termina en el proxy** | El tramo interno es HTTP. Un backend con su propio certificado duplica la renovación, y la copia que nadie mira es la que vence |
| **Con proxy delante, el backend escucha en loopback** | Si además escucha afuera, se lo alcanza salteando las cabeceras, la CSP y el límite de tasa |
| **Las cabeceras de seguridad y la CSP las emite el proxy, una sola vez** | Una aplicación que también las emite deja dos valores para el mismo encabezado y gana el último que llega. Qué tiene que decir la CSP es de [seguridad.md](seguridad.md) |

## Los procesos

| Debe quedar así | Por qué |
|---|---|
| **Cada pieza corre bajo el supervisor del sistema** y vuelve sola después de un reinicio de la máquina | Un proceso lanzado dentro de una sesión muere con ella, y nadie se entera hasta que alguien entra a mirar |
| **Ningún servicio del producto corre como root**, y cada producto tiene su usuario | Acota lo que alcanza una ejecución remota, y separa a un producto de los demás en la misma máquina |
| **La unidad del servicio queda aislada**: sin privilegios nuevos, con `/tmp` propio y el sistema de archivos en solo lectura salvo lo que deba escribir | No correr como root dejó de alcanzar hace mucho. Sin aislamiento, una ejecución remota en el backend lee todo lo que el usuario puede leer y escribe en un `/tmp` compartido con los demás servicios |
| **Dónde escucha y con qué certificado se lo dice el servicio que lo arranca**, no una constante en el código | Si el código también elige, contradice a la unidad que lo lanzó y se termina depurando el archivo equivocado |
| **Un despliegue no está terminado hasta que el servicio responde**, no hasta que el proceso existe | Un supervisor que reintenta solo devuelve éxito apenas el proceso arranca, aunque muera un segundo después; y un proceso vivo con la base inalcanzable sirve errores igual. Se comprueba contra el endpoint de salud — ver [fastapi.md](fastapi.md) |

## Los datos

| Debe quedar así | Por qué |
|---|---|
| **Una base y un usuario de base por producto** | Compartirlas hace que un volcado, una migración o un `DROP` crucen de un producto a otro |
| **El estado persistente vive fuera del árbol del repositorio desplegado** | Ese árbol se sincroniza desde git: lo que quede dentro se pierde en la próxima actualización |

## El código y la configuración

| Debe quedar así | Por qué |
|---|---|
| **Lo desplegado es un commit empujado**, no una copia del árbol de trabajo de alguien | Si no, lo que está corriendo no existe en ningún historial y no hay a dónde volver |
| **La configuración del servidor vive fuera del árbol del repositorio** | Un archivo de configuración dentro del repositorio termina enlazado desde el sistema, y entonces el servicio pasa a depender del árbol de git |
| **Los secretos llegan como archivos con permisos restringidos** | En la línea de comandos los lee cualquiera con `ps`; dentro de la unidad del servicio quedan legibles para todo el sistema |
