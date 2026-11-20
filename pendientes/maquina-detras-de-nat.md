# Una máquina detrás de NAT

Tema pendiente: **sin decidir**. Se probó una VPS NAT de TierHive. Canone todavía no acepta una
máquina sin IPv4 propia: este archivo junta lo comprobado y propone qué cambiar.

## Estado (verificado 2026-11-20)

| Pieza | Estado |
| :--- | :--- |
| `despliegue.md` | Supone una IPv4 propia, con el 22, el 80 y el 443 abiertos |
| `plantilla/infra/Caddyfile` | No acepta PROXY protocol |
| `install.py` | Su única opción para NAT es `--turn-ip`. Sirve solo con UDP reenviado, y este NAT no lo tiene |
| consola, `Remote` de `services/ssh.py` | Arma `ssh user@host` y no permite otro puerto |
| `plantilla/receiver/backup.sh` y `backup.ps1` | Arman `ssh <app>-receiver@<servidor>` y no permiten otro puerto |
| VPS de prueba | Se probó a mano, sin `install.py` |

## Qué es una VPS NAT de TierHive

| Recurso | Qué da |
| :--- | :--- |
| IPv4 | Compartida (`158.69.255.89` en Beauharnois), con un TCP y un UDP reenviados por VPS. En la de prueba son `7511→22` y `7511→7511` |
| Red privada | Una `/24` por cliente (`10.19.47.0/24`) |
| IPv6 | Una `/64` por ubicación, gratis, y una dirección `/128` por VPS |
| Web por IPv4 | Su HAProxy, en el 80 y el 443 de la IP compartida, con dos modos (abajo) |
| Máquina | KVM, Debian 13.7 con kernel `cloud`, systemd, cloud-init, Python 3.13.5 |
| Plan probado | 1 vCPU, 2 GB, 10 GB NVMe, IOPS «Low», sin swap, unos USD 1,5 al mes |
| Reglas de uso | «DO NOT use TierHive for production workloads, critical data». Sin SLA |

El HAProxy tiene dos modos por dominio:

| Modo | Qué hace |
| :--- | :--- |
| HTTP | Abre el TLS con su propio certificado y reenvía HTTP por su red |
| TCP | Reenvía el 443 sin abrir el TLS y el 80 tal cual, a los puertos que se elijan, con un encabezado PROXY protocol v2 al frente de cada conexión. Acepta comodines. El panel lo marca como experimental y disponible en pocas regiones |

Cada dominio pide un TXT `_tierhive-validation.<host>` antes de quedar activo, y su registro A
apunta a la IP de cada región elegida.

## Hallazgos comprobados

Las pruebas se hicieron desde una PC con IPv4 e IPv6, contra la VPS de prueba.

### Red

| Prueba | Resultado |
| :--- | :--- |
| Entrada por IPv6, TCP 22, 80, 443, 3478 y 50000, y UDP 3478 | Todo llega, sin NAT ni filtro: funciona como una IP propia |
| Configuración de la IPv6 | No viene configurada: el netplan de cloud-init trae solo la IPv4. Un archivo aparte, `/etc/netplan/60-ipv6.yaml`, con la dirección y la ruta `::/0` hacia la puerta de enlace, la deja fija: sobrevive a un reinicio y cloud-init no lo toca |
| Salida por IPv4 | Sale por `158.69.255.89` |
| Salida por IPv6 | Sale por la dirección propia de la VPS |
| HTTPS de salida a GitHub, al apt de Debian y al repositorio de Caddy | Funciona |
| UDP de salida (DNS a 1.1.1.1) | Funciona. El túnel de WireGuard de «Registros» puede salir |
| TCP de salida a 25, 465 y 587 (Gmail) | Bloqueado. No afecta: el correo sale por la API HTTPS de Equipaggio |
| SSH por el 7511 de IPv4 | Inestable. Una vez se cortó durante varios minutos (`Timeout before authentication` en `sshd`) mientras el 22 por IPv6 respondía. En otra prueba, de 8 conexiones seguidas entraron 6, tardando entre 3 y 30 s; la 7.ª se cerró y la 8.ª no conectó. La causa no se conoce |
| Latencia desde México | 290 ms por IPv4 y 72 ms por IPv6, en una sola medición |

### HAProxy en modo TCP

| Prueba | Resultado |
| :--- | :--- |
| HTTPS por la IP compartida | Llega a la VPS el TLS cerrado, con el certificado propio de la VPS |
| IP del visitante | El encabezado PROXY v2 trae la IP pública real, en el 443 y en el 80 |
| Origen en la VPS | `10.0.0.57`, la dirección del HAProxy de Beauharnois en la red de TierHive |
| Chequeos de salud | Cada 2 s, al 443 y al 80, con PROXY v2 tipo `LOCAL`. Sin backend vivo, el HAProxy responde 503. Cuando el backend vuelve, la primera petición puede fallar, hasta que los chequeos lo dan por vivo |
| El 80 | Pasa por HTTP: el HAProxy reescribe los nombres de las cabeceras en minúsculas |

### Caddy 2.11.9 con PROXY protocol

Configuración probada, en el mismo puerto para los dos caminos:

```caddyfile
{
	servers {
		listener_wrappers {
			proxy_protocol {
				allow 10.0.0.57/32
				fallback_policy reject
			}
			tls
		}
	}
}

http:// {
	redir https://{host}{uri} 308
}
```

| Prueba | Resultado |
| :--- | :--- |
| HTTPS por TierHive | Caddy ve la IP real y se la pasa al servidor en `X-Forwarded-For`, con `X-Forwarded-Proto: https` |
| HTTP por TierHive | 308 a HTTPS |
| HTTPS y HTTP directos por IPv6, sin encabezado | Funcionan, con la IPv6 real del visitante |
| Un encabezado PROXY falso desde fuera de `allow`, por IPv6 | Caddy corta la conexión, en el 443 y en el 80 |
| Chequeos de salud | Solo dejan una línea en el nivel `debug`; en el nivel por defecto no queda nada |
| `allow` con `10.0.0.0/8` y con `10.0.0.57/32` | Los dos funcionan |
| Certificado de Let's Encrypt (staging) por IPv6, solo con HTTP-01 | Emitido. Caddy atiende `/.well-known/acme-challenge/` con el sitio `http://` explícito |
| Certificado de Let's Encrypt (staging) por IPv6, solo con TLS-ALPN-01, con una cuenta nueva | Emitido |
| HTTP/3 | Caddy lo sirve con esta configuración: `listener_wrappers` no toca QUIC. Se probó desde la misma VPS hacia su IPv6; que el UDP entra por IPv6 se probó aparte, en el 3478 |
| Sin el bloque `http://` | El HTTP por TierHive recibe **400**. El servidor de redirección que Caddy crea solo no recibe los `listener_wrappers` (`caddy adapt` no lo muestra) y lee el encabezado PROXY como si fuera la petición |

## Cómo quedaría una máquina NAT

| Camino | IPv6 | IPv4 |
| :--- | :--- | :--- |
| Web | AAAA a la VPS, directo, con HTTP/3 | A a la IP de la región, por el HAProxy en modo TCP, sin HTTP/3 |
| Certificado | Caddy, por ACME: Let's Encrypt valida siempre primero por IPv6 cuando el host tiene AAAA | Solo con HTTP-01 y si el IPv6 no responde a tiempo; otro error no se reintenta por IPv4 |
| SSH (consola, receptora) | 22 | El puerto reenviado, como el 7511 |
| TURN | Funciona | No funciona: no hay UDP reenviado |
| Journal a Equipaggio | Sale | Sale |

## Qué cambiaría en Canone

Cada punto lleva la opción que se recomienda. Nada de esto está decidido.

| # | Pieza | Cambio propuesto |
| :--- | :--- | :--- |
| 1 | `despliegue.md`, sección nueva «Máquina detrás de NAT» | Escribir qué necesita una máquina así: IPv6 propia; un proxy en modo TCP con PROXY protocol para IPv4; sin TURN, salvo para clientes con IPv6; y SSH por el puerto reenviado |
| 2 | `install.py --proxy <cidr>` | Escribir en el `Caddyfile` el bloque global de `proxy_protocol` con `allow <cidr>` y `fallback_policy reject`, más el sitio `http://` que redirige con 308. Sin `--proxy`, el `Caddyfile` queda como hoy |
| 3 | `despliegue.md`, «Caddy» | Decir que con `--proxy` la redirección a HTTPS es la del sitio `http://`, no la que Caddy crea sola, y por qué |
| 4 | `despliegue.md`, «Firewall» | Sin cambio: el proxy entra por el 80 y el 443, que ya están abiertos |
| 5 | Script nuevo `ipv6.py <dirección>/64 <puerta de enlace>`, de quien prepara la máquina, como `swap.py` | Escribe `/etc/netplan/60-ipv6.yaml`, con modo 600, y corre `netplan apply`. Es un archivo aparte, porque cloud-init escribe el suyo. `uninstall.py machine` lo borra |
| 6 | consola, `Remote` | Un campo `port` que agrega `-p` a `ssh` y `-P` a `scp` |
| 7 | `backup.sh` y `backup.ps1` | Sin cambio de código: el puerto va en el `~/.ssh/config` de la receptora, con un `Host` que nombra al servidor |
| 8 | `despliegue.md`, «Coturn» | Decir que `--turn-ip` no alcanza detrás de un NAT sin UDP reenviado, y que entonces TURN solo sirve por IPv6 |
| 9 | `despliegue.md`, «Cumplimiento» | Una prueba en `infra.yml` del `Caddyfile` con `--proxy`: la IP real con el encabezado desde `allow`, el corte con un encabezado de otro origen, el acceso directo sin encabezado y la redirección por HTTP |
| 10 | `stack.md` o `despliegue.md` | Que un proveedor que prohíbe producción sirve solo para máquinas con `--development` |

## Preguntas abiertas

| Pregunta | Recomendación |
| :--- | :--- |
| ¿`allow` cubre toda `10.0.0.0/8` o solo la dirección del HAProxy? | Solo la dirección observada, `10.0.0.57/32`, que se probó. No se sabe si la VPS de otro cliente alcanza la nuestra por la red de TierHive, y con `/8` podría falsificar la IP del visitante. Otra región puede tener otra dirección: `--proxy` acepta varias |
| ¿Se acepta TierHive para producción? | No, por sus propias reglas de uso. Para desarrollo y pruebas, sí |
| ¿Un dominio por host o un comodín? | Un comodín `*.<dominio>` más `<dominio>`, si el modo TCP lo acepta como dice el panel. Si no, uno por host (`<dominio>`, `app.`, `panel.`), cada uno con su TXT |

## Lo que no se probó

Nada de esto cambia el plan:

| Qué | Por qué no hace falta para decidir |
| :--- | :--- |
| ACME por el camino IPv4 de TierHive | Let's Encrypt valida primero por el IPv6, que se probó, y solo pasa al IPv4 cuando la conexión por IPv6 no responde a tiempo. Por TierHive llegan el HTTP y el TLS sin abrir, que son los que usan HTTP-01 y TLS-ALPN-01. Probarlo pide un host con solo registro A hacia TierHive, y `navetta.equipaggio.net` apunta a Cloudflare |
| Un comodín en el modo TCP | Un dominio por host funciona, como se probó con `navetta`. El comodín solo ahorra registros TXT |
| `install.py` completo en la VPS | Lo que el NAT cambia es la red. `install.py` en Debian 13 ya se prueba en `infra.yml` |

## La VPS de prueba

| Dato | Valor |
| :--- | :--- |
| Panel | `control.tierhive.com`, VPS «Beauharnois Debian 01» (`kvm20977`) |
| SSH | `ssh root@158.69.255.89 -p 7511`, o `ssh root@2a11:6c7:2600:9103::2` mientras la IPv6 siga puesta |
| Red | Privada `10.19.47.2/24`, puerta `10.19.47.1`. IPv6 `2a11:6c7:2600:9103::2/64`, puerta `2a11:6c7:2600:9103::1`, fija en `/etc/netplan/60-ipv6.yaml` |
| HAProxy | `navetta.equipaggio.net` en modo TCP, región Beauharnois, `443→:8443` y `80→:8080` hacia `10.19.47.2` |
| Cloudflare | TXT `_tierhive-validation.navetta.equipaggio.net`. El registro A de `navetta` no se tocó |
| Lo que quedó | La llave `servidor@equi-1` en `/root/.ssh/authorized_keys`. Caddy, los servidores de prueba, sus archivos y la CA local de Caddy se borraron |

## Fuentes

- [TierHive](https://tierhive.com/) y su [Acceptable Use Policy](https://tierhive.com/acceptable-use.php)
- [Caddy 2.11.9, `proxy_protocol`](https://raw.githubusercontent.com/caddyserver/caddy/v2.11.9/modules/caddyhttp/proxyprotocol/listenerwrapper.go)
- [The PROXY protocol, versions 1 & 2](https://www.haproxy.org/download/2.9/doc/proxy-protocol.txt)
- [Let's Encrypt, IPv6 Support](https://letsencrypt.org/docs/ipv6-support/)
