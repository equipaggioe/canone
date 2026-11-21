# ADR

El porqué de lo que escriben las páginas y los README de Canone, que son lo que rige. «Aplica a» dice qué piezas toca cada decisión.

Formato y reglas: [documentacion.md](../documentacion.md).

| # | Título | Aplica a |
| :--- | :--- | :--- |
| [0001](0001-el-estandar-vive-en-un-repositorio.md) | El estándar vive en un repositorio y los demás lo enlazan | Todos |
| [0002](0002-los-archivos-base-se-copian-y-se-verifican.md) | Los archivos base se copian y un script verifica la copia | Con `server/` |
| [0003](0003-enum-como-varchar-con-check.md) | Un enum se guarda como VARCHAR con CHECK | Con base de datos |
| [0004](0004-geografia-con-funciones.md) | Una columna geográfica se declara con una función, no con un Annotated | Con PostGIS |
| [0005](0005-prefijo-api-al-montar.md) | El prefijo `/api` se aplica al montar, y la ruta no lleva versión | Con FastAPI |
| [0006](0006-dependencias-con-pyproject-y-uv.md) | Las dependencias de Python se declaran en `pyproject.toml` con `uv` | Con Python |
| [0007](0007-adapter-static.md) | Toda superficie web usa `adapter-static` | Con SvelteKit |
| [0008](0008-un-sobre-unico-de-evento-y-el-catalogo-es-del-repositorio.md) | Lo que pasa se registra en un sobre único, y el catálogo es de cada repositorio | Con `server/` |
| [0009](0009-el-login-no-delata-cuentas-y-el-bloqueo-vive-en-la-base.md) | El login no delata cuentas por tiempo y el bloqueo vive en una tabla | Con autenticación |
| [0010](0010-la-sesion-es-estado-vivo-y-la-historia-esta-en-los-eventos.md) | La tabla de sesiones es estado vivo, no historia | Con autenticación |
| [0011](0011-la-pasada-es-una-funcion-y-el-disparador-va-aparte.md) | La pasada periódica es una función, y el disparador va aparte | Con `server/` |
| [0012](0012-el-prefijo-api-v1-se-aplica-al-montar.md) | El prefijo `/api/v1` se aplica al montar | Con FastAPI |
| [0013](0013-un-enum-hereda-de-strenum-y-se-guarda-como-text-con-check.md) | Un enum hereda de `StrEnum` y se guarda como `text` con CHECK | Con base de datos |
| [0014](0014-una-pagina-se-escribe-desde-la-recomendacion-oficial.md) | Una página de plataforma se escribe desde la recomendación oficial, no desde el código | `plataformas/` |
| [0015](0015-el-sobre-de-error-sigue-el-rfc-9457.md) | El sobre de error sigue el RFC 9457 | Con `server/` y sus clientes |
| [0016](0016-una-pagina-es-un-catalogo-de-convenciones-que-sale-de-la-recomendacion-oficial.md) | Una página de plataforma es un catálogo de convenciones que sale de la recomendación oficial | `plataformas/` |
| [0017](0017-la-marca-vive-en-brand.md) | El logo y los colores del producto viven en `brand/` | Todos |
| [0018](0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md) | Una página se revisa contra la copia de sus estándares y solo dice lo que elige, endurece o no cubren | `plataformas/` |
| [0019](0019-el-ci-corre-cada-semana-aunque-no-haya-commits.md) | El CI corre cada semana aunque no haya commits | Todos |
| [0020](0020-un-monto-se-guarda-como-numeric-sin-escala-junto-al-codigo-iso-4217-de-su-moneda.md) | Un monto se guarda como `numeric` sin escala, junto al código ISO 4217 de su moneda | Con montos |
| [0021](0021-un-monto-viaja-como-objeto-con-el-monto-en-cadena-y-los-clientes-no-calculan-con-el.md) | Un monto viaja como objeto con el monto en cadena, y los clientes no calculan con él | Con montos, en el servidor y sus clientes |
| [0022](0022-donde-vive-el-tipo-money-que-valida-los-decimales-de-un-monto.md) | Dónde vive el tipo `Money` que valida los decimales de un monto | Con montos |
| [0023](0023-un-monto-se-guarda-como-numeric-sin-escala-y-sus-decimales-los-decide-cada-repositorio.md) | Un monto se guarda como `numeric` sin escala, y los decimales que admite los decide cada repositorio | Con montos |
| [0024](0024-la-clave-primaria-se-elige-por-lo-que-guarda-la-tabla.md) | La clave primaria se elige por lo que guarda la tabla: un código estándar, una identity o un uuid | Con base de datos |
| [0025](0025-los-tipos-los-revisa-pyrefly-en-modo-strict.md) | Los tipos los revisa Pyrefly en modo strict | Con Python |
| [0026](0026-el-type-de-un-problema-es-un-uri-https-fijo.md) | El `type` de un problema es un URI `https` fijo, y la validación tiene su propio tipo | Con `server/` y sus clientes |
| [0027](0027-el-prefijo-api-va-sin-version-en-un-apirouter-de-main.md) | El prefijo `/api` va sin versión, en un `APIRouter` de `main.py` | Con FastAPI |
| [0028](0028-una-pagina-esta-completa-cuando-sus-estandares-cubren-lo-que-hay-que-decidir.md) | Una página está completa cuando sus estándares cubren lo que hay que decidir | `plataformas/` |
| [0029](0029-las-secciones-de-una-pagina-van-en-bloques-fijos-y-los-temas-en-orden-alfabetico.md) | Las secciones de una página van en bloques fijos, y los temas en orden alfabético | `plataformas/` |
| [0030](0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md) | Una página cita lo que adopta en su mayoría, y lo demás es regla propia | `plataformas/` |
| [0031](0031-una-revision-empieza-por-lo-que-la-tecnologia-obliga-a-decidir.md) | Una revisión empieza por lo que la tecnología obliga a decidir | `plataformas/` |
| [0032](0032-una-guia-de-una-organizacion-se-cita-si-se-escribio-para-que-otros-la-adopten.md) | Una guía de una organización se cita si se escribió para que otros la adopten | `plataformas/` y `fuentes/` |
| [0033](0033-un-modulo-propio-para-lo-que-se-usa-en-varias-partes-de-la-app.md) | Un módulo propio para lo que se usa en varias partes de la app | Con FastAPI |
| [0034](0034-la-paginacion-es-por-cursor-con-reglas-propias.md) | La paginación es por cursor, con reglas propias | Con `server/` y sus clientes |
| [0035](0035-una-lista-con-numeros-de-pagina-se-pagina-por-page-y-devuelve-el-total.md) | Una lista con números de página se pagina por `page` y devuelve el total | Con `server/` y sus clientes |
| [0036](0036-el-almacen-en-memoria-es-valkey.md) | El almacén en memoria de todas las piezas es Valkey | Con un almacén en memoria |
| [0037](0037-la-uri-de-cada-tipo-de-problema-sirve-su-documentacion-bajo-api.md) | La URI de cada tipo de problema sirve su documentación, bajo `/api` | Con `server/` y sus clientes |
| [0038](0038-el-login-sigue-a-owasp-y-el-conteo-de-intentos-fallidos-vive-en-valkey.md) | El login sigue a OWASP, y el conteo de intentos fallidos vive en Valkey | Con autenticación |
| [0039](0039-las-paginas-publicas-se-prerenderizan-y-las-que-piden-sesion-salen-del-fallback.md) | Las páginas públicas se prerenderizan, y las que piden sesión salen del `fallback` | Con SvelteKit |
| [0040](0040-el-claude-md-global-guarda-solo-lo-que-es-para-claude.md) | `~/.claude/CLAUDE.md` guarda solo lo que es para Claude, y enlaza Canone para el método | Todos |
| [0041](0041-una-tarea-periodica-se-dispara-desde-la-pieza-y-su-interruptor-es-obligatorio.md) | Una tarea periódica se dispara desde la pieza, y su interruptor es un campo obligatorio | Con `server/` |
| [0042](0042-una-sesion-vencida-se-borra-sin-gracia.md) | Una sesión vencida se borra sin gracia | Con autenticación |
| [0043](0043-una-tarea-periodica-la-dispara-un-timer-de-systemd.md) | Una tarea periódica la dispara un timer de systemd | Con `server/` |
| [0044](0044-el-bloqueo-cuenta-en-una-ventana-y-el-titular-lo-ve-en-la-app.md) | El bloqueo cuenta los intentos en una ventana, y el titular lo ve en la app | Con autenticación |
| [0045](0045-el-login-y-las-contrasenas-siguen-el-nivel-1-de-asvs.md) | El login y las contraseñas siguen el nivel 1 de ASVS | Con autenticación |
| [0046](0046-la-contrasena-se-restablece-con-un-codigo-por-correo-o-por-sms.md) | La contraseña se restablece con un código por correo o por SMS | Con autenticación |
| [0047](0047-el-titular-levanta-el-bloqueo-desde-una-sesion-abierta.md) | El titular levanta el bloqueo desde una sesión abierta | Con autenticación |
| [0048](0048-una-app-flutter-usa-riverpod-go-router-dio-y-freezed.md) | Una app Flutter usa Riverpod, go_router, Dio y Freezed | Con Flutter |
| [0049](0049-la-ubicacion-en-segundo-plano-de-una-app-flutter-usa-geolocator-y-native-geofence.md) | La ubicación en segundo plano de una app Flutter usa geolocator con servicio en primer plano y native_geofence | Con Flutter |
| [0050](0050-un-monto-entra-solo-como-cadena-y-sale-sin-exponente.md) | Un monto entra solo como cadena y sale sin exponente | Con montos, en el servidor |
| [0051](0051-un-tutorial-no-se-cita-y-lo-que-se-toma-de-el-es-regla-propia.md) | Un tutorial no se cita, y lo que se toma de él es regla propia | `plataformas/` y `fuentes/` |
| [0052](0052-el-openapi-se-versiona-y-de-el-generan-sus-modelos-todos-los-clientes.md) | El OpenAPI se versiona, y de él generan sus modelos todos los clientes | Con `server/` y sus clientes |
| [0053](0053-la-paginacion-sigue-a-aip-158-y-los-numeros-de-pagina-usan-skip.md) | La paginación sigue a AIP-158, y los números de página usan `skip` | Con `server/` y sus clientes |
| [0054](0054-las-passkeys-son-un-contrato-de-transversal-y-una-app-usa-la-api-de-su-sistema.md) | Las passkeys son un contrato de transversal, y una app usa la API de su sistema | Con passkeys, en el servidor y sus clientes |
| [0055](0055-el-cliente-de-una-web-sveltekit-se-genera-con-openapi-typescript-y-llama-con-openapi-fetch.md) | El cliente de una web SvelteKit se genera con openapi-typescript y llama con openapi-fetch | Con SvelteKit |
| [0056](0056-una-regla-es-lo-que-escribe-la-pagina-y-lo-que-adopta-una-fuente-es-una-convencion.md) | Una regla es lo que escribe la página, y lo que adopta una fuente es una convención | `plataformas/` y `fuentes/` |
| [0057](0057-una-pagina-no-espera-a-que-un-repositorio-use-la-tecnologia.md) | Una página no espera a que un repositorio use la tecnología | `plataformas/` |
| [0058](0058-los-eventos-se-nombran-con-el-vocabulario-de-owasp-y-un-cambio-de-fila-es-un-evento.md) | Los eventos se nombran con el vocabulario de OWASP, y un cambio de fila es un evento | Con `server/` |
| [0059](0059-un-recurso-que-crea-el-usuario-se-crea-por-put-y-es-un-contrato-de-transversal.md) | Un recurso que crea el usuario se crea por `PUT`, y es un contrato de transversal | Con `server/` y sus clientes |
| [0060](0060-la-web-presenta-la-sesion-con-una-cookie-opaca-y-una-app-con-un-jwt-y-un-refresco-rotado.md) | La web presenta la sesión con una cookie opaca, y una app con un JWT y un refresco rotado | Con `server/` y sus clientes |
| [0061](0061-las-trazas-salen-de-la-telemetria-de-fastapi-y-el-cliente-muestra-el-traceid.md) | Las trazas salen de la telemetría de FastAPI, y el cliente muestra el `traceId` | Con `server/` y sus clientes |
| [0062](0062-los-colores-de-un-producto-salen-de-brand-tokens-en-dtcg-y-un-generador-arma-el-esquema-de-cada-cliente.md) | Los colores de un producto salen de `brand/tokens/` en DTCG, y un generador arma el esquema de cada cliente | Con clientes |
| [0063](0063-una-fuente-cumple-siete-requisitos-y-su-texto-se-lee-al-escribir-codigo.md) | Una fuente cumple siete requisitos, y su texto se lee al escribir código | `plataformas/` y `fuentes/` |
| [0064](0064-una-revision-da-un-veredicto-con-evidencia-sobre-cada-regla-fuente-y-fila.md) | Una revisión da un veredicto con evidencia sobre cada regla, fuente y fila | `plataformas/` |
| [0065](0065-la-licencia-de-una-fuente-no-decide-si-se-cita.md) | La licencia de una fuente no decide si se cita | `plataformas/` y `fuentes/` |
| [0066](0066-una-fuente-corresponde-a-la-version-en-uso-aunque-no-tenga-fecha.md) | Una fuente corresponde a la versión en uso, aunque no tenga fecha | `plataformas/` y `fuentes/` |
| [0067](0067-la-autenticacion-sigue-a-nist-y-el-bloqueo-cuenta-fallos-consecutivos-con-esperas.md) | La autenticación sigue a NIST, y el bloqueo cuenta fallos consecutivos con esperas crecientes | Con autenticación |
| [0068](0068-una-version-se-despliega-desde-un-tag-con-un-artefacto-y-un-script.md) | Una versión se despliega desde un tag, con un artefacto y un script | Con `server/` |
| [0069](0069-el-servidor-se-instala-desde-plantilla-infra-y-sus-cabeceras-no-frenan-a-las-apps.md) | El servidor se instala desde `plantilla/infra/`, y sus cabeceras no frenan a las apps | Con `server/` |
| [0070](0070-las-unidades-cargan-la-carpeta-de-credenciales-y-permissions-policy-sigue-a-owasp.md) | Las unidades cargan entera la carpeta de credenciales, y `Permissions-Policy` sigue a OWASP | Con `server/` |
| [0071](0071-cada-app-tiene-su-instancia-de-valkey-y-cada-superficie-su-host-en-caddy.md) | Cada app tiene su instancia de Valkey, y cada superficie, su host en Caddy | Con `server/` |
| [0072](0072-cada-instancia-de-valkey-limita-su-memoria-y-thp-se-apaga-solo-para-valkey.md) | Cada instancia de Valkey limita su memoria, y Transparent Huge Pages se apaga solo para Valkey | Con `server/` |
| [0073](0073-el-ping-de-uvicorn-cierra-el-websocket-que-no-responde-y-caddy-no-lo-corta-por-tiempo.md) | El ping de Uvicorn cierra el WebSocket que no responde, y Caddy no lo corta por tiempo | Con `server/` |
| [0074](0074-las-credenciales-del-respaldo-tienen-una-copia-fuera-del-servidor.md) | Las credenciales del respaldo tienen una copia fuera del servidor | Con `server/` |
| [0075](0075-canone-fija-el-repositorio-declara-y-consola-dispara.md) | Canone fija, el repositorio declara y consola dispara | Todos |
| [0076](0076-lo-que-cambia-entre-despliegues-sale-de-un-solo-archivo-y-lo-demas-es-codigo.md) | Lo que cambia entre despliegues sale de un solo archivo, y lo demás es código | Con `server/` |
| [0077](0077-un-vps-aloja-un-solo-producto.md) | Un VPS aloja un solo producto | Con `server/` |
| [0078](0078-el-respaldo-lo-pide-una-receptora-y-lo-guarda-su-rest-server.md) | El respaldo lo pide una receptora, y lo guarda su `rest-server` | Con `server/` |
| [0079](0079-canone-no-fija-la-operacion-del-respaldo.md) | Canone no fija la operación del respaldo | Con `server/` |
| [0080](0080-la-purga-de-event-log-es-una-funcion-y-una-ruta-de-salud-dice-que-alertar.md) | La purga de `event_log` es una función, y una ruta de salud dice qué alertar | Con `server/` |
| [0081](0081-la-purga-de-event-log-la-corre-el-dueno-del-esquema.md) | La purga de `event_log` la corre el dueño del esquema | Con `server/` |
| [0082](0082-la-ruta-de-salud-dice-cuanto-disco-queda.md) | La ruta de salud dice cuánto disco queda | Con `server/` |
| [0083](0083-la-base-y-sus-roles-los-crea-install-py-y-el-servidor-entra-por-peer.md) | La base y sus roles los crea `install.py`, y el servidor entra por `peer` | Con `server/` |
| [0084](0084-ssh-solo-acepta-llaves-y-root-no-entra.md) | `ssh` solo acepta llaves, y `root` no entra | Con `server/` |
| [0085](0085-el-dueno-del-esquema-entra-por-peer-con-su-cuenta-y-corre-el-volcado.md) | El dueño del esquema entra por `peer` con su cuenta, y corre el volcado | Con `server/` |
| [0086](0086-las-pruebas-corren-con-los-permisos-del-servidor-y-las-migraciones-con-el-dueno.md) | Las pruebas corren con los permisos del servidor, y las migraciones con el dueño | Con `server/` |
| [0087](0087-la-cuenta-que-administra-no-es-una-cuenta-de-la-app.md) | La cuenta que administra no es una cuenta de la app | Con `server/` |
| [0088](0088-gradle-agp-y-kotlin-tienen-una-sola-version-en-android-y-flutter.md) | Gradle, AGP y Kotlin tienen una sola versión en Android y en Flutter | Con Android o Flutter |
| [0089](0089-playwright-tiene-una-sola-version-exacta-en-todos-los-repositorios.md) | Playwright tiene una sola versión exacta en todos los repositorios | Con Playwright |
| [0090](0090-la-maquina-es-debian-13-sus-programas-salen-de-sus-paquetes-y-uv-tiene-una-sola-version-exacta.md) | La máquina es Debian 13, sus programas salen de sus paquetes, y uv tiene una sola versión exacta | Con Python |
| [0091](0091-cada-version-crea-su-entorno-en-el-servidor-y-una-migracion-se-reconoce-por-sus-heads.md) | Cada versión crea su entorno en el servidor, y una migración se reconoce por sus heads | Con `server/` |
| [0092](0092-las-actualizaciones-de-debian-se-instalan-solas-con-unattended-upgrades.md) | Las actualizaciones de Debian se instalan solas, con unattended-upgrades | Con `server/` |
| [0093](0093-lo-que-entra-se-niega-por-defecto-con-nftables-y-lo-que-sale-no-se-filtra.md) | Lo que entra se niega por defecto con nftables, y lo que sale no se filtra | Con `server/` |
| [0094](0094-el-arbol-del-servidor-sigue-el-fhs-3-0.md) | El árbol del servidor sigue el FHS 3.0 | Con `server/` |
| [0095](0095-una-lista-de-nombres-que-toma-una-regla-no-es-una-fuente.md) | Una lista de nombres que toma una regla no es una fuente | `plataformas/` y `fuentes/` |
| [0096](0096-coturn-releva-por-udp-sin-tls-y-niega-lo-que-iana-no-marca-como-alcanzable.md) | coturn releva por UDP, sin TLS, y niega lo que IANA no marca como alcanzable | Con `server/` |
| [0097](0097-la-ruta-de-salud-dice-cuando-fue-el-ultimo-evento.md) | La ruta de salud dice cuándo fue el último evento | Con `server/` |
| [0098](0098-protection-se-cumple-con-los-permisos-y-el-respaldo-y-no-detecta-ni-audita-accesos.md) | *Protection* se cumple con los permisos y el respaldo, y no detecta cambios ni audita accesos | Con `server/` |
| [0099](0099-las-trazas-no-se-exportan-y-ninguna-variable-de-entorno-agrega-un-exportador.md) | Las trazas no se exportan, y ninguna variable de entorno agrega un exportador | Con `server/` |
| [0100](0100-los-registros-salen-a-equipaggio-el-journal-por-wireguard-y-event-log-por-una-ruta-de-salud.md) | Los registros salen a equipaggio: el journal por WireGuard, y `event_log` por una ruta de salud | Con `server/` |
| [0101](0101-el-journal-guarda-a-lo-sumo-365-dias-y-equipaggio-nota-la-maquina-que-deja-de-enviar.md) | El journal guarda a lo sumo 365 días, y equipaggio nota la máquina que deja de enviar | Con `server/` |
| [0102](0102-la-hora-la-sincroniza-systemd-timesyncd-e-install-py-falla-si-no-esta-habilitado.md) | La hora la sincroniza systemd-timesyncd, e `install.py` falla si no está habilitado | Con `server/` |
| [0103](0103-unattended-upgrades-reinicia-la-maquina-a-las-0400-cuando-una-actualizacion-lo-pide.md) | unattended-upgrades reinicia la máquina a las 04:00 cuando una actualización lo pide | Con `server/` |
| [0104](0104-las-llaves-que-firman-los-releases-las-agrega-install-py-dos-en-una-maquina-nueva.md) | Las llaves que firman los releases las agrega `install.py`, dos en una máquina nueva | Con `server/` |
| [0105](0105-las-credenciales-las-cifra-credentials-py-de-canone-y-consola-solo-se-las-pasa.md) | Las credenciales las cifra `credentials.py` de Canone, y consola solo se las pasa | Con `server/` |
| [0106](0106-deploy-py-se-instala-desde-plantilla-infra-con-los-datos-de-la-app.md) | `deploy.py` se instala desde `plantilla/infra/` con los datos de la app, y no se copia al repositorio | Con `server/` |
| [0107](0107-canone-fija-la-interfaz-de-sus-programas-y-no-la-herramienta-que-los-corre.md) | Canone fija la interfaz de sus programas, y no la herramienta que los corre | Todos |
| [0108](0108-una-fuente-se-cita-entera-o-por-entradas-y-cada-parte-rige-en-una-sola-seccion.md) | Una fuente se cita entera o por entradas, y cada parte de una fuente entera rige en una sola sección | `plataformas/` y `fuentes/` |
| [0109](0109-lo-que-una-fuente-le-pide-a-otro-no-se-reparte-y-su-unidad-es-lo-que-tiene-url-propia.md) | Lo que una fuente le pide a otro no se reparte, y su unidad es lo que tiene URL propia | `plataformas/` y `fuentes/` |
| [0110](0110-uv-lo-instala-uv-py-con-su-version-y-su-sha-256-fijos.md) | uv lo instala `uv.py`, con su versión y su SHA-256 fijos | Con `server/` |
| [0111](0111-android-lint-no-avisa-versiones-nuevas.md) | Android Lint no avisa versiones nuevas | Con Android |
| [0112](0112-sveltekit-es-la-version-3-y-se-configura-en-vite-config.md) | SvelteKit es la versión 3, y se configura en `vite.config.ts` | Con SvelteKit |
| [0113](0113-en-fuentes-solo-queda-la-lista-de-la-que-un-programa-toma-valores.md) | En `fuentes/` solo queda la lista de la que un programa de Canone toma valores | `plataformas/` y `fuentes/` |
| [0114](0114-lo-que-cumplen-juntas-varias-piezas-va-en-transversal-y-lo-demas-en-la-pagina-de-su-tecnologia.md) | Lo que cumplen juntas varias piezas va en `transversal.md`, y lo demás en la página de su tecnología | `plataformas/` |
| [0115](0115-lo-que-se-cumple-es-una-convencion-adoptada-de-una-fuente-o-propia-de-canone.md) | Lo que se cumple es una convención, adoptada de una fuente o propia de Canone | `plataformas/` y `fuentes/` |
| [0116](0116-la-seccion-tema-esta-en-desarrollo-y-no-se-implementa.md) | La sección «Tema» está en desarrollo y no se implementa | «Tema» de `plataformas/`, `plantilla/README.md` y `verificar.py` |
| [0117](0117-una-fuente-se-cita-si-evita-escribir-al-menos-tres-convenciones.md) | Una fuente se cita si evita escribir al menos tres convenciones | `plataformas/` y `fuentes/` |
| [0118](0118-cada-pagina-fija-la-version-de-sus-tecnologias-y-la-plantilla-y-las-fuentes-la-siguen.md) | Cada página fija la versión de sus tecnologías, y la plantilla y las fuentes la siguen | `plataformas/`, `plantilla/` y `fuentes/` |
| [0119](0119-lo-que-corre-en-el-servidor-usa-la-version-de-debian-13-y-lo-demas-la-ultima-estable.md) | Lo que corre en el servidor usa la versión de Debian 13, y lo demás la última estable | `plataformas/`, `plantilla/` y `scripts/verificar.py` |
| [0120](0120-una-convencion-propia-puede-enlazar-el-documento-en-el-que-se-basa.md) | Una convención propia puede enlazar el documento en el que se basa | `plataformas/README.md`, `plataformas/` y `fuentes/` |
| [0121](0121-una-fuente-citada-solo-en-algunas-secciones-se-marca-por-partes.md) | Una fuente citada solo en algunas secciones se marca «por partes» | `plataformas/README.md`, `fuentes/README.md` y `scripts/verificar.py` |
| [0122](0122-una-lista-del-equipo-lleva-una-identity-integer-y-no-smallint.md) | Una lista del equipo lleva una identity `integer`, y no `smallint` | Con base de datos |
| [0123](0123-deploy-py-vuelve-a-una-version-guardada-y-borra-la-que-no-arranco.md) | `deploy.py` vuelve a una versión guardada con sus mismas migraciones, y borra la nueva que no arrancó | Con `server/` |
| [0124](0124-una-tabla-cuyas-filas-crea-el-servidor-lleva-una-identity-bigint.md) | Una tabla cuyas filas crea el servidor lleva una identity `bigint` | Con base de datos |
| [0125](0125-un-numeric-va-sin-precision-ni-escala.md) | Un `numeric` va sin precisión ni escala | Con base de datos |
| [0126](0126-el-indice-gist-lo-crea-geoalchemy2-con-sus-alembic-helpers.md) | El índice GiST lo crea GeoAlchemy2, con sus `alembic_helpers` | Con PostGIS |
| [0127](0127-database-py-vacia-la-base-solo-en-desarrollo-y-quien-administra-la-lee-como-app-read.md) | `database.py` vacía la base solo en una máquina en desarrollo, y quien administra la lee como `<app>_read` | Con `server/` |
| [0128](0128-los-seeders-corren-en-cada-despliegue-en-la-transaccion-de-las-migraciones.md) | Los seeders corren en cada despliegue, en la transacción de las migraciones | Con `server/` |
| [0129](0129-la-pagina-escribe-cada-convencion-que-rige-y-la-adoptada-lleva-su-origen.md) | La página escribe cada convención que rige, y la adoptada lleva su origen | `plataformas/`, `fuentes/`, `principios.md` y `scripts/verificar.py` |
| [0130](0130-estandar-solo-nombra-los-documentos-de-origen-y-una-eleccion-lleva-el-origen-de-su-regla.md) | `Estándar:` solo nombra los documentos de origen, y una elección lleva el origen de su regla | `plataformas/`, `principios.md` y `scripts/verificar.py` |
| [0131](0131-los-paquetes-de-la-maquina-los-instala-packages-py.md) | Los paquetes de la máquina los instala `packages.py`, que también los nombra sin instalarlos | Con `server/` |
| [0132](0132-el-swap-lo-crea-swap-py.md) | El swap de la máquina lo crea `swap.py` | Con `server/` |
| [0133](0133-la-autenticacion-tiene-su-pagina-y-el-servidor-comprueba-aparte-lo-que-sus-bibliotecas-no-miran.md) | La autenticación tiene su página, y el servidor comprueba aparte lo que sus bibliotecas no miran | `plataformas/` y `scripts/verificar.py`, con `server/` y sus clientes |
| [0134](0134-uninstall-py-deshace-la-maquina-en-tres-niveles.md) | `uninstall.py` deshace la máquina en tres niveles: la base, la app y la máquina | Con `server/` |
| [0135](0135-authorize-py-deja-entrar-a-root-con-una-llave.md) | `authorize.py` deja entrar a `root` con una llave antes de `install.py` | Con `server/` |
| [0136](0136-el-repositorio-declara-sus-permisos-del-navegador-en-permissions.md) | El repositorio declara las funciones de `Permissions-Policy` que usa en `permissions` | Con `server/` |
| [0137](0137-la-camara-de-capturas-va-en-scripts-screenshots.md) | La cámara de capturas va en `scripts/screenshots/`, y lo que genera no se versiona | Todos |
| [0138](0138-un-fid-que-fcm-da-por-ausente-se-borra.md) | Un FID al que FCM responde `UNREGISTERED` se borra | Con `server/` |
| [0139](0139-la-app-de-android-va-a-play-y-la-descarga-directa-es-su-apk-universal.md) | La app de Android va a Play, y la descarga directa es el APK universal que Play genera | Con `mobile/` |
| [0140](0140-la-camara-de-capturas-es-de-la-herramienta-que-la-corre.md) | La cámara de capturas es de la herramienta que la corre, y canone no fija dónde va | Todos |
| [0141](0141-la-app-de-flet-genera-sus-modelos-y-se-entrega-con-los-scripts-de-flet.md) | La app de Flet genera sus modelos con datamodel-code-generator y se entrega como AAB, `setup.exe` y AppImage | Con Flet |
| [0142](0142-una-pieza-prerenderizada-responde-404-con-su-pagina.md) | Una pieza toda prerenderizada responde 404 con su página, y una carpeta sin `index.html` no es una página | Con SvelteKit |
| [0143](0143-script-src-es-self-con-los-hashes-de-sveltekit-sin-strict-dynamic.md) | `script-src` es `'self'` con los hashes de SvelteKit, sin `'strict-dynamic'` | Con SvelteKit |
| [0144](0144-vitest-corre-src-playwright-corre-tests-y-ci-corre-los-dos.md) | Vitest corre solo `src/`, Playwright solo `tests/`, y CI corre los dos | Con SvelteKit |
| [0145](0145-una-convencion-entra-por-lo-que-empeora-sin-ella.md) | Una convención entra por lo que empeora sin ella, y una revisión la rehace desde la causa | `plataformas/` |
| [0146](0146-lo-comprobado-se-registra-con-su-resultado-y-no-se-vuelve-a-probar.md) | Lo comprobado se registra con su resultado y sus versiones, y no se vuelve a probar | Todos |
| [0147](0147-una-pieza-en-java-corre-en-su-unidad-con-el-jre-de-debian.md) | Una pieza en Java corre en su unidad, con el JRE de Debian 13, y se compila con sus dependencias fijadas por SHA-256 | Con una pieza en Java |
| [0148](0148-el-stack-se-fija-en-stack-md-y-la-ruta-de-lectura-va-por-pagina.md) | El stack se fija en `stack.md`, la ruta de lectura va por página, y una fuente es la guía de un asunto | `stack.md`, `README.md`, `plataformas/`, `principios.md`, `repositorio.md` y `scripts/verificar.py` |
| [0149](0149-las-unidades-de-la-app-permiten-mbind.md) | Las unidades que corren la app permiten `mbind`, la llamada con que el OpenBLAS de numpy fija la memoria de sus hilos | Con servidor |
| [0150](0150-el-indice-de-adr-lleva-numero-y-titulo-y-aplica-a-cuando-hace-falta.md) | El índice de ADR lleva número y título, y «Aplica a» cuando hay decisiones que tocan solo algunas piezas | Todos |
| [0151](0151-una-tarea-con-otro-calendario-corre-en-su-instancia-de-task.md) | Una tarea con otro calendario corre en su instancia de `PRODUCTO-task@`, y la app lo declara en `TIMERS` | Con servidor |
| [0152](0152-el-entorno-del-servidor-se-instala-compilado-y-sin-modo-editable.md) | El entorno del servidor se instala con el bytecode compilado y sin modo editable | Con servidor |
| [0153](0153-un-script-de-sh-con-set-e-no-niega-con-exclamacion.md) | Un script de `sh` con `set -e` no niega un comando con `!` | Todos |
| [0154](0154-las-particiones-por-delante-las-crea-el-dueno-en-migrate-y-la-purga.md) | Las particiones por delante las crea el dueño del esquema, en `migrate` y en la purga | Con servidor |
| [0155](0155-caddy-sale-de-su-repositorio-apt.md) | Caddy sale de su repositorio APT, y no de los paquetes de Debian 13 | Con servidor |
| [0156](0156-una-imagen-con-varios-tamanos-es-una-carpeta-de-su-fila.md) | Una imagen que se muestra en varios tamaños se guarda una vez por tamaño, en la carpeta de su fila | Con servidor |
| [0157](0157-los-datos-de-ejemplo-entran-como-el-servidor.md) | Los datos de ejemplo entran con la cuenta del servidor y su carpeta de archivos | Con servidor |
| [0158](0158-las-teselas-son-vectoriales-de-openfreemap-y-cada-cliente-las-dibuja-con-maplibre.md) | Las teselas son vectoriales, de OpenFreeMap, y cada cliente las dibuja con MapLibre | Con mapas |
| [0159](0159-cada-cliente-comprueba-en-ci-que-declara-lo-que-importa-y-usa-lo-que-declara.md) | Cada cliente comprueba en CI que declara lo que importa y usa lo que declara | Con clientes |
| [0160](0160-el-usuario-elige-el-modo-claro-u-oscuro-en-cada-dispositivo.md) | El usuario elige el modo claro u oscuro en cada dispositivo, y «sistema» es el inicial | Con clientes |
| [0161](0161-cada-regla-queda-en-una-sola-pagina-y-plugins-deja-de-ser-una-carpeta-de-primer-nivel.md) | Cada regla queda en una sola página, y `plugins/` deja de ser una carpeta de primer nivel | Todos |
| [0162](0162-una-pagina-escribe-decisiones-y-no-como-funciona-su-tecnologia.md) | Una página escribe decisiones, y no cómo funciona su tecnología | `plataformas/` |
| [0163](0163-una-revision-recorre-el-documento-entero-y-propone-tambien-lo-que-falta.md) | Una revisión recorre el documento entero y propone también lo que falta | `plataformas/` |
| [0164](0164-lo-que-se-instala-en-la-maquina-va-en-despliegue-tambien-la-unidad-de-una-pieza.md) | Lo que se instala en la máquina va en `despliegue.md`, también la unidad de una pieza | `plataformas/` |
| [0165](0165-qt-escribe-solo-lo-que-elige-y-se-aplica.md) | `qt.md` escribe solo lo que elige, y se aplica a los repositorios | Con Qt |
| [0166](0166-flet-escribe-solo-lo-que-elige.md) | `flet.md` escribe solo lo que elige | Con Flet |
| [0167](0167-android-escribe-solo-lo-que-elige-y-cumple-los-contratos-de-red.md) | `android.md` escribe solo lo que elige, y cumple los contratos de red de `transversal.md` | Con Android |
| [0168](0168-android-traduce-errores-pagina-con-paging-y-sigue-el-idioma-por-app.md) | Android traduce los errores en la fuente de red, pagina con Paging 3 y sigue el idioma por app del sistema | Con Android |
| [0169](0169-el-stack-suma-los-paquetes-que-sus-paginas-ya-pedian-y-el-servidor-declara-uvicorn.md) | El stack suma los paquetes que sus páginas ya pedían, y el servidor declara Uvicorn sin el extra `standard` | `stack.md` |
| [0170](0170-cada-app-guarda-su-numero-de-build-en-su-manifiesto.md) | Cada app guarda su número de build en su manifiesto | Con Android, Flutter o Flet |
| [0171](0171-dependency-analysis-no-cuenta-lo-que-solo-usa-el-codigo-que-genera-hilt.md) | dependency-analysis no cuenta lo que solo usa el código que genera Hilt | Con Android |
| [0172](0172-una-tarea-que-maneja-chromium-corre-en-su-instancia-de-browser.md) | Una tarea que maneja Chromium corre en su instancia de `PRODUCTO-browser@`, con el Chromium de Debian | Con servidor |
| [0173](0173-una-pieza-en-java-se-compila-con-el-jdk-del-ci-sin-advertencias-y-el-servidor-la-prueba-corriendo.md) | Una pieza en Java se compila con el JDK del CI, sin advertencias y con google-java-format, y el servidor la prueba corriendo | Con una pieza en Java |
| [0174](0174-flet-fija-sus-transitivas-con-pip-constraint-y-construye-sin-flet-build-action.md) | Flet fija sus transitivas con `PIP_CONSTRAINT` y construye sin flet-build-action | Con Flet |
| [0175](0175-qt-y-flet-entran-con-pantallas-propias-sin-salir-al-navegador.md) | Las apps de escritorio de Qt y de Flet entran con pantallas propias, sin salir al navegador | Con Qt o Flet |
| [0176](0176-la-app-de-flet-dibuja-el-mapa-con-flet-map-y-teselas-raster.md) | La app de Flet dibuja el mapa con flet-map y teselas raster | Con Flet |
| [0177](0177-flutter-y-sveltekit-dejan-de-estar-en-desarrollo.md) | `flutter.md` y `sveltekit.md` dejan de estar en desarrollo | Con Flutter o SvelteKit |
| [0178](0178-la-interfaz-de-flet-es-declarativa.md) | La interfaz de Flet es declarativa | Con Flet |
| [0179](0179-una-app-de-flet-no-muestra-mapas.md) | Una app de Flet no muestra mapas | Con Flet |
| [0180](0180-cada-plataforma-se-escribe-como-si-hubiera-cuenta-y-cada-repositorio-elige-donde-publica.md) | Cada plataforma se escribe como si hubiera cuenta, y cada repositorio elige dónde publica | Con apps o con `desktop/` |
| [0181](0181-cubre-y-aporta-cuentan-juntas-las-paginas-de-una-misma-documentacion.md) | «Cubre» y «Aporta» cuentan juntas las páginas de una misma documentación | `plataformas/` y `fuentes/` |
| [0182](0182-flutter-traduce-los-errores-reintenta-y-autentica-en-un-solo-http-client.md) | Flutter traduce los errores, reintenta y autentica en un solo `http.Client` | Con Flutter |
| [0183](0183-windows-va-sin-firmar-y-los-canales-de-flutter-los-crea-su-application.md) | Windows va sin firmar, y los canales de Flutter los crea su `Application` | Con apps o con `desktop/` |
| [0184](0184-la-uri-de-retorno-es-https-donde-se-puede-y-cada-pieza-elige-sus-plataformas.md) | La URI de retorno es `https` donde se puede, y cada pieza elige sus plataformas | Con apps o con `desktop/` |
| [0185](0185-una-cuenta-entra-con-passkey-o-contrasena-y-cada-repositorio-elige-cuales-ofrece.md) | Una cuenta entra con passkey o con contraseña, y cada repositorio elige cuáles ofrece | Con autenticación |
| [0186](0186-lo-que-no-es-interfaz-va-en-services-y-un-servicio-externo-tiene-su-modulo-en-api.md) | Lo que no es interfaz va en `services/`, y un servicio externo tiene su módulo en `api/` | Con clientes |
| [0187](0187-flet-fija-jni-y-jni-flutter-en-el-pubspec-que-genera.md) | Flet fija `jni` y `jni_flutter` en el `pubspec.yaml` que genera | Con Flet |
| [0188](0188-verificar-comprueba-el-arbol-de-qt-y-flet-y-ruff-deja-http-solo-en-api.md) | `verificar.py` comprueba el árbol de Qt y de Flet, y ruff deja HTTP solo en `api/` | Con clientes |
| [0189](0189-lo-que-no-es-codigo-de-qt-va-en-src-app-assets.md) | Lo que no es código de una app de Qt va en `src/app/assets/` | Con `desktop/` |
| [0190](0190-la-app-de-flet-en-ios-usa-la-passkey-en-sfsafariviewcontroller.md) | La app de Flet en iOS usa la passkey en `SFSafariViewController` y recibe el retorno en un esquema propio | Con Flet |
| [0191](0191-la-primera-cuenta-de-administracion-se-registra-con-el-codigo-de-instalacion.md) | La primera cuenta de administración se registra con el código de instalación | Con autenticación |
| [0192](0192-una-app-de-qt-no-declara-el-dominio-de-su-organizacion.md) | Una app de Qt no declara el dominio de su organización | Con `desktop/` |
| [0193](0193-flet-lee-el-codigo-por-sms-con-una-extension-de-la-plantilla.md) | Flet lee el código por SMS con una extensión que copia la plantilla | Con Flet |
| [0194](0194-el-sms-sirve-para-entrar-y-el-escritorio-y-la-web-de-flutter-y-flet-tienen-passkey.md) | El SMS sirve para entrar, y el escritorio y la web de Flutter y Flet tienen passkey | Con autenticación |
| [0195](0195-un-widget-de-qt-que-flota-sobre-otros-se-ubica-sin-layout-con-su-sizehint.md) | Un widget de Qt que flota sobre otros se ubica sin layout, con el tamaño de su `sizeHint()` | Con `desktop/` |
| [0196](0196-python-escribe-solo-lo-que-dice-su-origen-y-cada-fila-nombra-lo-que-su-herramienta-hace-cumplir.md) | `python.md` escribe solo lo que dice su origen, y cada fila de Cumplimiento nombra lo que su herramienta hace cumplir | Con Python |
| [0197](0197-qt-traduce-con-translate-y-un-language-py-canonico-y-empaqueta-despues-de-los-recursos.md) | Qt traduce con `translate` y un `language.py` canónico, y empaqueta después de compilar los recursos | Con `desktop/` |
| [0198](0198-la-seccion-tema-deja-de-estar-en-desarrollo.md) | La sección «Tema» deja de estar en desarrollo | «Tema» de `plataformas/`, `plantilla/README.md` y `verificar.py` |
| [0199](0199-fastapi-cada-fila-detecta-lo-que-promete-y-el-servidor-reconecta-compara-los-server-default-y-limita-cada-subida.md) | Cada fila de `fastapi.md` detecta lo que promete, y el servidor reconecta tras un reinicio de PostgreSQL, compara los `server_default` y limita cada subida | Con `server/` |
| [0200](0200-una-fuente-que-gana-la-eleccion-reemplaza-a-la-de-su-asunto-y-los-webhooks-siguen-a-owasp.md) | Una fuente que gana la elección reemplaza a la de su asunto, y los webhooks siguen a OWASP | `plataformas/README.md` y con `server/` |
| [0201](0201-un-producto-elige-sus-temas-y-sus-modos-y-el-modo-es-otro-modificador.md) | Un producto elige sus temas y sus modos, y el modo es otro modificador | «Tema» de `plataformas/`, `plantilla/` y `verificar.py` |
| [0202](0202-postgres-escribe-solo-lo-que-dice-su-origen-postgis-deja-de-ser-fuente-y-cada-convencion-verificable-tiene-su-prueba.md) | `postgres.md` escribe solo lo que dice su origen, PostGIS deja de ser fuente y cada convención verificable tiene su prueba | `postgres.md`, `fastapi.md`, `fuentes/` y con `server/` |
| [0203](0203-una-tabla-que-amplia-otra-lleva-su-clave-foranea-como-clave-una-lista-que-se-busca-va-en-una-tabla-y-el-ci-de-canone-prueba-la-plantilla-del-servidor.md) | Una tabla que amplía otra lleva su clave foránea como clave, una lista que se busca va en una tabla, y el CI de Canone prueba la plantilla del servidor | `postgres.md`, `fastapi.md`, `fuentes/`, con `server/` y el CI de Canone |
| [0204](0204-una-columna-espacial-dice-si-lleva-indice-un-texto-sin-mayusculas-se-guarda-en-minusculas-y-un-unique-con-null-dice-si-son-duplicados.md) | Una columna espacial dice si lleva índice, un texto sin mayúsculas se guarda en minúsculas, y un `UNIQUE` con `NULL` dice si son duplicados | `postgres.md`, `fastapi.md` y con `server/` |
| [0205](0205-una-columna-timestamptz-termina-en-at-si-es-un-instante-y-en-from-o-until-si-limita-un-periodo.md) | Una columna `timestamptz` termina en `_at` si es un instante, y en `_from` o `_until` si limita un periodo | Con base de datos |
| [0206](0206-el-servidor-pasa-el-correo-a-minusculas-al-recibirlo.md) | El servidor pasa el correo a minúsculas al recibirlo | Con autenticación |
| [0207](0207-autenticacion-deja-lo-que-tiene-una-sola-forma-el-titular-cierra-sus-sesiones-y-el-flujo-del-navegador-se-liga-a-una-cookie.md) | `autenticacion.md` deja lo que tiene una sola forma, el titular cierra sus sesiones, y el flujo del navegador se liga a una cookie | `autenticacion.md`, `fastapi.md`, `fuentes/` y con autenticación |
| [0208](0208-las-contrasenas-siguen-a-asvs-v6-y-los-requisitos-de-credential-manager-dejan-de-ser-fuente.md) | Las contraseñas siguen a ASVS V6, y los requisitos de Credential Manager dejan de ser fuente | `autenticacion.md`, `android.md`, `fuentes/` y con autenticación |
