# Fuentes

Copia de los textos de las fuentes que citan las páginas de [plataformas/](../plataformas/), y de las listas de las que un programa de Canone toma valores. Una página se revisa contra el texto de aquí, no de memoria. Una fuente que solo cita un ADR no se copia: el ADR la usa como argumento de su decisión, y ninguna página adopta sus convenciones.

- Cada archivo es el texto de su fuente, sin editar. Cuando la fuente es una página web, es su contenido convertido a Markdown.
- Cada archivo se descarga del tag o la rama de la versión que se usa, nunca de `main` ni de `master`. Una fuente sin versiones se descarga de un commit fijo, y su URL lleva el SHA.
- La publicación de una nueva versión no implica su adopción automática. Decidir si se incorpora corresponde al mantenimiento de Canone: requiere revisar sus cambios y determinar si justifican modificar las convenciones existentes.
- Al cambiar la versión de una tecnología, se vuelven a descargar sus fuentes.
- Para actualizar un archivo se vuelve a descargar de su fuente; `git diff` muestra qué cambió.
- Una fuente que ninguna página cita se borra.
- La columna «Cita» dice si la fuente se cita `entera` o `por entradas` ([plataformas/README.md](../plataformas/README.md#unidad-y-alcance-de-la-cita)).

| Archivo | Fuente | Cita | Nota |
| :--- | :--- | :--- | :--- |
| [python/pep-0008.rst](python/pep-0008.rst) | [origen](https://raw.githubusercontent.com/python/peps/5514795ade79a5bf6f3c08c562b02689d0a9feb2/peps/pep-0008.rst) | entera |  |
| [python/pep-0257.rst](python/pep-0257.rst) | [origen](https://raw.githubusercontent.com/python/peps/f22614f903cd50d19e5463913fde6d4a17109de0/peps/pep-0257.rst) | entera |  |
| [python/pep-0698.rst](python/pep-0698.rst) | [origen](https://raw.githubusercontent.com/python/peps/e8273d3ed3a87718778c0979a4518e07a7a87760/peps/pep-0698.rst) | entera |  |
| [python/asyncio-dev.rst](python/asyncio-dev.rst) | [origen](https://raw.githubusercontent.com/python/cpython/3.13/Doc/library/asyncio-dev.rst) | entera | Rama 3.13, la versión que usan las piezas: la de `main` nombra `InterpreterPoolExecutor`, que no existe en 3.13. |
| [python/io.rst](python/io.rst) | [origen](https://raw.githubusercontent.com/python/cpython/3.13/Doc/library/io.rst) | por entradas | Rama 3.13, la versión que usan las piezas: desde 3.15 la codificación por defecto es UTF-8 y la sección *Text Encoding* ya no recomienda indicarla. |
| [pypa/pyproject-toml.rst](pypa/pyproject-toml.rst) | [origen](https://raw.githubusercontent.com/pypa/packaging.python.org/3b98ceeae062e84ae5527f850622b057878aa11e/source/specifications/pyproject-toml.rst) | por entradas |  |
| [pypa/dependency-groups.rst](pypa/dependency-groups.rst) | [origen](https://raw.githubusercontent.com/pypa/packaging.python.org/cdb4bf7ce8de9263fc3ec9e4c46117f49c4f72c5/source/specifications/dependency-groups.rst) | por entradas |  |
| [pytest/goodpractices.rst](pytest/goodpractices.rst) | [origen](https://raw.githubusercontent.com/pytest-dev/pytest/9.2.0/doc/en/explanation/goodpractices.rst) | entera |  |
| [typing/best_practices.rst](typing/best_practices.rst) | [origen](https://raw.githubusercontent.com/python/typing/953e24d71aa6ea97f58852046fc355d11b564333/docs/reference/best_practices.rst) | entera |  |
| [typing/modernizing.rst](typing/modernizing.rst) | [origen](https://raw.githubusercontent.com/python/typing/39164cd2c5b4e2608cb8b5d2fc8af9ae6f0c0fe8/docs/guides/modernizing.rst) | entera |  |
| [sqlalchemy/asyncio.rst](sqlalchemy/asyncio.rst) | [origen](https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_1_8/doc/build/orm/extensions/asyncio.rst) | entera |  |
| [sqlalchemy/session_basics.rst](sqlalchemy/session_basics.rst) | [origen](https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_1_8/doc/build/orm/session_basics.rst) | entera |  |
| [alembic/autogenerate.rst](alembic/autogenerate.rst) | [origen](https://raw.githubusercontent.com/sqlalchemy/alembic/rel_1_20_1/docs/build/autogenerate.rst) | entera |  |
| [postgresql/datatype.sgml](postgresql/datatype.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/datatype.sgml) | por entradas |  |
| [postgresql/json.sgml](postgresql/json.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/json.sgml) | entera |  |
| [postgresql/func.sgml](postgresql/func.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/func.sgml) | por entradas |  |
| [postgresql/ddl.sgml](postgresql/ddl.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/ddl.sgml) | entera |  |
| [postgresql/syntax.sgml](postgresql/syntax.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/syntax.sgml) | por entradas |  |
| [postgresql/indices.sgml](postgresql/indices.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/indices.sgml) | entera |  |
| [postgresql/backup.sgml](postgresql/backup.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/backup.sgml) | entera |  |
| [postgresql/client-auth.sgml](postgresql/client-auth.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/client-auth.sgml) | por entradas |  |
| [postgresql/user-manag.sgml](postgresql/user-manag.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/user-manag.sgml) | por entradas |  |
| [postgresql/config.sgml](postgresql/config.sgml) | [origen](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/config.sgml) | por entradas |  |
| [postgis/using_postgis_dataman.xml](postgis/using_postgis_dataman.xml) | [origen](https://raw.githubusercontent.com/postgis/postgis/stable-3.5/doc/using_postgis_dataman.xml) | entera |  |
| [rfc/rfc3339.txt](rfc/rfc3339.txt) | [origen](https://www.rfc-editor.org/rfc/rfc3339.txt) | entera |  |
| [rfc/rfc5646.txt](rfc/rfc5646.txt) | [origen](https://www.rfc-editor.org/rfc/rfc5646.txt) | entera |  |
| [rfc/rfc6749.txt](rfc/rfc6749.txt) | [origen](https://www.rfc-editor.org/rfc/rfc6749.txt) | entera |  |
| [rfc/rfc6585.txt](rfc/rfc6585.txt) | [origen](https://www.rfc-editor.org/rfc/rfc6585.txt) | entera |  |
| [rfc/rfc6901.txt](rfc/rfc6901.txt) | [origen](https://www.rfc-editor.org/rfc/rfc6901.txt) | entera |  |
| [rfc/rfc7493.txt](rfc/rfc7493.txt) | [origen](https://www.rfc-editor.org/rfc/rfc7493.txt) | entera |  |
| [rfc/rfc7519.txt](rfc/rfc7519.txt) | [origen](https://www.rfc-editor.org/rfc/rfc7519.txt) | entera |  |
| [rfc/rfc7636.txt](rfc/rfc7636.txt) | [origen](https://www.rfc-editor.org/rfc/rfc7636.txt) | entera |  |
| [rfc/rfc8030.txt](rfc/rfc8030.txt) | [origen](https://www.rfc-editor.org/rfc/rfc8030.txt) | entera |  |
| [rfc/rfc8252.txt](rfc/rfc8252.txt) | [origen](https://www.rfc-editor.org/rfc/rfc8252.txt) | entera |  |
| [rfc/rfc8292.txt](rfc/rfc8292.txt) | [origen](https://www.rfc-editor.org/rfc/rfc8292.txt) | entera |  |
| [rfc/rfc8656.txt](rfc/rfc8656.txt) | [origen](https://www.rfc-editor.org/rfc/rfc8656.txt) | entera |  |
| [rfc/rfc8725.txt](rfc/rfc8725.txt) | [origen](https://www.rfc-editor.org/rfc/rfc8725.txt) | entera |  |
| [rfc/rfc9110.txt](rfc/rfc9110.txt) | [origen](https://www.rfc-editor.org/rfc/rfc9110.txt) | entera |  |
| [rfc/rfc9457.txt](rfc/rfc9457.txt) | [origen](https://www.rfc-editor.org/rfc/rfc9457.txt) | entera |  |
| [rfc/rfc9700.txt](rfc/rfc9700.txt) | [origen](https://www.rfc-editor.org/rfc/rfc9700.txt) | entera |  |
| [openapi/openapi-3.1.2.md](openapi/openapi-3.1.2.md) | [origen](https://raw.githubusercontent.com/OAI/OpenAPI-Specification/3.1.2/versions/3.1.2.md) | por entradas | Línea 3.1, la versión que genera FastAPI |
| [google-aip/aip-0158.md](google-aip/aip-0158.md) | [origen](https://raw.githubusercontent.com/aip-dev/google.aip.dev/2ccc61a4e09882bdd63aea1a42dceebc37bf3bd5/aip/general/0158.md) | entera |  |
| [w3c/csp3.bs](w3c/csp3.bs) | [origen](https://raw.githubusercontent.com/w3c/webappsec-csp/b1bad631b091cdca904138d6947a16b89edfd2b4/index.bs) | entera |  |
| [w3c/webauthn-3.html](w3c/webauthn-3.html) | [origen](https://www.w3.org/TR/2026/REC-webauthn-3-20260825/) | entera | Recomendación del 2026-08-25 |
| [w3c/webrtc.html](w3c/webrtc.html) | [origen](https://www.w3.org/TR/2025/REC-webrtc-20250313/) | por entradas | Recomendación del 2025-03-13 |
| [w3c/push-api.html](w3c/push-api.html) | [origen](https://www.w3.org/TR/2026/WD-push-api-20261005/) | por entradas | Borrador de trabajo del 2026-10-05 |
| [w3c/wcag22.html](w3c/wcag22.html) | [origen](https://www.w3.org/TR/WCAG22/) | entera |  |
| [w3c/permissions-policy-features.md](w3c/permissions-policy-features.md) | [origen](https://raw.githubusercontent.com/w3c/webappsec-permissions-policy/29398046f1e0cb45c091adda853df74925dc740a/features.md) |  | Commit 2939804. Lista de nombres, no fuente |
| [dtcg/format.html](dtcg/format.html) | [origen](https://www.designtokens.org/tr/2025.10/format/) | entera |  |
| [dtcg/color.html](dtcg/color.html) | [origen](https://www.designtokens.org/tr/2025.10/color/) | entera |  |
| [dtcg/resolver.html](dtcg/resolver.html) | [origen](https://www.designtokens.org/tr/2025.10/resolver/) | entera |  |
| [whatwg/notifications.bs](whatwg/notifications.bs) | [origen](https://raw.githubusercontent.com/whatwg/notifications/7dc3884173370fe9385d538de299e415a2b9613a/notifications.bs) | entera |  |
| [wicg/sms-one-time-codes.bs](wicg/sms-one-time-codes.bs) | [origen](https://raw.githubusercontent.com/WICG/sms-one-time-codes/2bb70db2550c4a4d76a4836f1b42d7abfca4ab82/index.bs) | entera |  |
| [wicg/webotp.bs](wicg/webotp.bs) | [origen](https://raw.githubusercontent.com/WICG/web-otp/7c4a606a085b44d9de75001f7e801f07a4d85f8c/index.bs) | entera |  |
| [nist/sp800-63b-4.txt](nist/sp800-63b-4.txt) | [origen](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63B-4.pdf) | entera | Texto extraído del PDF |
| [nist/sp800-41r1.txt](nist/sp800-41r1.txt) | [origen](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-41r1.pdf) | entera | Texto extraído del PDF |
| [iana/iana-ipv4-special-registry.csv](iana/iana-ipv4-special-registry.csv) | [origen](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry-1.csv) |  | Descargado el 2026-10-27. Lista de direcciones, no fuente |
| [iana/iana-ipv6-special-registry.csv](iana/iana-ipv6-special-registry.csv) | [origen](https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry-1.csv) |  | Descargado el 2026-10-27. Lista de direcciones, no fuente |
| [fhs/fhs-3.0.txt](fhs/fhs-3.0.txt) | [origen](https://www.debian.org/doc/packaging-manuals/fhs/fhs-3.0.txt) | por entradas | Versión 3.0, la que sigue Debian 13. Copia de Debian: refspecs.linuxfoundation.org rechaza la descarga |
| [owasp/ASVS_V3_Web_Frontend_Security.md](owasp/ASVS_V3_Web_Frontend_Security.md) | [origen](https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x12-V3-Web-Frontend-Security.md) | entera | Versión 5.0.0 |
| [owasp/ASVS_V7_Session_Management.md](owasp/ASVS_V7_Session_Management.md) | [origen](https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x16-V7-Session-Management.md) | entera | Versión 5.0.0 |
| [owasp/Authorization.md](owasp/Authorization.md) | [origen](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Authorization_Cheat_Sheet.md) | entera |  |
| [owasp/Content_Security_Policy.md](owasp/Content_Security_Policy.md) | [origen](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/1eacf6cb9bfcba006ca972a804c5faace8c2758a/cheatsheets/Content_Security_Policy_Cheat_Sheet.md) | entera |  |
| [owasp/Password_Storage.md](owasp/Password_Storage.md) | [origen](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Password_Storage_Cheat_Sheet.md) | entera |  |
| [owasp/HTTP_Headers.md](owasp/HTTP_Headers.md) | [origen](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/HTTP_Headers_Cheat_Sheet.md) | entera |  |
| [owasp/Logging.md](owasp/Logging.md) | [origen](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Logging_Cheat_Sheet.md) | entera |  |
| [owasp/Logging_Vocabulary.md](owasp/Logging_Vocabulary.md) | [origen](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Logging_Vocabulary_Cheat_Sheet.md) | por entradas |  |
| [owasp/Third_Party_Payment_Gateway_Integration.md](owasp/Third_Party_Payment_Gateway_Integration.md) | [origen](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Third_Party_Payment_Gateway_Integration_Cheat_Sheet.md) | entera |  |
| [owasp/File_Upload.md](owasp/File_Upload.md) | [origen](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/File_Upload_Cheat_Sheet.md) | entera |  |
| [owasp/WebSocket_Security.md](owasp/WebSocket_Security.md) | [origen](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/WebSocket_Security_Cheat_Sheet.md) | entera |  |
| [valkey/admin.md](valkey/admin.md) | [origen](https://raw.githubusercontent.com/valkey-io/valkey-doc/8.1.1/topics/admin.md) | entera | Valkey 8.1, la versión de Debian 13 |
| [valkey/security.md](valkey/security.md) | [origen](https://raw.githubusercontent.com/valkey-io/valkey-doc/8.1.1/topics/security.md) | entera | Valkey 8.1, la versión de Debian 13 |
| [standard-webhooks/standard-webhooks.md](standard-webhooks/standard-webhooks.md) | [origen](https://raw.githubusercontent.com/standard-webhooks/standard-webhooks/v1.0.2/spec/standard-webhooks.md) | entera |  |
| [sveltekit/project-structure.md](sveltekit/project-structure.md) | [origen](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.1.1/documentation/docs/10-getting-started/30-project-structure.md) | entera |  |
| [sveltekit/load.md](sveltekit/load.md) | [origen](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.1.1/documentation/docs/20-core-concepts/20-load.md) | entera |  |
| [sveltekit/page-options.md](sveltekit/page-options.md) | [origen](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.1.1/documentation/docs/20-core-concepts/40-page-options.md) | entera |  |
| [sveltekit/state-management.md](sveltekit/state-management.md) | [origen](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.1.1/documentation/docs/20-core-concepts/50-state-management.md) | entera |  |
| [sveltekit/adapter-static.md](sveltekit/adapter-static.md) | [origen](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.1.1/documentation/docs/25-build-and-deploy/50-adapter-static.md) | entera |  |
| [svelte/state.md](svelte/state.md) | [origen](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/02-$state.md) | entera |  |
| [svelte/derived.md](svelte/derived.md) | [origen](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/03-$derived.md) | entera |  |
| [svelte/effect.md](svelte/effect.md) | [origen](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/04-$effect.md) | entera |  |
| [svelte/props.md](svelte/props.md) | [origen](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/05-$props.md) | entera |  |
| [svelte/bindable.md](svelte/bindable.md) | [origen](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/06-$bindable.md) | entera |  |
| [svelte/sv-check.md](svelte/sv-check.md) | [origen](https://raw.githubusercontent.com/sveltejs/cli/sv@1.3.0/documentation/docs/20-commands/30-sv-check.md) | por entradas |  |
| [unocss/guide-config-file.md](unocss/guide-config-file.md) | [origen](https://raw.githubusercontent.com/unocss/unocss/v66.12.0/docs/guide/config-file.md) | entera |  |
| [unocss/config-index.md](unocss/config-index.md) | [origen](https://raw.githubusercontent.com/unocss/unocss/v66.12.0/docs/config/index.md) | por entradas |  |
| [unocss/config-theme.md](unocss/config-theme.md) | [origen](https://raw.githubusercontent.com/unocss/unocss/v66.12.0/docs/config/theme.md) | por entradas |  |
| [unocss/presets-wind4.md](unocss/presets-wind4.md) | [origen](https://raw.githubusercontent.com/unocss/unocss/v66.12.0/docs/presets/wind4.md) | entera |  |
| [unocss/integrations-vite.md](unocss/integrations-vite.md) | [origen](https://raw.githubusercontent.com/unocss/unocss/v66.12.0/docs/integrations/vite.md) | entera |  |
| [vitest/guide.md](vitest/guide.md) | [origen](https://raw.githubusercontent.com/vitest-dev/vitest/v5.1.0/docs/guide/index.md) | entera |  |
| [vitest/features.md](vitest/features.md) | [origen](https://raw.githubusercontent.com/vitest-dev/vitest/v5.1.0/docs/guide/features.md) | entera |  |
| [paraglide/basics.md](paraglide/basics.md) | [origen](https://raw.githubusercontent.com/opral/paraglide-js/bad4564fbbb0c4d204b8621fdcd5aac5c6ceb899/docs/basics.md) | entera |  |
| [paraglide/compiling-messages.md](paraglide/compiling-messages.md) | [origen](https://raw.githubusercontent.com/opral/paraglide-js/5ed1745276180e3cb481d5e8cefd7eae3a9d8ce6/docs/compiling-messages.md) | entera |  |
| [paraglide/strategy.md](paraglide/strategy.md) | [origen](https://raw.githubusercontent.com/opral/paraglide-js/bad4564fbbb0c4d204b8621fdcd5aac5c6ceb899/docs/strategy.md) | entera |  |
| [dart/effective-dart-index.md](dart/effective-dart-index.md) | [origen](https://raw.githubusercontent.com/dart-lang/site-www/fd943b8add36fe5eaa55b594ea6a8501ae667407/src/content/effective-dart/index.md) | entera |  |
| [dart/effective-dart-style.md](dart/effective-dart-style.md) | [origen](https://raw.githubusercontent.com/dart-lang/site-www/d7879f023185039ecceecca635d6ce9d182b5d87/src/content/effective-dart/style.md) | entera |  |
| [dart/effective-dart-documentation.md](dart/effective-dart-documentation.md) | [origen](https://raw.githubusercontent.com/dart-lang/site-www/83ebb33f4768c0b568d2d07541328785aeee2199/src/content/effective-dart/documentation.md) | entera |  |
| [dart/effective-dart-usage.md](dart/effective-dart-usage.md) | [origen](https://raw.githubusercontent.com/dart-lang/site-www/f751f882acad62538b7356cc90ab13c25ec5b4a4/src/content/effective-dart/usage.md) | entera |  |
| [dart/effective-dart-design.md](dart/effective-dart-design.md) | [origen](https://raw.githubusercontent.com/dart-lang/site-www/065a1a10ca7b2e3d955a34e9294b096f7a5ef664/src/content/effective-dart/design.md) | entera |  |
| [flutter/app-architecture-concepts.md](flutter/app-architecture-concepts.md) | [origen](https://raw.githubusercontent.com/flutter/website/c63034dad2738e18d4f3a0c88487410179395f3a/sites/docs/src/content/app-architecture/concepts.md) | entera |  |
| [flutter/app-architecture-guide.md](flutter/app-architecture-guide.md) | [origen](https://raw.githubusercontent.com/flutter/website/afe82c4e59af75731eb83c2138a93837934f65b8/sites/docs/src/content/app-architecture/guide.md) | entera |  |
| [flutter/app-architecture-recommendations.md](flutter/app-architecture-recommendations.md) | [origen](https://raw.githubusercontent.com/flutter/website/afe82c4e59af75731eb83c2138a93837934f65b8/sites/docs/src/content/app-architecture/recommendations.md) | entera |  |
| [flutter/architecture-recommendations.yml](flutter/architecture-recommendations.yml) | [origen](https://raw.githubusercontent.com/flutter/website/afe82c4e59af75731eb83c2138a93837934f65b8/sites/docs/src/data/architectureRecommendations.yml) | entera | Las recomendaciones que la página anterior muestra desde este archivo |
| [flutter/state-mgmt-simple.md](flutter/state-mgmt-simple.md) | [origen](https://raw.githubusercontent.com/flutter/website/4d79bcadda0e47e66a6a7ebe35eaea50474e4d9d/sites/docs/src/content/data-and-backend/state-mgmt/simple.md) | entera |  |
| [flutter/internationalization.md](flutter/internationalization.md) | [origen](https://raw.githubusercontent.com/flutter/website/5aa5d3cfa2c41558b22516125c73d7a5efc4ce15/sites/docs/src/content/ui/internationalization/index.md) | entera |  |
| [flutter/accessibility.md](flutter/accessibility.md) | [origen](https://raw.githubusercontent.com/flutter/website/954d844c43c6ad9dd7cb1855b58ae145bee49983/sites/docs/src/content/ui/accessibility/index.md) | entera |  |
| [flutter/accessibility-assistive.md](flutter/accessibility-assistive.md) | [origen](https://raw.githubusercontent.com/flutter/website/afe82c4e59af75731eb83c2138a93837934f65b8/sites/docs/src/content/ui/accessibility/assistive-technologies.md) | entera |  |
| [flutter/accessibility-testing.md](flutter/accessibility-testing.md) | [origen](https://raw.githubusercontent.com/flutter/website/afe82c4e59af75731eb83c2138a93837934f65b8/sites/docs/src/content/ui/accessibility/accessibility-testing.md) | entera |  |
| [pub/shared_preferences/README.md](pub/shared_preferences/README.md) | [origen](https://raw.githubusercontent.com/flutter/packages/shared_preferences-v2.5.6/packages/shared_preferences/shared_preferences/README.md) | entera |  |
| [pub/flutter_secure_storage/README.md](pub/flutter_secure_storage/README.md) | [origen](https://pub.dev/api/archives/flutter_secure_storage-11.2.0.tar.gz) | entera | `README.md` del paquete 11.2.0 publicado |
| [pub/provider/README.md](pub/provider/README.md) | [origen](https://pub.dev/api/archives/provider-6.1.5+1.tar.gz) | entera | `README.md` del paquete 6.1.5+1 publicado |
| [osm/attribution-guidelines.md](osm/attribution-guidelines.md) | [origen](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines) | entera | Página web convertida a Markdown |
| [kotlin/coding-conventions.md](kotlin/coding-conventions.md) | [origen](https://raw.githubusercontent.com/JetBrains/kotlin-web-site/f51dacdc4420c6690ad88d513caf3c1a0a25b75f/docs/topics/coding-conventions.md) | entera |  |
| [android/architecture.md](android/architecture.md) | [origen](https://developer.android.com/topic/architecture) | entera | Página web convertida a Markdown |
| [android/architecture-recommendations.md](android/architecture-recommendations.md) | [origen](https://developer.android.com/topic/architecture/recommendations) | entera | Página web convertida a Markdown |
| [android/ui-layer.md](android/ui-layer.md) | [origen](https://developer.android.com/topic/architecture/ui-layer) | entera | Página web convertida a Markdown |
| [android/data-layer.md](android/data-layer.md) | [origen](https://developer.android.com/topic/architecture/data-layer) | entera | Página web convertida a Markdown |
| [android/kotlin-style-guide.md](android/kotlin-style-guide.md) | [origen](https://developer.android.com/kotlin/style-guide) | entera | Página web convertida a Markdown |
| [android/coroutines-best-practices.md](android/coroutines-best-practices.md) | [origen](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) | entera | Página web convertida a Markdown |
| [android/hilt.md](android/hilt.md) | [origen](https://developer.android.com/training/dependency-injection/hilt-android) | entera | Página web convertida a Markdown |
| [android/datastore.md](android/datastore.md) | [origen](https://developer.android.com/topic/libraries/architecture/datastore) | entera | Página web convertida a Markdown |
| [android/keystore.md](android/keystore.md) | [origen](https://developer.android.com/privacy-and-security/keystore) | entera | Página web convertida a Markdown |
| [android/testing-fundamentals.md](android/testing-fundamentals.md) | [origen](https://developer.android.com/training/testing/fundamentals) | entera | Página web convertida a Markdown |
| [android/localization.md](android/localization.md) | [origen](https://developer.android.com/guide/topics/resources/localization) | entera | Página web convertida a Markdown |
| [android/accessibility-apps.md](android/accessibility-apps.md) | [origen](https://developer.android.com/guide/topics/ui/accessibility/apps) | entera | Página web convertida a Markdown |
| [android/accessibility-principles.md](android/accessibility-principles.md) | [origen](https://developer.android.com/guide/topics/ui/accessibility/principles) | entera | Página web convertida a Markdown |
| [android/sms-retriever-request.md](android/sms-retriever-request.md) | [origen](https://developers.google.com/identity/sms-retriever/request) | entera | Página web convertida a Markdown |
| [android/credential-manager-prerequisites.md](android/credential-manager-prerequisites.md) | [origen](https://developer.android.com/identity/credential-manager/prerequisites) | entera | Página web convertida a Markdown |
| [android/create-passkeys.md](android/create-passkeys.md) | [origen](https://developer.android.com/identity/passkeys/create-passkeys) | entera | Página web convertida a Markdown |
| [android/sign-in-with-passkeys.md](android/sign-in-with-passkeys.md) | [origen](https://developer.android.com/identity/passkeys/sign-in-with-passkeys) | entera | Página web convertida a Markdown |
| [android/notification-permission.md](android/notification-permission.md) | [origen](https://developer.android.com/develop/ui/compose/notifications/notification-permission) | entera | Página web convertida a Markdown |
| [android/notification-channels.md](android/notification-channels.md) | [origen](https://developer.android.com/develop/ui/compose/notifications/channels) | entera | Página web convertida a Markdown |
| [compose/state.md](compose/state.md) | [origen](https://developer.android.com/develop/ui/compose/state) | entera | Página web convertida a Markdown |
| [compose/architecture.md](compose/architecture.md) | [origen](https://developer.android.com/develop/ui/compose/architecture) | entera | Página web convertida a Markdown |
| [compose/testing.md](compose/testing.md) | [origen](https://developer.android.com/develop/ui/compose/testing) | entera | Página web convertida a Markdown |
| [compose/accessibility-testing.md](compose/accessibility-testing.md) | [origen](https://developer.android.com/develop/ui/compose/accessibility/testing) | entera | Página web convertida a Markdown |
| [flet/encrypting-sensitive-data.md](flet/encrypting-sensitive-data.md) | [origen](https://raw.githubusercontent.com/flet-dev/flet/v1.0.5/website/docs/cookbook/encrypting-sensitive-data.md) | entera |  |
| [flet/securestorage.md](flet/securestorage.md) | [origen](https://raw.githubusercontent.com/flet-dev/flet/v1.0.5/website/docs/services/securestorage/index.md) | por entradas |  |
| [flet/publish.md](flet/publish.md) | [origen](https://raw.githubusercontent.com/flet-dev/flet/v1.0.5/website/docs/publish/index.md) | por entradas |  |
| [pyside6/considerations.rst](pyside6/considerations.rst) | [origen](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/considerations.rst) | entera |  |
| [pyside6/porting_from2.rst](pyside6/porting_from2.rst) | [origen](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/faq/porting_from2.rst) | entera |  |
| [pyside6/signals_and_slots.rst](pyside6/signals_and_slots.rst) | [origen](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/signals_and_slots.rst) | entera |  |
| [pyside6/translations.rst](pyside6/translations.rst) | [origen](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/translations.rst) | entera |  |
| [pyside6/deployment-pyside6-deploy.rst](pyside6/deployment-pyside6-deploy.rst) | [origen](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/deployment/deployment-pyside6-deploy.rst) | por entradas |  |
| [qt/layout.qdoc](qt/layout.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/layout.qdoc) | entera |  |
| [qt/model-view-programming.qdoc](qt/model-view-programming.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/model-view-programming.qdoc) | entera |  |
| [qt/stylesheet.qdoc](qt/stylesheet.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet.qdoc) | entera |  |
| [qt/stylesheet-syntax.qdoc](qt/stylesheet-syntax.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet-syntax.qdoc) | entera |  |
| [qt/stylesheet-customizing.qdoc](qt/stylesheet-customizing.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet-customizing.qdoc) | entera |  |
| [qt/stylesheet-reference.qdoc](qt/stylesheet-reference.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet-reference.qdoc) | por entradas |  |
| [qt/threads.qdoc](qt/threads.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtdoc/v6.12.0/doc/src/frameworks-technologies/threads.qdoc) | entera |  |
| [qt/qwidget.qdoc](qt/qwidget.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/kernel/qwidget.cpp) | por entradas | Comentarios `/*! */` del código fuente |
| [qt/qdialog.qdoc](qt/qdialog.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/dialogs/qdialog.cpp) | por entradas | Comentarios `/*! */` del código fuente |
| [qt/qsettings.qdoc](qt/qsettings.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/corelib/io/qsettings.cpp) | por entradas | Comentarios `/*! */` del código fuente |
| [qt/qnetworkaccessmanager.qdoc](qt/qnetworkaccessmanager.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/network/access/qnetworkaccessmanager.cpp) | por entradas | Comentarios `/*! */` del código fuente |
| [qt/accessible.qdoc](qt/accessible.qdoc) | [origen](https://raw.githubusercontent.com/qt/qtdoc/v6.12.0/doc/src/frameworks-technologies/accessible.qdoc) | entera |  |
| [pytest-qt/qapplication.rst](pytest-qt/qapplication.rst) | [origen](https://raw.githubusercontent.com/pytest-dev/pytest-qt/4.5.0/docs/qapplication.rst) | entera |  |
| [pytest-qt/signals.rst](pytest-qt/signals.rst) | [origen](https://raw.githubusercontent.com/pytest-dev/pytest-qt/4.5.0/docs/signals.rst) | por entradas |  |
| [systemd/systemd.exec.xml](systemd/systemd.exec.xml) | [origen](https://raw.githubusercontent.com/systemd/systemd/v257.13/man/systemd.exec.xml) | por entradas | systemd 257, la versión de Debian 13 |
| [systemd/journald.conf.xml](systemd/journald.conf.xml) | [origen](https://raw.githubusercontent.com/systemd/systemd/v257.13/man/journald.conf.xml) | por entradas | systemd 257, la versión de Debian 13 |
| [systemd/journal-upload.conf.xml](systemd/journal-upload.conf.xml) | [origen](https://raw.githubusercontent.com/systemd/systemd/v257.13/man/journal-upload.conf.xml) | por entradas | systemd 257, la versión de Debian 13 |
| [wireguard/wg-quick.8](wireguard/wg-quick.8) | [origen](https://git.zx2c4.com/wireguard-tools/plain/src/man/wg-quick.8?h=v1.0.20210914) | por entradas | wireguard-tools 1.0.20210914, la versión de Debian 13 |
| [wireguard/wg.8](wireguard/wg.8) | [origen](https://git.zx2c4.com/wireguard-tools/plain/src/man/wg.8?h=v1.0.20210914) | por entradas | wireguard-tools 1.0.20210914, la versión de Debian 13 |
| [openssh/sshd_config.5](openssh/sshd_config.5) | [origen](https://raw.githubusercontent.com/openssh/openssh-portable/V_10_0_P1/sshd_config.5) | por entradas | OpenSSH 10.0, la versión de Debian 13 |
| [openssh/ssh-keygen.1](openssh/ssh-keygen.1) | [origen](https://raw.githubusercontent.com/openssh/openssh-portable/V_10_0_P1/ssh-keygen.1) | por entradas | OpenSSH 10.0, la versión de Debian 13 |
| [unattended-upgrades/50unattended-upgrades.Debian](unattended-upgrades/50unattended-upgrades.Debian) | [origen](https://sources.debian.org/data/main/u/unattended-upgrades/2.12/data/50unattended-upgrades.Debian) | por entradas | unattended-upgrades 2.12, la versión de Debian 13 |
