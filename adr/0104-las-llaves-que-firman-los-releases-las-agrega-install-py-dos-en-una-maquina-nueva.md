# ADR-0104 · Las llaves que firman los releases las agrega install.py, dos en una máquina nueva

- **Estado:** Aceptada
- **Fecha:** 2026-10-28
- **Alcance:** «Versiones» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

`deploy.py` comprueba la firma del `.sha256` contra `/etc/<app>/allowed_signers`, pero nada creaba
ese archivo, y el primer despliegue fallaba al no encontrarlo.

## Decisión

1. `install.py --signer <llave>` agrega a `allowed_signers` la línea
   `deploy namespaces="deploy" <llave>`, en el formato de *ALLOWED SIGNERS* de
   [`ssh-keygen`](../fuentes/openssh/ssh-keygen.1).
2. Una máquina nueva necesita dos `--signer`: la de la computadora de quien firma y una guardada
   fuera de ella, como las llaves de la cuenta que administra (ADR-0084).
3. Después, `--signer` solo agrega llaves. Una llave se retira borrando su línea.

## Consecuencias

- Perder la computadora no impide desplegar.
- Una firma hecha con la misma llave para otro espacio de nombres, como `git`, no despliega.
- Cada corrida de `install.py` en las pruebas lleva dos `--signer`.

## Descartado

- **Escribir `allowed_signers` a mano:** nada lo comprueba, y el primer despliegue falla.
- **Una sola llave:** perder la computadora deja sin desplegar hasta entrar y agregar otra.
