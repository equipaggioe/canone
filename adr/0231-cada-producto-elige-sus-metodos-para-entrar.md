# ADR-0231 · Cada producto elige sus métodos para entrar

- **Estado:** Aceptada
- **Fecha:** 2026-11-23
- **Alcance:** `autenticacion.md`, `fastapi.md` y `plantilla/server/`

## Contexto

`autenticacion.md` decía que el servidor acepta en toda cuenta los métodos para entrar, y que cada
repositorio elige cuáles ofrece cada pieza. Un producto que no quería un método dejaba abiertas sus
rutas, que un atacante puede llamar aunque ninguna pantalla las ofrezca, y con los archivos de
autenticación copiados sin editar no podía quitarlas.

## Decisión

1. Cada repositorio elige qué métodos usa su producto: la passkey, el código por SMS y la contraseña,
   en cualquier combinación.
2. Los métodos son la constante `METHODS` de `methods.py`: cambian con el producto, no con el
   despliegue.
3. El servidor monta solo las rutas de esos métodos, y el registro acepta solo sus autenticadores.
   El código de autorización va con la passkey, porque su página la pide.
4. Si el producto usa la passkey, una cuenta de administración entra solo con ella. Si no la usa,
   entra con los métodos del producto.
5. Las pruebas de un método que el producto no usa se saltan, y las de la sesión la abren sin pasar
   por un método.

## Consecuencias

- Sin passkey, la cuenta de administración entra con un método que se puede suplantar con phishing.
- Una app de escritorio de un producto sin passkey entra con sus otros métodos, sin el código de
  autorización.
- `openapi.json` cambia con los métodos del producto.
- La parte 6 agrega el código por SMS a `Method`.

## Descartado

- **Un campo de `Settings`.** El método es una decisión del producto, no de cada despliegue.
- **Montar todas las rutas y que el cliente elija.** Deja abierto un método que nadie usa.
- **Que cada repositorio borre los archivos del método que no usa.** Rompe la copia sin editar.
- **La passkey siempre, para la cuenta de administración.** Obligaría a todo producto a llevarla.
