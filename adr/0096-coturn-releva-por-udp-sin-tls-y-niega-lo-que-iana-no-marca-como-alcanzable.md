# ADR-0096 · coturn releva por UDP, sin TLS, y niega lo que IANA no marca como alcanzable

- **Estado:** Aceptada
- **Fecha:** 2026-10-27
- **Alcance:** «Coturn», «Firewall» y «Proyecto» de
  [`plataformas/despliegue.md`](../plataformas/despliegue.md), `plantilla/infra/`, `scripts/infra/`
  y `.github/workflows/infra.yml`

## Contexto

«Coturn» decía solo en qué puertos escucha y que niega relevar hacia direcciones privadas. No había
plantilla, `install.py` no lo instalaba, y el firewall del
[ADR-0093](0093-lo-que-entra-se-niega-por-defecto-con-nftables-y-lo-que-sale-no-se-filtra.md) no
abría los puertos por donde coturn releva: una llamada por TURN habría fallado.

## Decisión

1. coturn escucha solo en el 3478, por UDP y por TCP, sin TLS. Quita el 5349 de la regla anterior.
2. Releva solo por UDP, del 49152 al 65535, el rango de la sección 7.2 del RFC 8656, con
   `no-tcp-relay`, y el firewall abre esos puertos solo con TURN.
3. Una credencial tiene a lo sumo 10 asignaciones, y cada una 500 000 bytes por segundo, como pide
   la sección 21.3.1 del RFC 8656.
4. Niega relevar hacia las redes que no son de internet, y hacia las de multicast.
5. `install.py` genera el secreto la primera vez y lo conserva. Lo escribe en `/etc/turnserver.conf`,
   que lee solo el grupo `turnserver`, y como `turn_secret` en la carpeta de credenciales de la app.
   El `realm` es el dominio de la app.
6. coturn no abre su consola de administración (`no-cli`).
7. `install.py --turn` instala la configuración, abre los puertos y reinicia coturn, y falla si
   coturn no está instalado.
8. `infra.yml` levanta coturn con la plantilla y releva desde otro namespace de red.
9. Las redes que no son de internet son los bloques que los registros de direcciones
   de uso especial de IANA marcan como no alcanzables globalmente, copiados en `fuentes/iana/`, y
   `scripts/infra/peers.py` compara la plantilla con ellos.
10. `nftables.conf` incluye `/etc/nftables.d/*.nft`, y `install.py --turn` pone ahí `turn.nft`,
    que quita sin `--turn`.
11. En una máquina cuya interfaz tiene solo una dirección privada, `install.py --turn-ip <pública>`
    agrega `external-ip` a `/etc/turnserver.conf`, e `infra.yml` lo prueba detrás de un NAT.
12. La línea es `external-ip=<pública>/<privada>`, y la privada es la de la ruta por
    defecto, de `ip route get`.

## Consecuencias

- Una red que deja pasar solo TLS no llega a coturn.
- La plantilla conserva las líneas activas del `turnserver.conf` de Debian 13: `syslog`,
  `no-rfc5780`, `no-stun-backward-compatibility` y `response-origin-only-with-rfc5780`.
- `denied-peer-ip` no lleva `0.0.0.0` ni `::`: coturn 4.6.1 lee un rango con esas direcciones como
  cualquier dirección, y negaba todo. `0.0.0.0` queda dentro de `0.0.0.0/8`, y `::` coturn lo niega
  por sí mismo.
- Un bloque alcanzable dentro de uno que no lo es, como el anycast de TURN en `192.0.0.0/24`, queda
  negado con el que lo contiene.
- Comprobado en Debian 13.5 con coturn 4.6.1: `scripts/infra/coturn.sh` releva hacia una dirección
  de internet por IPv4 y por IPv6, y no hacia `10.9.1.2`, `127.0.0.1`, `0.0.0.0`, `::1` ni
  `::ffff:127.0.0.1`, ni con otro secreto, ni con 12 asignaciones de una credencial; falla si la
  plantilla quita la cuota o un bloque, o si agrega `0.0.0.0`. Con la configuración de la plantilla,
  la unidad de Debian arranca como `turnserver`, que lee el archivo, y escucha solo en el 3478.
- Comprobado detrás de un NAT de nftables, con coturn en `10.20.0.2` y `1.2.3.1` como pública: sin
  `external-ip`, dos clientes de fuera no se alcanzan, porque coturn entrega `10.20.0.2`; con
  `external-ip=1.2.3.1/10.20.0.2` se alcanzan, y con `external-ip=1.2.3.1` sola, no.
- `nftables.sh` pasa con y sin `turn.nft`, y falla si `turn.nft` abre hasta el 65000.

## Descartado

- **TLS en el 5349:** WebRTC ya cifra la llamada, y coturn necesitaría el certificado de Caddy, que
  vive en una carpeta interna suya.
- **Relevar por TCP:** WebRTC no lo pide.
- **Un secreto nuevo en cada corrida:** las credenciales ya entregadas dejarían de servir.
