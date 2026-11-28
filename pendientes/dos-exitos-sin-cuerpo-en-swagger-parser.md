# Una operación con dos éxitos sin cuerpo en el cliente de swagger_parser

Tema pendiente: **sin decidir**.

## Estado (verificado 2026-11-28)

`PUT /api/account/password` responde 201 si la cuenta no tenía contraseña y 204 si la cambia, los dos
sin cuerpo. swagger_parser 2.4.0, en su modo por defecto, acepta solo el 2xx más bajo de una
operación sin cuerpo, el 201: el cambio de una contraseña, con 204, falla en una app de Flutter con
`ClientException('HTTP 204')`. Leído en
[`dart_client_mapper.dart`](https://raw.githubusercontent.com/Carapacik/swagger_parser/2.4.0/swagger_parser/lib/src/dart/dart_client_mapper.dart):
los 2xx sin cuerpo se suman a los aceptados solo si la operación devuelve un valor. Sin confirmar con
una prueba: ningún repositorio con Flutter usa la contraseña.

## Qué hay que decidir

- Si el cambio de la contraseña responde 200 sin cuerpo, para que el 201 del [ADR-0253](../adr/0253-una-app-de-flutter-recibe-el-201-como-200-y-ese-201-viene-con-un-200-del-mismo-cuerpo.md) cubra también el caso sin cuerpo.
- O si se espera un arreglo de swagger_parser.

## Cuándo se retoma

Antes de que una app de Flutter ofrezca la contraseña.
