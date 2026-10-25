# ADR-0079 · canone no fija la operación del respaldo

- **Estado:** Aceptada
- **Fecha:** 2026-10-24
- **Alcance:** «Configuración» y «Respaldos» de
  [`plataformas/despliegue.md`](../plataformas/despliegue.md)

## Contexto

canone fija cómo se escribe el código y no corre nada ([README](../README.md)). El
[ADR-0074](0074-las-credenciales-del-respaldo-tienen-una-copia-fuera-del-servidor.md) y el punto 7
del [ADR-0078](0078-el-respaldo-lo-pide-una-receptora-y-lo-guarda-su-rest-server.md) fijaban tareas
de quien despliega, fuera del código: dónde guarda una copia de `restic_password`, y que cada mes
limpia y prueba el repositorio de la receptora.

## Decisión

1. canone no fija dónde se guarda una copia de `restic_password` fuera del servidor.
2. canone no fija la limpieza del repositorio de la receptora.

## Consecuencias

- «Configuración» deja de citar la sección 2.9 del *Secrets Management Cheat Sheet* de OWASP, que
  solo sostenía la copia.
- El servidor sigue sin poder borrar respaldos: sin una limpieza fuera de canone, el repositorio
  de la receptora crece sin límite.
