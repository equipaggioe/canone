# ADR de `canone`

Decisiones transversales. **Cada una dice a qué aplica**: la mayoría vale solo para los
repositorios que usan esa plataforma. Un repositorio que se aparta de una abre un ADR propio que
diga de qué se aparta y por qué.

Formato y reglas: [`documentacion.md`](../documentacion.md).

| # | Título | Aplica a | Estado |
|---|---|---|---|
| [0001](0001-el-estandar-vive-en-un-repositorio.md) | El estándar vive en un repositorio y los demás lo enlazan | Todos | Aceptada; la última frase del punto 2 la reemplazan ADR-0014 y ADR-0057, y el punto 4, ADR-0040 |
| [0002](0002-los-archivos-base-se-copian-y-se-verifican.md) | Los archivos base se copian y un script verifica la copia | Con `server/` | Aceptada |
| [0003](0003-enum-como-varchar-con-check.md) | Un enum se guarda como VARCHAR con CHECK | Con base de datos | Reemplazada por ADR-0013 |
| [0004](0004-geografia-con-funciones.md) | Una columna geográfica se declara con una función, no con un Annotated | Con PostGIS | Aceptada |
| [0005](0005-prefijo-api-al-montar.md) | El prefijo `/api` se aplica al montar, y la ruta no lleva versión | Con FastAPI | Reemplazada por ADR-0027 |
| [0006](0006-dependencias-con-pyproject-y-uv.md) | Las dependencias de Python se declaran en `pyproject.toml` con `uv` | Con Python | Aceptada; el punto 3, en lo que toca a `mypy`, lo reemplaza ADR-0025 |
| [0007](0007-adapter-static.md) | Toda superficie web usa `adapter-static` | Con SvelteKit | Reemplazada; el punto 1 lo reemplaza ADR-0039, y los puntos 2 y 3 se descartan |
| [0008](0008-un-sobre-unico-de-evento-y-el-catalogo-es-del-repositorio.md) | Lo que pasa se registra en un sobre único, y el catálogo es de cada repositorio | Con `server/` | Aceptada, salvo la mitad del punto 6 sobre la API, que sigue en propuesta; el punto 3 lo reemplaza ADR-0038, y los puntos 1, 2, 4, 7 y 8 y la mitad del punto 6 sobre la transacción, ADR-0058 |
| [0009](0009-el-login-no-delata-cuentas-y-el-bloqueo-vive-en-la-base.md) | El login no delata cuentas por tiempo y el bloqueo vive en una tabla | Con autenticación | Reemplazada por ADR-0038 |
| [0010](0010-la-sesion-es-estado-vivo-y-la-historia-esta-en-los-eventos.md) | La tabla de sesiones es estado vivo, no historia | Con autenticación | Aceptada; el punto 3, en lo que revoca, lo reemplaza ADR-0038, y la gracia del punto 6, ADR-0042 |
| [0011](0011-la-pasada-es-una-funcion-y-el-disparador-va-aparte.md) | La pasada periódica es una función, y el disparador va aparte | Con `server/` | Reemplazada por ADR-0043 |
| [0012](0012-el-prefijo-api-v1-se-aplica-al-montar.md) | El prefijo `/api/v1` se aplica al montar | Con FastAPI | Rechazada por ADR-0027 |
| [0013](0013-un-enum-hereda-de-strenum-y-se-guarda-como-text-con-check.md) | Un enum hereda de `StrEnum` y se guarda como `text` con CHECK | Con base de datos | Aceptada |
| [0014](0014-una-pagina-se-escribe-desde-la-recomendacion-oficial.md) | Una página de plataforma se escribe desde la recomendación oficial, no desde el código | `plataformas/` | Reemplazada por ADR-0016 |
| [0015](0015-el-sobre-de-error-sigue-el-rfc-9457.md) | El sobre de error sigue el RFC 9457 | Con `server/` y sus clientes | Aceptada; el punto 3 lo reemplaza ADR-0026 |
| [0016](0016-una-pagina-es-un-catalogo-de-convenciones-que-sale-de-la-recomendacion-oficial.md) | Una página de plataforma es un catálogo de convenciones que sale de la recomendación oficial | `plataformas/` | Reemplazada por ADR-0018 |
| [0017](0017-la-marca-vive-en-brand.md) | El logo y los colores del producto viven en `brand/` | Todos | Aceptada |
| [0018](0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md) | Una página se revisa contra la copia de sus estándares y solo dice lo que elige, endurece o no cubren | `plataformas/` | Aceptada; los puntos 2, 3, 4, 5 y 9 los reemplaza ADR-0030, y el punto 6, en lo que deja sin efecto, ADR-0056 |
| [0019](0019-el-ci-corre-cada-semana-aunque-no-haya-commits.md) | El CI corre cada semana aunque no haya commits | Todos | Aceptada |
| [0020](0020-un-monto-se-guarda-como-numeric-sin-escala-junto-al-codigo-iso-4217-de-su-moneda.md) | Un monto se guarda como `numeric` sin escala, junto al código ISO 4217 de su moneda | Con montos | Reemplazada por ADR-0023 |
| [0021](0021-un-monto-viaja-como-objeto-con-el-monto-en-cadena-y-los-clientes-no-calculan-con-el.md) | Un monto viaja como objeto con el monto en cadena, y los clientes no calculan con él | Con montos, en el servidor y sus clientes | Aceptada |
| [0022](0022-donde-vive-el-tipo-money-que-valida-los-decimales-de-un-monto.md) | Dónde vive el tipo `Money` que valida los decimales de un monto | Con montos | Reemplazada por ADR-0023 |
| [0023](0023-un-monto-se-guarda-como-numeric-sin-escala-y-sus-decimales-los-decide-cada-repositorio.md) | Un monto se guarda como `numeric` sin escala, y los decimales que admite los decide cada repositorio | Con montos | Aceptada |
| [0024](0024-la-clave-primaria-se-elige-por-lo-que-guarda-la-tabla.md) | La clave primaria se elige por lo que guarda la tabla: un código estándar, una identity o un uuid | Con base de datos | Aceptada |
| [0025](0025-los-tipos-los-revisa-pyrefly-en-modo-strict.md) | Los tipos los revisa Pyrefly en modo strict | Con Python | Aceptada |
| [0026](0026-el-type-de-un-problema-es-un-uri-https-fijo.md) | El `type` de un problema es un URI `https` fijo, y la validación tiene su propio tipo | Con `server/` y sus clientes | Aceptada; el punto 1 lo reemplaza ADR-0037, y el 2, ADR-0033 |
| [0027](0027-el-prefijo-api-va-sin-version-en-un-apirouter-de-main.md) | El prefijo `/api` va sin versión, en un `APIRouter` de `main.py` | Con FastAPI | Aceptada |
| [0028](0028-una-pagina-esta-completa-cuando-sus-estandares-cubren-lo-que-hay-que-decidir.md) | Una página está completa cuando sus estándares cubren lo que hay que decidir | `plataformas/` | Aceptada; el punto 1 lo reemplaza ADR-0031 |
| [0029](0029-las-secciones-de-una-pagina-van-en-bloques-fijos-y-los-temas-en-orden-alfabetico.md) | Las secciones de una página van en bloques fijos, y los temas en orden alfabético | `plataformas/` | Aceptada |
| [0030](0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md) | Una página cita lo que adopta en su mayoría, y lo demás es regla propia | `plataformas/` | Aceptada; el punto 4 lo reemplaza ADR-0056, y el punto 3, ADR-0063 |
| [0031](0031-una-revision-empieza-por-lo-que-la-tecnologia-obliga-a-decidir.md) | Una revisión empieza por lo que la tecnología obliga a decidir | `plataformas/` | Aceptada |
| [0032](0032-una-guia-de-una-organizacion-se-cita-si-se-escribio-para-que-otros-la-adopten.md) | Una guía de una organización se cita si se escribió para que otros la adopten | `plataformas/` y `fuentes/` | Reemplazada por ADR-0063 |
| [0033](0033-un-modulo-propio-para-lo-que-se-usa-en-varias-partes-de-la-app.md) | Un módulo propio para lo que se usa en varias partes de la app | Con FastAPI | Aceptada |
| [0034](0034-la-paginacion-es-por-cursor-con-reglas-propias.md) | La paginación es por cursor, con reglas propias | Con `server/` y sus clientes | Reemplazada por ADR-0053 |
| [0035](0035-una-lista-con-numeros-de-pagina-se-pagina-por-page-y-devuelve-el-total.md) | Una lista con números de página se pagina por `page` y devuelve el total | Con `server/` y sus clientes | Reemplazada por ADR-0053 |
| [0036](0036-el-almacen-en-memoria-es-valkey.md) | El almacén en memoria de todas las piezas es Valkey | Con un almacén en memoria | Aceptada |
| [0037](0037-la-uri-de-cada-tipo-de-problema-sirve-su-documentacion-bajo-api.md) | La URI de cada tipo de problema sirve su documentación, bajo `/api` | Con `server/` y sus clientes | Aceptada |
| [0038](0038-el-login-sigue-a-owasp-y-el-conteo-de-intentos-fallidos-vive-en-valkey.md) | El login sigue a OWASP, y el conteo de intentos fallidos vive en Valkey | Con autenticación | Reemplazada por ADR-0044 |
| [0039](0039-las-paginas-publicas-se-prerenderizan-y-las-que-piden-sesion-salen-del-fallback.md) | Las páginas públicas se prerenderizan, y las que piden sesión salen del `fallback` | Con SvelteKit | Aceptada |
| [0040](0040-el-claude-md-global-guarda-solo-lo-que-es-para-claude.md) | `~/.claude/CLAUDE.md` guarda solo lo que es para Claude, y enlaza canone para el método | Todos | Aceptada |
| [0041](0041-una-tarea-periodica-se-dispara-desde-la-pieza-y-su-interruptor-es-obligatorio.md) | Una tarea periódica se dispara desde la pieza, y su interruptor es un campo obligatorio | Con `server/` | Reemplazada por ADR-0043 |
| [0042](0042-una-sesion-vencida-se-borra-sin-gracia.md) | Una sesión vencida se borra sin gracia | Con autenticación | Aceptada |
| [0043](0043-una-tarea-periodica-la-dispara-un-timer-de-systemd.md) | Una tarea periódica la dispara un timer de systemd | Con `server/` | Aceptada |
| [0044](0044-el-bloqueo-cuenta-en-una-ventana-y-el-titular-lo-ve-en-la-app.md) | El bloqueo cuenta los intentos en una ventana, y el titular lo ve en la app | Con autenticación | Aceptada; el punto 1 lo reemplaza ADR-0045; los puntos 2 y 3, ADR-0067, y el punto 6, ADR-0060 |
| [0045](0045-el-login-y-las-contrasenas-siguen-el-nivel-1-de-asvs.md) | El login y las contraseñas siguen el nivel 1 de ASVS | Con autenticación | Aceptada; los puntos 1, 2 y 3 los reemplaza ADR-0067 |
| [0046](0046-la-contrasena-se-restablece-con-un-codigo-por-correo-o-por-sms.md) | La contraseña se restablece con un código por correo o por SMS | Con autenticación | Aceptada |
| [0047](0047-el-titular-levanta-el-bloqueo-desde-una-sesion-abierta.md) | El titular levanta el bloqueo desde una sesión abierta | Con autenticación | Aceptada; el punto 2 lo reemplaza ADR-0067 |
| [0048](0048-una-app-flutter-usa-riverpod-go-router-dio-y-freezed.md) | Una app Flutter usa Riverpod, go_router, Dio y Freezed | Con Flutter | Propuesta |
| [0049](0049-la-ubicacion-en-segundo-plano-de-una-app-flutter-usa-geolocator-y-native-geofence.md) | La ubicación en segundo plano de una app Flutter usa geolocator con servicio en primer plano y native_geofence | Con Flutter | Propuesta |
| [0050](0050-un-monto-entra-solo-como-cadena-y-sale-sin-exponente.md) | Un monto entra solo como cadena y sale sin exponente | Con montos, en el servidor | Aceptada |
| [0051](0051-un-tutorial-no-se-cita-y-lo-que-se-toma-de-el-es-regla-propia.md) | Un tutorial no se cita, y lo que se toma de él es regla propia | `plataformas/` y `fuentes/` | Aceptada |
| [0052](0052-el-openapi-se-versiona-y-de-el-generan-sus-modelos-todos-los-clientes.md) | El OpenAPI se versiona, y de él generan sus modelos todos los clientes | Con `server/` y sus clientes | Aceptada |
| [0053](0053-la-paginacion-sigue-a-aip-158-y-los-numeros-de-pagina-usan-skip.md) | La paginación sigue a AIP-158, y los números de página usan `skip` | Con `server/` y sus clientes | Aceptada |
| [0054](0054-las-passkeys-son-un-contrato-de-transversal-y-una-app-usa-la-api-de-su-sistema.md) | Las passkeys son un contrato de transversal, y una app usa la API de su sistema | Con passkeys, en el servidor y sus clientes | Aceptada |
| [0055](0055-el-cliente-de-una-web-sveltekit-se-genera-con-openapi-typescript-y-llama-con-openapi-fetch.md) | El cliente de una web SvelteKit se genera con openapi-typescript y llama con openapi-fetch | Con SvelteKit | Aceptada |
| [0056](0056-una-regla-es-lo-que-escribe-la-pagina-y-lo-que-adopta-una-fuente-es-una-convencion.md) | Una regla es lo que escribe la página, y lo que adopta una fuente es una convención | `plataformas/` y `fuentes/` | Aceptada; el punto 4 lo reemplaza ADR-0063 |
| [0057](0057-una-pagina-no-espera-a-que-un-repositorio-use-la-tecnologia.md) | Una página no espera a que un repositorio use la tecnología | `plataformas/` | Aceptada |
| [0058](0058-los-eventos-se-nombran-con-el-vocabulario-de-owasp-y-un-cambio-de-fila-es-un-evento.md) | Los eventos se nombran con el vocabulario de OWASP, y un cambio de fila es un evento | Con `server/` | Aceptada; la purga del punto 11 la reemplaza ADR-0080 |
| [0059](0059-un-recurso-que-crea-el-usuario-se-crea-por-put-y-es-un-contrato-de-transversal.md) | Un recurso que crea el usuario se crea por `PUT`, y es un contrato de transversal | Con `server/` y sus clientes | Aceptada, salvo el punto 2, que sigue en propuesta |
| [0060](0060-la-web-presenta-la-sesion-con-una-cookie-opaca-y-una-app-con-un-jwt-y-un-refresco-rotado.md) | La web presenta la sesión con una cookie opaca, y una app con un JWT y un refresco rotado | Con `server/` y sus clientes | Aceptada |
| [0061](0061-las-trazas-salen-de-la-telemetria-de-fastapi-y-el-cliente-muestra-el-traceid.md) | Las trazas salen de la telemetría de FastAPI, y el cliente muestra el `traceId` | Con `server/` y sus clientes | Aceptada |
| [0062](0062-los-colores-de-un-producto-salen-de-brand-tokens-en-dtcg-y-un-generador-arma-el-esquema-de-cada-cliente.md) | Los colores de un producto salen de `brand/tokens/` en DTCG, y un generador arma el esquema de cada cliente | Con clientes | Aceptada, salvo los puntos 7, 8 y 9, que siguen en propuesta |
| [0063](0063-una-fuente-cumple-siete-requisitos-y-su-texto-se-lee-al-escribir-codigo.md) | Una fuente cumple siete requisitos, y su texto se lee al escribir código | `plataformas/` y `fuentes/` | Aceptada; el requisito «con licencia» del punto 1 lo quita ADR-0065, y «fija» lo reemplaza ADR-0066 |
| [0064](0064-una-revision-da-un-veredicto-con-evidencia-sobre-cada-regla-fuente-y-fila.md) | Una revisión da un veredicto con evidencia sobre cada regla, fuente y fila | `plataformas/` | Aceptada |
| [0065](0065-la-licencia-de-una-fuente-no-decide-si-se-cita.md) | La licencia de una fuente no decide si se cita | `plataformas/` y `fuentes/` | Aceptada |
| [0066](0066-una-fuente-corresponde-a-la-version-en-uso-aunque-no-tenga-fecha.md) | Una fuente corresponde a la versión en uso, aunque no tenga fecha | `plataformas/` y `fuentes/` | Aceptada |
| [0067](0067-la-autenticacion-sigue-a-nist-y-el-bloqueo-cuenta-fallos-consecutivos-con-esperas.md) | La autenticación sigue a NIST, y el bloqueo cuenta fallos consecutivos con esperas crecientes | Con autenticación | Aceptada |
| [0068](0068-una-version-se-despliega-desde-un-tag-con-un-artefacto-y-un-script.md) | Una versión se despliega desde un tag, con un artefacto y un script | Con `server/` | Aceptada |
| [0069](0069-el-servidor-se-instala-desde-plantilla-infra-y-sus-cabeceras-no-frenan-a-las-apps.md) | El servidor se instala desde `plantilla/infra/`, y sus cabeceras no frenan a las apps | Con `server/` | Aceptada; el punto 2 lo reemplaza ADR-0070, y el punto 5, ADR-0078 |
| [0070](0070-las-unidades-cargan-la-carpeta-de-credenciales-y-permissions-policy-sigue-a-owasp.md) | Las unidades cargan entera la carpeta de credenciales, y `Permissions-Policy` sigue a OWASP | Con `server/` | Aceptada |
| [0071](0071-cada-app-tiene-su-instancia-de-valkey-y-cada-superficie-su-host-en-caddy.md) | Cada app tiene su instancia de Valkey, y cada superficie, su host en Caddy | Con `server/` | Aceptada; el motivo del punto 1 lo reemplaza ADR-0077 |
| [0072](0072-cada-instancia-de-valkey-limita-su-memoria-y-thp-se-apaga-solo-para-valkey.md) | Cada instancia de Valkey limita su memoria, y Transparent Huge Pages se apaga solo para Valkey | Con `server/` | Aceptada |
| [0073](0073-el-ping-de-uvicorn-cierra-el-websocket-que-no-responde-y-caddy-no-lo-corta-por-tiempo.md) | El ping de Uvicorn cierra el WebSocket que no responde, y Caddy no lo corta por tiempo | Con `server/` | Aceptada |
| [0074](0074-las-credenciales-del-respaldo-tienen-una-copia-fuera-del-servidor.md) | Las credenciales del respaldo tienen una copia fuera del servidor | Con `server/` | Descartada por ADR-0079 |
| [0075](0075-canone-fija-el-repositorio-declara-y-consola-dispara.md) | canone fija, el repositorio declara y consola dispara | Todos | Aceptada; la primera consecuencia y el motivo de los descartes los reemplaza ADR-0077 |
| [0076](0076-lo-que-cambia-entre-despliegues-sale-de-un-solo-archivo-y-lo-demas-es-codigo.md) | Lo que cambia entre despliegues sale de un solo archivo, y lo demás es código | Con `server/` | Aceptada |
| [0077](0077-un-vps-aloja-un-solo-producto.md) | Un VPS aloja un solo producto | Con `server/` | Aceptada |
| [0078](0078-el-respaldo-lo-pide-una-receptora-y-lo-guarda-su-rest-server.md) | El respaldo lo pide una receptora, y lo guarda su `rest-server` | Con `server/` | Aceptada; el punto 7 lo reemplaza ADR-0079 |
| [0079](0079-canone-no-fija-la-operacion-del-respaldo.md) | canone no fija la operación del respaldo | Con `server/` | Aceptada |
| [0080](0080-la-purga-de-event-log-es-una-funcion-y-una-ruta-de-salud-dice-que-alertar.md) | La purga de `event_log` es una función, y una ruta de salud dice qué alertar | Con `server/` | Aceptada; los puntos 3 y 4 los reemplaza ADR-0081 |
| [0081](0081-la-purga-de-event-log-la-corre-el-dueno-del-esquema.md) | La purga de `event_log` la corre el dueño del esquema | Con `server/` | Aceptada |
| [0082](0082-la-ruta-de-salud-dice-cuanto-disco-queda.md) | La ruta de salud dice cuánto disco queda | Con `server/` | Aceptada |
| [0083](0083-la-base-y-sus-roles-los-crea-install-py-y-el-servidor-entra-por-peer.md) | La base y sus roles los crea `install.py`, y el servidor entra por `peer` | Con `server/` | Aceptada |
| [0084](0084-ssh-solo-acepta-llaves-y-root-no-entra.md) | `ssh` solo acepta llaves, y `root` no entra | Con `server/` | Aceptada |
