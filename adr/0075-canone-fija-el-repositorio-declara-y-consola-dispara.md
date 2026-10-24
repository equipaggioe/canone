# ADR-0075 · canone fija, el repositorio declara y consola dispara

- **Estado:** Aceptada
- **Fecha:** 2026-10-23
- **Alcance:** «Quién hace qué» de [`README.md`](../README.md)

## Contexto

Con el despliegue por tag ([ADR-0068](0068-una-version-se-despliega-desde-un-tag-con-un-artefacto-y-un-script.md))
y el servidor instalado desde `plantilla/infra/` ([ADR-0069](0069-el-servidor-se-instala-desde-plantilla-infra-y-sus-cabeceras-no-frenan-a-las-apps.md)),
consola seguía generando sus propias unidades de systemd, su Caddyfile y su `.env`. Escribía los
mismos archivos que instala `install.py`: el Caddyfile de consola borraba los sitios de las demás
apps de la máquina, y su unidad pisaba la de la plantilla, que lleva sandboxing. Ningún documento
decía cuál de los tres decidía, así que la duda volvía en cada cambio.

## Decisión

1. canone fija las reglas y da las plantillas. No guarda datos de ninguna app ni corre nada.
2. El repositorio sigue las reglas, copia las plantillas que se copian y declara sus datos.
3. consola lee los datos del repositorio y dispara lo que dan las plantillas: las que se copian las
   toma del repositorio, y las que se instalan, de canone. No escribe unidades, configuración ni
   scripts propios. Lo que no tiene plantilla se agrega primero a canone.
4. Un secreto no se declara con su valor en el repositorio: el repositorio declara el campo, y el
   valor vive en `.consola/config.env`
   ([ADR-0076](0076-lo-que-cambia-entre-despliegues-sale-de-un-solo-archivo-y-lo-demas-es-codigo.md)).

## Consecuencias

- Un VPS con varias apps no depende de qué versión de consola instaló cada una: todas salen de la
  misma plantilla.
- Lo que hoy falta en canone, como la creación de los roles de Postgres o coturn, bloquea a consola
  hasta que canone tenga su regla y su plantilla.
- El puerto, el dominio y la memoria van en `.consola/config.env`, junto con lo demás que cambia
  entre despliegues.

## Descartado

- **Que consola genere la configuración del servidor:** dos fuentes del mismo archivo, que se
  pisan en una máquina compartida.
- **Que cada repositorio copie `plantilla/infra/`:** el Caddyfile y Valkey se comparten entre las
  apps de la máquina, y una copia por repositorio se separaría de las demás.
