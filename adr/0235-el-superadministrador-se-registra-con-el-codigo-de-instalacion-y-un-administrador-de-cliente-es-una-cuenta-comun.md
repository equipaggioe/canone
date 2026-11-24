# ADR-0235 · El superadministrador se registra con el código de instalación, y un administrador de cliente es una cuenta común

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Alcance:** `autenticacion.md` y `plantilla/server/`

## Contexto

El [ADR-0191](0191-la-primera-cuenta-de-administracion-se-registra-con-el-codigo-de-instalacion.md)
hizo nacer la primera cuenta de administración con el código de instalación, pero «por el registro
normal, con su correo o su teléfono verificado». El
[ADR-0226](0226-el-registro-trae-el-codigo-y-la-passkey-y-volver-a-autenticarse-renueva-la-sesion.md)
hizo que todo registro trajera el código enviado al correo o al teléfono, y la plantilla lo exigía
también con el código de instalación.

Se vio el 2026-11-24 al desplegar equipaggio: su servidor es el que envía el correo y los SMS de
los productos. Su primera cuenta no podía nacer hasta que su propio correo o su pasarela de SMS
funcionaran, y esos procesos todavía no corren en el VPS.

`autenticacion.md` llamaba «cuenta de administración» a quien opera la instalación, y en otra línea
decía que el administrador de una organización cliente es una cuenta común. Las dos clases no se
distinguían con claridad.

## Decisión

1. Un producto tiene dos clases de administración. El **superadministrador** opera la instalación
   y tiene `role` `superadmin`. El **administrador de cliente** administra lo suyo dentro del
   producto y es una cuenta común, `role` `user`. Las reglas de administración de
   `autenticacion.md` valen solo para el superadministrador, en su propia sección.
2. El primer superadministrador se registra con el código de instalación **en lugar del** código
   enviado al correo o al teléfono. Su correo o su teléfono quedan sin verificar.
3. Un registro con los dos códigos, o sin ninguno, responde 422.
4. Quien administra define el código de instalación en la configuración del repositorio en
   Consola, uno por repositorio, y llega al servidor por `credentials.py`. Lo que el ADR-0191
   decidió de esto pasa a la página.

## Consecuencias

- El superadministrador entra en cuanto se despliega, aunque el producto todavía no envíe correo
  ni SMS.
- El rol `admin` pasa a llamarse `superadmin`, también en la migración de la plantilla.
- Lo que antes limitaba los intentos con el código de instalación era el código enviado, con sus
  límites. Sin él, solo lo limitan la ceremonia de la passkey y el candado del registro. Cuántos
  intentos admite queda sin decidir.

## Descartado

- **Seguir exigiendo el código enviado al superadministrador.** Un producto que se envía a sí mismo
  el correo o los SMS no podría tener su primera cuenta.
- **Que el administrador de cliente tenga un rol propio.** Administrar una organización es una
  relación con ella, y lo que permite lo decide cada producto.
