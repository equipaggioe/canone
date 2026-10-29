# ADR-0106 · deploy.py se instala desde `plantilla/infra/` con los datos de la app, y no se copia al repositorio

- **Estado:** Aceptada
- **Fecha:** 2026-10-28
- **Alcance:** «Versiones» de [`plataformas/despliegue.md`](../plataformas/despliegue.md),
  `plantilla/infra/` y `plantilla/scripts/deploy.py`

## Contexto

`plantilla/scripts/deploy.py` es un punto de partida: cada repositorio lo copia, cambia `PRODUCTO`
y `OWNER`, y ajusta `TOKEN`, `UNITS` y `DESKTOP`. Lo demás, que es casi todo el script (la firma,
las migraciones, la vuelta atrás y las cinco versiones que se conservan), es igual en todas las
apps. Cada copia puede separarse de la plantilla sin que nada lo note, como pasó con
`models/base.py`, y `infra.yml` prueba la plantilla, no las copias. Además, la primera versión no
tiene `current`, y el script se copia a mano desde el tag.

## Decisión

1. `deploy.py` pasa a `plantilla/infra/`, e `install.py` lo instala en
   `/usr/local/lib/<app>/deploy.py` con los datos de la app, igual que las unidades. Sale de
   `plantilla/scripts/` y del artefacto del release.
2. `install.py` recibe esos datos: `--owner` es el dueño del repositorio en GitHub, `--private` hace
   que el script lea el token de `<app>-deploy/github_token`, y `--desktop` nombra cada instalable
   que trae el release: `linux`, `windows` o `macos`.
3. `deploy.py` reinicia `<app>.service`, la única unidad del servidor que instala `install.py`, así
   que `UNITS` deja de ser un dato.
4. Se despliega con `sudo python3 /usr/local/lib/<app>/deploy.py <versión>`. Reemplaza el punto 3
   del [ADR-0068](0068-una-version-se-despliega-desde-un-tag-con-un-artefacto-y-un-script.md), que
   ponía el script en `scripts/` del repositorio.

## Consecuencias

- Un cambio en `deploy.py` llega a cada app al reinstalar, y `infra.yml` prueba el mismo archivo
  que corre cada servidor.
- La primera versión se despliega sin copiar nada a mano.
- Una app que agrega un instalable o pasa a ser privada vuelve a correr `install.py`.
- consola corre `deploy.py` desde la máquina, y deja de tomarlo del repositorio.

## Descartado

- **Seguir copiándolo como punto de partida:** deja una copia por repositorio que puede separarse
  de las demás, y ninguna prueba de canone corre esas copias.
- **Copiarlo como canónico y que `verificar.py` compare la copia:** los datos de la app seguirían
  en el código, y una corrección no llegaría a un servidor hasta que cada repositorio la copie y
  publique un tag.
- **Que `deploy.py` busque los instalables en el `.sha256` firmado:** un release al que le falta
  uno se desplegaría sin error, y `downloads/` seguiría sirviendo el anterior.
