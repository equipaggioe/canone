# ADR-0093 · Lo que entra se niega por defecto con nftables, y lo que sale no se filtra

- **Estado:** Aceptada
- **Fecha:** 2026-10-26
- **Alcance:** «Firewall» de [`plataformas/despliegue.md`](../plataformas/despliegue.md),
  `plantilla/infra/` y `.github/workflows/infra.yml`

## Contexto

La máquina no tenía firewall: lo que no debía verse desde fuera, como el 8000 de Uvicorn o el 5432
de PostgreSQL, quedaba cerrado solo porque cada programa escucha en loopback. Un programa que
escuchara en todas las direcciones quedaba abierto a internet.

## Decisión

1. La máquina tiene firewall, y lo que entra se niega salvo lo que la regla nombra: el 22 y el 80
   por TCP, el 443 por TCP y por UDP, y los puertos de coturn con TURN.
2. Lo que sale no se filtra.
3. «Firewall» cita la sección 4.1.3, *TCP and UDP*, de NIST SP 800-41 Rev. 1, que pide
   negar por defecto lo que entra y deja más libre lo que sale.
4. El firewall es el nftables de Debian 13, con `plantilla/infra/nftables.conf`, que
   `install.py` instala en `/etc/nftables.conf` y carga.
5. ICMP entra entero, y nada pasa por la máquina hacia otra red.
6. `infra.yml` carga la regla en un namespace de red y prueba los puertos desde otro.

## Consecuencias

- Un puerto nuevo cambia `nftables.conf` y «Firewall» en el mismo commit.
- La plantilla todavía no abre los puertos de coturn: coturn no tiene plantilla.
- Comprobado en Debian 13.5 con nftables 1.1.3: `scripts/infra/nftables.sh` pasa con la plantilla,
  y falla si la regla abre el 8000, si cierra la salida o si abre el 53 por UDP en vez del 443.

## Descartado

- **La introducción de la sección 4 de SP 800-41 Rev. 1:** también niega por defecto lo que sale, y
  la app habla con dominios de terceros cuyas direcciones cambian, que nftables no puede seguir.
- **La sección 4.3 de NIST SP 800-123:** nombra el firewall de host entre los controles comunes,
  pero no decide cuál ni cómo, y remite a la SP 800-41.
- **La sección 21.2 del RFC 8656:** trata del firewall entre el cliente y TURN, no del de la
  máquina.
- **Solo el firewall del proveedor:** queda fuera de lo que instala canone, y nada lo prueba.
