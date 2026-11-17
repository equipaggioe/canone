# Fuentes

Copia de los textos de las fuentes de las que salen las convenciones adoptadas de las páginas de [plataformas/](../plataformas/), y de las listas de las que un programa de Canone toma valores. Una página se revisa contra el texto de aquí, no de memoria. Una fuente que solo cita un ADR no se copia: el ADR la usa como argumento de su decisión, y ninguna página adopta sus convenciones.

- Cada archivo es el texto de su fuente, sin editar. Cuando la fuente es una página web, es su contenido convertido a Markdown.
- Cada archivo se descarga del tag o la rama de la versión que se usa, nunca de `main` ni de `master`. Una fuente sin versiones se descarga de un commit fijo, y su URL lleva el SHA.
- La publicación de una nueva versión no implica su adopción automática. Decidir si se incorpora corresponde al mantenimiento de Canone: requiere revisar sus cambios y determinar si justifican modificar las convenciones existentes.
- Al cambiar la versión de una tecnología, se vuelven a descargar sus fuentes.
- Para actualizar un archivo se vuelve a descargar de su fuente; `git diff` muestra qué cambió, y cada cambio que se adopta se pasa a las convenciones que lo tienen como origen.
- Un archivo que no es el origen de ninguna convención se borra, salvo una lista de la que un programa de Canone toma valores.

| Archivo | Fuente | Nota |
| :--- | :--- | :--- |
| [python/pep-0008.rst](python/pep-0008.rst) | [URL](https://raw.githubusercontent.com/python/peps/5514795ade79a5bf6f3c08c562b02689d0a9feb2/peps/pep-0008.rst) |  |
| [python/pep-0257.rst](python/pep-0257.rst) | [URL](https://raw.githubusercontent.com/python/peps/f22614f903cd50d19e5463913fde6d4a17109de0/peps/pep-0257.rst) |  |
| [python/asyncio-dev.rst](python/asyncio-dev.rst) | [URL](https://raw.githubusercontent.com/python/cpython/3.13/Doc/library/asyncio-dev.rst) | Rama 3.13, la versión que usan las piezas: la de `main` nombra `InterpreterPoolExecutor`, que no existe en 3.13. |
| [python/asyncio-task.rst](python/asyncio-task.rst) | [URL](https://raw.githubusercontent.com/python/cpython/3.13/Doc/library/asyncio-task.rst) | Rama 3.13, la versión que usan las piezas |
| [pytest/goodpractices.rst](pytest/goodpractices.rst) | [URL](https://raw.githubusercontent.com/pytest-dev/pytest/9.2.0/doc/en/explanation/goodpractices.rst) |  |
| [typing/best_practices.rst](typing/best_practices.rst) | [URL](https://raw.githubusercontent.com/python/typing/953e24d71aa6ea97f58852046fc355d11b564333/docs/reference/best_practices.rst) |  |
| [typing/modernizing.rst](typing/modernizing.rst) | [URL](https://raw.githubusercontent.com/python/typing/39164cd2c5b4e2608cb8b5d2fc8af9ae6f0c0fe8/docs/guides/modernizing.rst) |  |
| [sqlalchemy/asyncio.rst](sqlalchemy/asyncio.rst) | [URL](https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_1_8/doc/build/orm/extensions/asyncio.rst) |  |
| [sqlalchemy/session_basics.rst](sqlalchemy/session_basics.rst) | [URL](https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_1_8/doc/build/orm/session_basics.rst) |  |
| [alembic/autogenerate.rst](alembic/autogenerate.rst) | [URL](https://raw.githubusercontent.com/sqlalchemy/alembic/rel_1_20_1/docs/build/autogenerate.rst) |  |
| [postgresql/datatype.sgml](postgresql/datatype.sgml) | [URL](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/datatype.sgml) |  |
| [postgresql/json.sgml](postgresql/json.sgml) | [URL](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/json.sgml) |  |
| [postgresql/ddl.sgml](postgresql/ddl.sgml) | [URL](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/ddl.sgml) |  |
| [postgresql/indices.sgml](postgresql/indices.sgml) | [URL](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/indices.sgml) |  |
| [postgresql/backup.sgml](postgresql/backup.sgml) | [URL](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/backup.sgml) |  |
| [postgis/using_postgis_dataman.xml](postgis/using_postgis_dataman.xml) | [URL](https://raw.githubusercontent.com/postgis/postgis/stable-3.5/doc/using_postgis_dataman.xml) |  |
| [rfc/rfc5646.txt](rfc/rfc5646.txt) | [URL](https://www.rfc-editor.org/rfc/rfc5646.txt) |  |
| [rfc/rfc6749.txt](rfc/rfc6749.txt) | [URL](https://www.rfc-editor.org/rfc/rfc6749.txt) |  |
| [rfc/rfc6585.txt](rfc/rfc6585.txt) | [URL](https://www.rfc-editor.org/rfc/rfc6585.txt) |  |
| [rfc/rfc7493.txt](rfc/rfc7493.txt) | [URL](https://www.rfc-editor.org/rfc/rfc7493.txt) |  |
| [rfc/rfc7636.txt](rfc/rfc7636.txt) | [URL](https://www.rfc-editor.org/rfc/rfc7636.txt) |  |
| [rfc/rfc7946.txt](rfc/rfc7946.txt) | [URL](https://www.rfc-editor.org/rfc/rfc7946.txt) |  |
| [rfc/rfc8030.txt](rfc/rfc8030.txt) | [URL](https://www.rfc-editor.org/rfc/rfc8030.txt) |  |
| [rfc/rfc8252.txt](rfc/rfc8252.txt) | [URL](https://www.rfc-editor.org/rfc/rfc8252.txt) |  |
| [rfc/rfc8292.txt](rfc/rfc8292.txt) | [URL](https://www.rfc-editor.org/rfc/rfc8292.txt) |  |
| [rfc/rfc8656.txt](rfc/rfc8656.txt) | [URL](https://www.rfc-editor.org/rfc/rfc8656.txt) |  |
| [rfc/rfc9110.txt](rfc/rfc9110.txt) | [URL](https://www.rfc-editor.org/rfc/rfc9110.txt) |  |
| [rfc/rfc9457.txt](rfc/rfc9457.txt) | [URL](https://www.rfc-editor.org/rfc/rfc9457.txt) |  |
| [rfc/rfc9700.txt](rfc/rfc9700.txt) | [URL](https://www.rfc-editor.org/rfc/rfc9700.txt) |  |
| [openapi/openapi-3.1.2.md](openapi/openapi-3.1.2.md) | [URL](https://raw.githubusercontent.com/OAI/OpenAPI-Specification/3.1.2/versions/3.1.2.md) | Línea 3.1, la versión que genera FastAPI |
| [google-aip/aip-0158.md](google-aip/aip-0158.md) | [URL](https://raw.githubusercontent.com/aip-dev/google.aip.dev/2ccc61a4e09882bdd63aea1a42dceebc37bf3bd5/aip/general/0158.md) |  |
| [w3c/webauthn-3.html](w3c/webauthn-3.html) | [URL](https://www.w3.org/TR/2026/REC-webauthn-3-20260825/) | Recomendación del 2026-08-25 |
| [w3c/push-api.html](w3c/push-api.html) | [URL](https://www.w3.org/TR/2026/WD-push-api-20261005/) | Borrador de trabajo del 2026-10-05 |
| [w3c/wcag22.html](w3c/wcag22.html) | [URL](https://www.w3.org/TR/2024/REC-WCAG22-20241212/) |  |
| [w3c/permissions-policy-features.md](w3c/permissions-policy-features.md) | [URL](https://raw.githubusercontent.com/w3c/webappsec-permissions-policy/29398046f1e0cb45c091adda853df74925dc740a/features.md) | Commit 2939804. Lista de nombres, no fuente |
| [dtcg/format.html](dtcg/format.html) | [URL](https://www.designtokens.org/tr/2025.10/format/) |  |
| [dtcg/color.html](dtcg/color.html) | [URL](https://www.designtokens.org/tr/2025.10/color/) |  |
| [dtcg/resolver.html](dtcg/resolver.html) | [URL](https://www.designtokens.org/tr/2025.10/resolver/) |  |
| [wicg/sms-one-time-codes.bs](wicg/sms-one-time-codes.bs) | [URL](https://raw.githubusercontent.com/WICG/sms-one-time-codes/2bb70db2550c4a4d76a4836f1b42d7abfca4ab82/index.bs) |  |
| [nist/sp800-63b-4.txt](nist/sp800-63b-4.txt) | [URL](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63B-4.pdf) | Texto extraído del PDF |
| [nist/sp800-41r1.txt](nist/sp800-41r1.txt) | [URL](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-41r1.pdf) | Texto extraído del PDF |
| [nist/ir7966.txt](nist/ir7966.txt) | [URL](https://nvlpubs.nist.gov/nistpubs/ir/2015/NIST.IR.7966.pdf) | Texto extraído del PDF |
| [iana/iana-ipv4-special-registry.csv](iana/iana-ipv4-special-registry.csv) | [URL](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry-1.csv) | Descargado el 2026-10-27. Lista de direcciones, no fuente |
| [iana/iana-ipv6-special-registry.csv](iana/iana-ipv6-special-registry.csv) | [URL](https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry-1.csv) | Descargado el 2026-10-27. Lista de direcciones, no fuente |
| [fhs/fhs-3.0.txt](fhs/fhs-3.0.txt) | [URL](https://www.debian.org/doc/packaging-manuals/fhs/fhs-3.0.txt) | Versión 3.0, la que sigue Debian 13. Copia de Debian: refspecs.linuxfoundation.org rechaza la descarga |
| [owasp/ASVS_V3_Web_Frontend_Security.md](owasp/ASVS_V3_Web_Frontend_Security.md) | [URL](https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x12-V3-Web-Frontend-Security.md) | Versión 5.0.0 |
| [owasp/ASVS_V7_Session_Management.md](owasp/ASVS_V7_Session_Management.md) | [URL](https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x16-V7-Session-Management.md) | Versión 5.0.0 |
| [owasp/Authorization.md](owasp/Authorization.md) | [URL](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Authorization_Cheat_Sheet.md) |  |
| [owasp/Content_Security_Policy.md](owasp/Content_Security_Policy.md) | [URL](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/eaa71fb4a421dc057bf03a3856d0d34967299ff1/cheatsheets/Content_Security_Policy_Cheat_Sheet.md) |  |
| [owasp/Password_Storage.md](owasp/Password_Storage.md) | [URL](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Password_Storage_Cheat_Sheet.md) |  |
| [owasp/HTTP_Headers.md](owasp/HTTP_Headers.md) | [URL](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/HTTP_Headers_Cheat_Sheet.md) |  |
| [owasp/Logging.md](owasp/Logging.md) | [URL](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Logging_Cheat_Sheet.md) |  |
| [owasp/Logging_Vocabulary.md](owasp/Logging_Vocabulary.md) | [URL](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Logging_Vocabulary_Cheat_Sheet.md) |  |
| [owasp/Third_Party_Payment_Gateway_Integration.md](owasp/Third_Party_Payment_Gateway_Integration.md) | [URL](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/Third_Party_Payment_Gateway_Integration_Cheat_Sheet.md) |  |
| [owasp/File_Upload.md](owasp/File_Upload.md) | [URL](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/File_Upload_Cheat_Sheet.md) |  |
| [owasp/WebSocket_Security.md](owasp/WebSocket_Security.md) | [URL](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/08bda3ac496ba5feed72e577de327057d0be4485/cheatsheets/WebSocket_Security_Cheat_Sheet.md) |  |
| [valkey/admin.md](valkey/admin.md) | [URL](https://raw.githubusercontent.com/valkey-io/valkey-doc/8.1.1/topics/admin.md) | Valkey 8.1, la versión de Debian 13 |
| [valkey/security.md](valkey/security.md) | [URL](https://raw.githubusercontent.com/valkey-io/valkey-doc/8.1.1/topics/security.md) | Valkey 8.1, la versión de Debian 13 |
| [standard-webhooks/standard-webhooks.md](standard-webhooks/standard-webhooks.md) | [URL](https://raw.githubusercontent.com/standard-webhooks/standard-webhooks/v1.0.2/spec/standard-webhooks.md) |  |
| [sveltekit/project-structure.md](sveltekit/project-structure.md) | [URL](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.2.0/documentation/docs/10-getting-started/30-project-structure.md) |  |
| [sveltekit/load.md](sveltekit/load.md) | [URL](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.2.0/documentation/docs/20-core-concepts/20-load.md) |  |
| [sveltekit/page-options.md](sveltekit/page-options.md) | [URL](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.2.0/documentation/docs/20-core-concepts/40-page-options.md) |  |
| [sveltekit/state-management.md](sveltekit/state-management.md) | [URL](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.2.0/documentation/docs/20-core-concepts/50-state-management.md) |  |
| [sveltekit/adapter-static.md](sveltekit/adapter-static.md) | [URL](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.2.0/documentation/docs/25-build-and-deploy/50-adapter-static.md) |  |
| [sveltekit/accessibility.md](sveltekit/accessibility.md) | [URL](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.2.0/documentation/docs/40-best-practices/10-accessibility.md) |  |
| [svelte/best-practices.md](svelte/best-practices.md) | [URL](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/07-misc/01-best-practices.md) |  |
| [svelte/props.md](svelte/props.md) | [URL](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/05-$props.md) |  |
| [unocss/presets-wind4.md](unocss/presets-wind4.md) | [URL](https://raw.githubusercontent.com/unocss/unocss/v66.13.0/docs/presets/wind4.md) |  |
| [unocss/integrations-vite.md](unocss/integrations-vite.md) | [URL](https://raw.githubusercontent.com/unocss/unocss/v66.13.0/docs/integrations/vite.md) |  |
| [paraglide/basics.md](paraglide/basics.md) | [URL](https://raw.githubusercontent.com/generaltranslation/paraglide-js/7d207f935af539ad1113d4f00563258caf5dc040/docs/basics.md) | Commit de la versión 3.2.2 |
| [paraglide/compiling-messages.md](paraglide/compiling-messages.md) | [URL](https://raw.githubusercontent.com/generaltranslation/paraglide-js/7d207f935af539ad1113d4f00563258caf5dc040/docs/compiling-messages.md) | Commit de la versión 3.2.2 |
| [dart/effective-dart-style.md](dart/effective-dart-style.md) | [URL](https://raw.githubusercontent.com/dart-lang/site-www/d7879f023185039ecceecca635d6ce9d182b5d87/src/content/effective-dart/style.md) |  |
| [dart/effective-dart-documentation.md](dart/effective-dart-documentation.md) | [URL](https://raw.githubusercontent.com/dart-lang/site-www/83ebb33f4768c0b568d2d07541328785aeee2199/src/content/effective-dart/documentation.md) |  |
| [dart/effective-dart-usage.md](dart/effective-dart-usage.md) | [URL](https://raw.githubusercontent.com/dart-lang/site-www/f751f882acad62538b7356cc90ab13c25ec5b4a4/src/content/effective-dart/usage.md) |  |
| [dart/effective-dart-design.md](dart/effective-dart-design.md) | [URL](https://raw.githubusercontent.com/dart-lang/site-www/065a1a10ca7b2e3d955a34e9294b096f7a5ef664/src/content/effective-dart/design.md) |  |
| [flutter/app-architecture-concepts.md](flutter/app-architecture-concepts.md) | [URL](https://raw.githubusercontent.com/flutter/website/c63034dad2738e18d4f3a0c88487410179395f3a/sites/docs/src/content/app-architecture/concepts.md) |  |
| [flutter/app-architecture-guide.md](flutter/app-architecture-guide.md) | [URL](https://raw.githubusercontent.com/flutter/website/afe82c4e59af75731eb83c2138a93837934f65b8/sites/docs/src/content/app-architecture/guide.md) |  |
| [flutter/architecture-recommendations.yml](flutter/architecture-recommendations.yml) | [URL](https://raw.githubusercontent.com/flutter/website/afe82c4e59af75731eb83c2138a93837934f65b8/sites/docs/src/data/architectureRecommendations.yml) | Las recomendaciones que muestra [*Architecture recommendations and resources*](https://raw.githubusercontent.com/flutter/website/afe82c4e59af75731eb83c2138a93837934f65b8/sites/docs/src/content/app-architecture/recommendations.md) |
| [flutter/internationalization.md](flutter/internationalization.md) | [URL](https://raw.githubusercontent.com/flutter/website/5aa5d3cfa2c41558b22516125c73d7a5efc4ce15/sites/docs/src/content/ui/internationalization/index.md) |  |
| [pub/shared_preferences/README.md](pub/shared_preferences/README.md) | [URL](https://raw.githubusercontent.com/flutter/packages/shared_preferences-v2.5.6/packages/shared_preferences/shared_preferences/README.md) |  |
| [pub/flutter_secure_storage/README.md](pub/flutter_secure_storage/README.md) | [URL](https://raw.githubusercontent.com/juliansteenbakker/flutter_secure_storage/flutter_secure_storage-v11.2.0/flutter_secure_storage/README.md) |  |
| [riverpod/do_dont.mdx](riverpod/do_dont.mdx) | [URL](https://raw.githubusercontent.com/rrousselGit/riverpod/flutter_riverpod-v3.5.0/website/docs/root/do_dont.mdx) | Tag de flutter_riverpod 3.5.0 |
| [riverpod/providers.mdx](riverpod/providers.mdx) | [URL](https://raw.githubusercontent.com/rrousselGit/riverpod/flutter_riverpod-v3.5.0/website/docs/concepts2/providers.mdx) | Tag de flutter_riverpod 3.5.0 |
| [riverpod/refs.mdx](riverpod/refs.mdx) | [URL](https://raw.githubusercontent.com/rrousselGit/riverpod/flutter_riverpod-v3.5.0/website/docs/concepts2/refs.mdx) | Tag de flutter_riverpod 3.5.0 |
| [riverpod/consumers.mdx](riverpod/consumers.mdx) | [URL](https://raw.githubusercontent.com/rrousselGit/riverpod/flutter_riverpod-v3.5.0/website/docs/concepts2/consumers.mdx) | Tag de flutter_riverpod 3.5.0 |
| [riverpod/auto_dispose.mdx](riverpod/auto_dispose.mdx) | [URL](https://raw.githubusercontent.com/rrousselGit/riverpod/flutter_riverpod-v3.5.0/website/docs/concepts2/auto_dispose.mdx) | Tag de flutter_riverpod 3.5.0 |
| [riverpod/containers.mdx](riverpod/containers.mdx) | [URL](https://raw.githubusercontent.com/rrousselGit/riverpod/flutter_riverpod-v3.5.0/website/docs/concepts2/containers.mdx) | Tag de flutter_riverpod 3.5.0 |
| [riverpod/about_code_generation.mdx](riverpod/about_code_generation.mdx) | [URL](https://raw.githubusercontent.com/rrousselGit/riverpod/flutter_riverpod-v3.5.0/website/docs/concepts/about_code_generation.mdx) | Tag de flutter_riverpod 3.5.0 |
| [osm/attribution-guidelines.md](osm/attribution-guidelines.md) | [URL](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines) | Página web convertida a Markdown |
| [kotlin/coding-conventions.md](kotlin/coding-conventions.md) | [URL](https://raw.githubusercontent.com/JetBrains/kotlin-web-site/f51dacdc4420c6690ad88d513caf3c1a0a25b75f/docs/topics/coding-conventions.md) |  |
| [android/architecture.md](android/architecture.md) | [URL](https://developer.android.com/topic/architecture) | Página web convertida a Markdown |
| [android/architecture-recommendations.md](android/architecture-recommendations.md) | [URL](https://developer.android.com/topic/architecture/recommendations) | Página web convertida a Markdown |
| [android/data-layer.md](android/data-layer.md) | [URL](https://developer.android.com/topic/architecture/data-layer) | Página web convertida a Markdown |
| [android/kotlin-style-guide.md](android/kotlin-style-guide.md) | [URL](https://developer.android.com/kotlin/style-guide) | Página web convertida a Markdown |
| [android/coroutines-best-practices.md](android/coroutines-best-practices.md) | [URL](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) | Página web convertida a Markdown |
| [android/hilt.md](android/hilt.md) | [URL](https://developer.android.com/training/dependency-injection/hilt-android) | Página web convertida a Markdown |
| [android/localization.md](android/localization.md) | [URL](https://developer.android.com/guide/topics/resources/localization) | Página web convertida a Markdown |
| [android/credential-manager-prerequisites.md](android/credential-manager-prerequisites.md) | [URL](https://developer.android.com/identity/credential-manager/prerequisites) | Página web convertida a Markdown |
| [android/create-passkeys.md](android/create-passkeys.md) | [URL](https://developer.android.com/identity/passkeys/create-passkeys) | Página web convertida a Markdown |
| [android/sign-in-with-passkeys.md](android/sign-in-with-passkeys.md) | [URL](https://developer.android.com/identity/passkeys/sign-in-with-passkeys) | Página web convertida a Markdown |
| [android/notification-permission.md](android/notification-permission.md) | [URL](https://developer.android.com/develop/ui/compose/notifications/notification-permission) | Página web convertida a Markdown |
| [compose/state.md](compose/state.md) | [URL](https://developer.android.com/develop/ui/compose/state) | Página web convertida a Markdown |
| [flet/publish.md](flet/publish.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/publish/index.md) |  |
| [flet/publish-android.md](flet/publish-android.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/publish/android.md) |  |
| [flet/publish-windows.md](flet/publish-windows.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/publish/windows.md) |  |
| [flet/publish-linux.md](flet/publish-linux.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/publish/linux.md) |  |
| [flet/integration-testing.md](flet/integration-testing.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/getting-started/integration-testing.md) |  |
| [flet/async-apps.md](flet/async-apps.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/async-apps.md) |  |
| [flet/custom-controls.md](flet/custom-controls.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/custom-controls.md) |  |
| [flet/navigation-and-routing.md](flet/navigation-and-routing.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/navigation-and-routing.md) |  |
| [flet/accessibility.md](flet/accessibility.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/accessibility.md) |  |
| [flet/client-storage.md](flet/client-storage.md) | [URL](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/client-storage.md) |  |
| [pyside6/deployment-pyside6-deploy.rst](pyside6/deployment-pyside6-deploy.rst) | [URL](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/deployment/deployment-pyside6-deploy.rst) |  |
| [qt/model-view-programming.qdoc](qt/model-view-programming.qdoc) | [URL](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/model-view-programming.qdoc) |  |
| [qt/qwidget.qdoc](qt/qwidget.qdoc) | [URL](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/kernel/qwidget.cpp) | Comentarios `/*! */` del código fuente |
| [qt/qsettings.qdoc](qt/qsettings.qdoc) | [URL](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/corelib/io/qsettings.cpp) | Comentarios `/*! */` del código fuente |
| [qt/accessible.qdoc](qt/accessible.qdoc) | [URL](https://raw.githubusercontent.com/qt/qtdoc/v6.12.0/doc/src/frameworks-technologies/accessible.qdoc) |  |
| [systemd/systemd.exec.xml](systemd/systemd.exec.xml) | [URL](https://raw.githubusercontent.com/systemd/systemd/v257.13/man/systemd.exec.xml) | systemd 257, la versión de Debian 13 |
