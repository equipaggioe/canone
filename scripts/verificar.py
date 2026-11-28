# -*- coding: utf-8 -*-
"""Comprueba que un repositorio cumpla las convenciones de canone.

    python scripts/verificar.py --repo ../navetta
    python scripts/verificar.py --todos ..
    python scripts/verificar.py --canone

Con --canone comprueba las páginas, la plantilla y los workflows de canone.

Cada incumplimiento nombra el documento que escribe su regla. Falla con código 1 y la lista de
incumplimientos. Un incumplimiento que un ADR aceptado del repositorio nombra en «Se aparta de» se
informa aparte y no cuenta (documentacion.md, «Formato»).
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import re
import subprocess
import sys
import tomllib
import unicodedata
from pathlib import Path
from types import ModuleType

CANONE = Path(__file__).resolve().parent.parent
PLANTILLA = CANONE / "plantilla"
PAGINAS = {pagina.name for pagina in (CANONE / "plataformas").glob("*.md")}

# plataformas/README.md, «En desarrollo»: de una página que empieza con la nota no se exige nada.
# Solo cuenta la nota anterior a la primera sección.
NOTA = "> **En desarrollo; no se implementa"


def vigentes() -> set[str]:
    """Devuelve las páginas de plataformas/ que no están en desarrollo."""
    return {
        pagina
        for pagina in PAGINAS
        if NOTA not in (CANONE / "plataformas" / pagina).read_text(encoding="utf-8").split("\n## ", 1)[0]
    }

CANONICOS = [
    Path("server/alembic.ini"),
    Path("server/alembic/README"),
    Path("server/alembic/env.py"),
    Path("server/alembic/script.py.mako"),
    Path("server/src/app/__init__.py"),
    Path("server/src/app/database.py"),
    Path("server/src/app/tracing.py"),
    Path("server/src/app/openapi.py"),
    Path("server/src/app/models/__init__.py"),
    Path("server/src/app/models/base.py"),
    Path("server/src/app/models/event/__init__.py"),
    Path("server/src/app/models/ruff.toml"),
    Path("server/src/app/mock_data/__init__.py"),
    Path("server/src/app/routers/__init__.py"),
    Path("server/src/app/routers/problems.py"),
    Path("server/src/app/schemas/__init__.py"),
    Path("server/src/app/schemas/base.py"),
    Path("server/src/app/schemas/page.py"),
    Path("server/src/app/seeders/__init__.py"),
    Path("server/src/app/services/__init__.py"),
    Path("server/src/app/services/files.py"),
    Path("server/src/app/store.py"),
    Path("server/tests/__init__.py"),
    Path("server/tests/test_conventions.py"),
    Path("server/tests/test_events.py"),
    Path("server/tests/test_files.py"),
    Path("server/tests/test_tasks.py"),
]

# plataformas/fastapi.md, «Proyecto»: los de un servidor con cuentas, que es el que tiene models/account/.
CUENTAS = [
    Path("server/src/app/blocklist.txt"),
    Path("server/src/app/models/account/__init__.py"),
    Path("server/src/app/models/account/account.py"),
    Path("server/src/app/models/account/account_session.py"),
    Path("server/src/app/models/account/passkey.py"),
    Path("server/src/app/models/account/password.py"),
    Path("server/src/app/models/account/phone.py"),
    Path("server/src/app/models/account/push_fid.py"),
    Path("server/src/app/models/account/push_subscription.py"),
    Path("server/src/app/models/account/recovery.py"),
    Path("server/src/app/models/account/recovery_address.py"),
    Path("server/src/app/models/account/recovery_code.py"),
    Path("server/src/app/models/account/throttled.py"),
    Path("server/src/app/pages.py"),
    Path("server/src/app/routers/account.py"),
    Path("server/src/app/routers/accounts.py"),
    Path("server/src/app/routers/auth.py"),
    Path("server/src/app/routers/authorization.py"),
    Path("server/src/app/routers/fcm.py"),
    Path("server/src/app/routers/passkey.py"),
    Path("server/src/app/routers/password.py"),
    Path("server/src/app/routers/recovery.py"),
    Path("server/src/app/routers/sms.py"),
    Path("server/src/app/routers/web_push.py"),
    Path("server/src/app/routers/websocket.py"),
    Path("server/src/app/schemas/account.py"),
    Path("server/src/app/schemas/accounts.py"),
    Path("server/src/app/schemas/auth.py"),
    Path("server/src/app/schemas/authorization.py"),
    Path("server/src/app/schemas/fcm.py"),
    Path("server/src/app/schemas/web_push.py"),
    Path("server/src/app/schemas/websocket.py"),
    Path("server/src/app/services/account.py"),
    Path("server/src/app/services/accounts.py"),
    Path("server/src/app/services/attestation.py"),
    Path("server/src/app/services/authenticators.py"),
    Path("server/src/app/services/authorization.py"),
    Path("server/src/app/services/channel.py"),
    Path("server/src/app/services/clients.py"),
    Path("server/src/app/services/codes.py"),
    Path("server/src/app/services/fcm.py"),
    Path("server/src/app/services/limits.py"),
    Path("server/src/app/services/messages.py"),
    Path("server/src/app/services/notices.py"),
    Path("server/src/app/services/passkeys.py"),
    Path("server/src/app/services/passwords.py"),
    Path("server/src/app/services/push.py"),
    Path("server/src/app/services/recovery.py"),
    Path("server/src/app/services/registration.py"),
    Path("server/src/app/services/sessions.py"),
    Path("server/src/app/services/sms.py"),
    Path("server/src/app/services/web_push.py"),
    Path("server/src/app/services/websocket.py"),
    Path("server/src/app/translations.py"),
    Path("server/tests/authenticator.py"),
    Path("server/tests/test_account.py"),
    Path("server/tests/test_accounts.py"),
    Path("server/tests/test_authorization.py"),
    Path("server/tests/test_messages.py"),
    Path("server/tests/test_methods.py"),
    Path("server/tests/test_passkeys.py"),
    Path("server/tests/test_passwords.py"),
    Path("server/tests/test_push.py"),
    Path("server/tests/test_recovery.py"),
    Path("server/tests/test_registration.py"),
    Path("server/tests/test_sessions.py"),
    Path("server/tests/test_sms.py"),
    Path("server/tests/test_websocket.py"),
]

# Lo demás de plantilla/server/, que cada repositorio completa.
COMPLETABLES = [
    Path("server/alembic/versions/82f87036a005_accounts.py"),
    Path("server/alembic/versions/d34c1b992b0b_event_log.py"),
    Path("server/openapi.json"),
    Path("server/pyproject.toml"),
    Path("server/src/app/clients.py"),
    Path("server/src/app/colors.py"),
    Path("server/src/app/config.py"),
    Path("server/src/app/dependencies.py"),
    Path("server/src/app/enums.py"),
    Path("server/src/app/errors.py"),
    Path("server/src/app/ijson.py"),
    Path("server/src/app/locale/es/LC_MESSAGES/messages.po"),
    Path("server/src/app/main.py"),
    Path("server/src/app/methods.py"),
    Path("server/src/app/models/event/event_log.py"),
    Path("server/src/app/push.py"),
    Path("server/src/app/routers/health.py"),
    Path("server/src/app/schemas/health.py"),
    Path("server/src/app/services/events.py"),
    Path("server/src/app/services/health.py"),
    Path("server/src/app/services/transport.py"),
    Path("server/src/app/tasks.py"),
    Path("server/tests/conftest.py"),
    Path("server/tests/test_health.py"),
    Path("server/tests/test_transport.py"),
    Path("server/uv.lock"),
]

# plataformas/flet.md, «Código por SMS»: la extensión de Flet que lee el código del SMS.
SMS = [
    Path("packages/sms/.gitignore"),
    Path("packages/sms/pyproject.toml"),
    Path("packages/sms/src/flet_sms/__init__.py"),
    Path("packages/sms/src/flet_sms/sms.py"),
    Path("packages/sms/src/flutter/flet_sms/pubspec.yaml"),
    Path("packages/sms/src/flutter/flet_sms/lib/flet_sms.dart"),
    Path("packages/sms/src/flutter/flet_sms/lib/src/extension.dart"),
    Path("packages/sms/src/flutter/flet_sms/lib/src/sms_code.dart"),
]

# plataformas/autenticacion.md, «Passkeys»: el plugin de Flutter y la extensión de Flet que usan la
# passkey con la API del sistema, en Android, iOS, macOS y Windows.
PASSKEY = [
    Path("packages/passkey/.gitignore"),
    Path("packages/passkey/pyproject.toml"),
    Path("packages/passkey/src/flet_passkey/__init__.py"),
    Path("packages/passkey/src/flet_passkey/passkey.py"),
    Path("packages/passkey/src/flutter/flet_passkey/pubspec.yaml"),
    Path("packages/passkey/src/flutter/flet_passkey/lib/flet_passkey.dart"),
    Path("packages/passkey/src/flutter/flet_passkey/lib/src/extension.dart"),
    Path("packages/passkey/src/flutter/flet_passkey/lib/src/passkey_service.dart"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/pubspec.yaml"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/analysis_options.yaml"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/lib/passkey.dart"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/android/build.gradle.kts"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/android/settings.gradle.kts"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/android/src/main/AndroidManifest.xml"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/android/src/main/kotlin/canone/passkey/PasskeyPlugin.kt"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/darwin/passkey.podspec"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/darwin/passkey/Package.swift"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/darwin/passkey/Sources/passkey/PasskeyPlugin.swift"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/windows/CMakeLists.txt"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/windows/include/passkey/passkey_plugin_c_api.h"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/windows/passkey_plugin.cpp"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/windows/passkey_plugin.h"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/windows/passkey_plugin_c_api.cpp"),
    Path("packages/passkey/src/flutter/flet_passkey/passkey/test/windows_test.dart"),
]

# Una pieza se llama por dónde corre; el sufijo, cuando hay varias en el mismo lugar, es del
# dominio. `panel` y `landing` son las dos excepciones, con el nombre que ya usa la industria, y una
# pieza en Java, con `dependencies.txt`, lleva el nombre de su jar (java.md).
PREFIJOS = ("server", "web", "mobile", "desktop")
FIJAS = {"panel", "landing", "packages", "docs", "scripts", "brand"}


def nombre_valido(nombre: str) -> bool:
    if nombre in FIJAS:
        return True
    base, _, rol = nombre.partition("-")
    if base not in PREFIJOS:
        return False
    return rol.isidentifier() or not rol


def normalizar(texto: str) -> str:
    return texto.replace("\r\n", "\n").rstrip() + "\n"


# principios.md, «Nombres»: a lo sumo cuatro palabras. Se revisan las funciones, los métodos y las
# clases; las variables y los atributos se revisan leyendo, porque ahí caen los campos de una API
# externa. Las excepciones que se detectan solas: las pruebas, lo marcado como override, el código
# generado (lo que git ignora, o lo que lo dice en su cabecera) y el sufijo de las clases de
# schemas/.
MAXIMO_PALABRAS = 4
PRUEBAS = {"tests", "test", "androidTest", "integration_test"}
PALABRA = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z0-9]+|[A-Z]+")
DECLARACION = {
    ".dart": re.compile(
        r"^\s*(?:(?:static|external|abstract)\s+)*(?:class\s+(\w+)"
        r"|(?:void|bool|int|double|num|dynamic|[A-Z]\w*)(?:<[^()=;]*>)?\??\s+(\w+)\s*(?:<[^()]*>)?\()",
        re.M,
    ),
    ".kt": re.compile(r"^\s*(?:[a-z]+\s+)*(?:class|interface|object|fun)\s+(?:<[^>]*>\s*)?(?:\w+\.)?(\w+)", re.M),
    ".ts": re.compile(
        r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function\*?\s+(\w+)|class\s+(\w+)"
        r"|(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*(?::[^=]*)?=>)",
        re.M,
    ),
}
DECLARACION[".svelte"] = DECLARACION[".ts"]
OVERRIDE = {".dart": re.compile(r"@override\s*$"), ".kt": re.compile(r"\boverride\b"), ".ts": re.compile(r"\boverride\b")}
OVERRIDE[".svelte"] = OVERRIDE[".ts"]


def palabras(nombre: str) -> int:
    return len(PALABRA.findall(nombre.strip("_$")))


def generado(texto: str) -> bool:
    cabecera = texto[:500].lower()
    return "generated" in cabecera or "do not edit" in cabecera


def es_prueba(archivo: Path) -> bool:
    nombre = archivo.name
    return (
        bool(PRUEBAS & set(archivo.parts))
        or nombre.startswith("test_")
        or nombre == "conftest.py"
        or re.search(r"[._-](test|spec)\.\w+$", nombre) is not None
        or nombre.endswith(("_test.dart", "Test.kt"))
    )


def nombres_python(texto: str, en_schemas: bool) -> list[tuple[int, str, int]]:
    largos = []
    for nodo in ast.walk(ast.parse(texto)):
        if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        decoradores = {getattr(d, "id", getattr(d, "attr", "")) for d in nodo.decorator_list}
        if "override" in decoradores or nodo.name.startswith("test"):
            continue
        cuenta = palabras(nodo.name) - (1 if en_schemas and isinstance(nodo, ast.ClassDef) else 0)
        if cuenta > MAXIMO_PALABRAS:
            largos.append((nodo.lineno, nodo.name, cuenta))
    return largos


def nombres_otros(texto: str, sufijo: str) -> list[tuple[int, str, int]]:
    largos = []
    lineas = texto.splitlines()
    for coincidencia in DECLARACION[sufijo].finditer(texto):
        grupo = next(i for i, g in enumerate(coincidencia.groups(), 1) if g)
        nombre = coincidencia.group(grupo)
        linea = texto.count("\n", 0, coincidencia.start(grupo)) + 1
        anterior = lineas[linea - 2] if linea > 1 else ""
        if OVERRIDE[sufijo].search(lineas[linea - 1]) or OVERRIDE[sufijo].search(anterior):
            continue
        if nombre.startswith("test"):
            continue
        cuenta = palabras(nombre)
        if cuenta > MAXIMO_PALABRAS:
            largos.append((linea, nombre, cuenta))
    return largos


def listar(repo: Path) -> list[str]:
    """Lo que git sigue o seguiría: lo ignorado no es del repositorio."""
    return subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.splitlines()


# repositorio.md, «Scripts de shell»: POSIX ignora -e en un comando que empieza con !.
NEGACION = re.compile(r"^\s*!\s")
CON_E = re.compile(r"^\s*set\s+-[a-z]*e", re.M)


def negaciones(raiz: Path, archivos: list[str]) -> list[str]:
    """Las líneas que niegan un comando con ! en un script de sh con set -e: nunca lo cortan."""
    fallas: list[str] = []
    for rel in archivos:
        if not rel.endswith(".sh") or not (raiz / rel).is_file():
            continue
        texto = (raiz / rel).read_text(encoding="utf-8", errors="replace")
        if not CON_E.search(texto):
            continue
        for numero, linea in enumerate(texto.splitlines(), start=1):
            if NEGACION.match(linea):
                fallas.append(
                    f"repositorio.md: {rel}:{numero} niega con ! bajo set -e, y la línea nunca corta el script"
                )
    return fallas


def nombres_largos(repo: Path) -> list[str]:
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        sufijo = relativo.suffix
        archivo = repo / relativo
        if sufijo not in (".py", *DECLARACION) or es_prueba(relativo) or not archivo.is_file():
            continue
        texto = archivo.read_text(encoding="utf-8", errors="replace")
        if generado(texto):
            continue
        if sufijo == ".py":
            try:
                largos = nombres_python(texto, "schemas" in relativo.parts)
            except SyntaxError:
                fallas.append(f"principios.md: {relativo.as_posix()} no se pudo leer como Python")
                continue
        else:
            largos = nombres_otros(texto, sufijo)
        for linea, nombre, cuenta in largos:
            fallas.append(f"principios.md: {relativo.as_posix()}:{linea} {nombre} tiene {cuenta} palabras")
    return fallas


# principios.md, «Nombres»: un identificador no repite el nombre del repositorio. Se revisa la
# configuración, donde el prefijo del proyecto es costumbre: las claves de los `.env.example`, los
# `String.fromEnvironment` de Dart y el `env_prefix` de pydantic-settings.
CONFIGURACION = {
    ".dart": re.compile(r"String\.fromEnvironment\(\s*['\"](\w+)['\"]"),
    ".py": re.compile(r"env_prefix\s*=\s*['\"](\w+)['\"]"),
}
CLAVE_ENV = re.compile(r"^\s*(?:export\s+)?([A-Za-z_]\w*)\s*=", re.M)


def configuracion_con_repositorio(repo: Path) -> list[str]:
    proyecto = re.sub(r"\W", "_", repo.resolve().name).upper()
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        archivo = repo / relativo
        if relativo.name.endswith(".env.example"):
            patron = CLAVE_ENV
        elif relativo.suffix in CONFIGURACION:
            patron = CONFIGURACION[relativo.suffix]
        else:
            continue
        if not archivo.is_file():
            continue
        texto = archivo.read_text(encoding="utf-8", errors="replace")
        for coincidencia in patron.finditer(texto):
            nombre = coincidencia.group(1)
            if proyecto in nombre.upper().strip("_").split("_"):
                linea = texto.count("\n", 0, coincidencia.start(1)) + 1
                fallas.append(
                    f"principios.md: {relativo.as_posix()}:{linea} {nombre} repite el nombre del repositorio"
                )
    return fallas


# plataformas/transversal.md, «Tema»: los colores de cada cliente se generan desde brand/tokens/ con
# scripts/tokens.py, y lo generado está al día. Se usa la copia de canone, así una copia editada no
# se revisa a sí misma.
def generador() -> ModuleType:
    especificacion = importlib.util.spec_from_file_location("tokens", PLANTILLA / "scripts/tokens.py")
    assert especificacion and especificacion.loader
    tokens = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(tokens)
    return tokens


def colores_generados(repo: Path) -> list[str]:
    tokens = generador()
    try:
        clientes = tokens.outputs(repo)
    except tokens.TokenError as error:
        return [f"plataformas/transversal.md: {error}"]
    if not clientes:
        return []
    return [f"plataformas/transversal.md: {falla}" for falla in tokens.stale(repo)]


def colores_plantilla() -> list[str]:
    """Comprueba que los colores de plantilla/server/ salgan de plantilla/brand/tokens/."""
    tokens = generador()
    rel = Path("server/src/app/colors.py")
    if (PLANTILLA / rel).read_text(encoding="utf-8") != tokens.generate(PLANTILLA)[PLANTILLA / rel]:
        return [f"plataformas/transversal.md: plantilla/{rel.as_posix()} no sale de plantilla/brand/tokens/"]
    return []


def comparar(copia: Path, canonico: Path, nombre: str) -> list[str]:
    if not copia.exists():
        return [f"plantilla/README.md: falta {nombre}"]
    if normalizar(copia.read_text(encoding="utf-8")) != normalizar(
        canonico.read_text(encoding="utf-8")
    ):
        return [f"plantilla/README.md: {nombre} no coincide con el canónico de canone"]
    return []


# plataformas/fastapi.md, «Idiomas»: el catálogo de cada idioma traduce los textos de las cuentas.
LOCALE = Path("server/src/app/locale")
CATALOGO = Path("LC_MESSAGES/messages.po")
CADENA = re.compile(r'"((?:[^"\\]|\\.)*)"')


def textos(po: Path) -> dict[str, str]:
    """Devuelve cada msgid de un catálogo con su msgstr, vacío si es fuzzy: pybabel no lo compila."""
    encontrados: dict[str, str] = {}
    for entrada in re.split(r"\n\s*\n", po.read_text(encoding="utf-8")):
        partes: dict[str, str] = {}
        clave = ""
        for linea in entrada.splitlines():
            palabra, _, resto = linea.partition(" ")
            if not linea.startswith('"'):
                clave, linea = palabra, resto
            partes[clave] = partes.get(clave, "") + "".join(CADENA.findall(linea))
        if "msgid" in partes:
            fuzzy = re.search(r"^#,.*\bfuzzy\b", entrada, re.M)
            encontrados[partes["msgid"]] = "" if fuzzy else partes.get("msgstr", "")
    return encontrados


def catalogos(repo: Path) -> list[str]:
    """Comprueba que el catálogo de cada idioma del repositorio tenga los textos de la plantilla."""
    esperados = textos(PLANTILLA / LOCALE / "es" / CATALOGO)
    idiomas = {"es"} | {p.name for p in (repo / LOCALE).glob("*") if p.is_dir()}
    fallas: list[str] = []
    for idioma in sorted(idiomas):
        po = LOCALE / idioma / CATALOGO
        if not (repo / po).is_file():
            fallas.append(f"plataformas/fastapi.md: falta {po.as_posix()}")
            continue
        hallados = textos(repo / po)
        fallas.extend(
            f"plataformas/fastapi.md: {po.as_posix()} no traduce «{texto}»"
            for texto in esperados
            if not hallados.get(texto)
        )
    return fallas



# stack.md, «Versiones»: una tecnología lleva la misma versión en todas las piezas. Una fila que se
# repite en otro bloque lleva la misma versión, salvo la que dice «en lugar de».
def repetidas() -> list[str]:
    """Devuelve las filas de stack.md que repiten otra con otra versión."""
    vistas: dict[str, tuple[str, str]] = {}
    fallas = []
    titulo = ""
    for linea in (CANONE / "stack.md").read_text(encoding="utf-8").splitlines():
        if linea.startswith("## "):
            titulo = linea[3:].strip()
        elif linea.startswith("| ") and titulo in STACK and not linea.startswith(("| Se usa", "| :---")):
            celdas = [celda.strip() for celda in linea.strip("|").split(" | ")]
            if "en lugar de" in celdas[0] or celdas[0].startswith("La API de Android"):
                continue
            clave = celdas[0].split(",")[0].replace("`", "").strip()
            version = STACK[titulo][clave]
            if clave in vistas and vistas[clave][1] != version:
                fallas.append(
                    f"stack.md: {clave} lleva {vistas[clave][1]} en «{vistas[clave][0]}» y {version} en «{titulo}»"
                )
            vistas.setdefault(clave, (titulo, version))
    return fallas

def sin_clasificar() -> list[str]:
    """Los archivos de plantilla/server/ que ninguna lista nombra: nadie compararía su copia."""
    listados = {rel.as_posix() for rel in (*CANONICOS, *CUENTAS, *COMPLETABLES)}
    hallados = {rel for rel in listar(PLANTILLA) if rel.startswith("server/") and (PLANTILLA / rel).is_file()}
    return [f"plantilla/README.md: plantilla/{rel} no está en ninguna lista de verificar.py" for rel in sorted(hallados - listados)] + [
        f"plantilla/README.md: verificar.py nombra plantilla/{rel}, que no existe" for rel in sorted(listados - hallados)
    ]


# stack.md fija las versiones, y aquí no se repiten: se leen de sus tablas. La clave es la primera
# celda, sin lo que sigue a la coma, y el valor, la primera palabra de «Versión».
def leer_stack(texto: str) -> dict[str, dict[str, str]]:
    """Devuelve la versión de cada fila, por bloque."""
    bloques: dict[str, dict[str, str]] = {}
    titulo = ""
    tabla = False
    for linea in texto.splitlines():
        if linea.startswith("## "):
            titulo, tabla = linea[3:].strip(), False
        elif linea.startswith("| Se usa |"):
            tabla = True
        elif not linea.startswith("|"):
            tabla = False
        elif tabla and not linea.startswith("| :---"):
            celdas = [celda.strip() for celda in linea.strip("|").split(" | ")]
            # «La API de Android, en `compileSdk`» está tres veces: su clave es la celda entera.
            entera = celdas[0].startswith("La API de Android")
            clave = celdas[0] if entera else celdas[0].split(",")[0]
            clave = clave.replace("`", "").strip()
            filas = bloques.setdefault(titulo, {})
            if clave in filas:
                raise ValueError(f"stack.md: «{titulo}» tiene dos filas de {clave}")
            filas[clave] = celdas[1].split(" ")[0].rstrip(",")
    return bloques


STACK = leer_stack((CANONE / "stack.md").read_text(encoding="utf-8"))
# Los extras de cada fila que los nombra, como «stripe, con el extra `async`».
EXTRAS = {
    fila.lower(): set(re.findall(r"`(\w+)`", extras.split(" en ")[0]))
    for fila, extras in re.findall(
        r"^\| ([\w-]+), con (?:el extra|los extras) ([^|]+) \|", (CANONE / "stack.md").read_text(encoding="utf-8"), re.M
    )
}
ANDROID = STACK["Android"]
# stack.md, «Flet»: el plugin de packages/passkey/ compila con la API que encuentra el AGP de Flet.
PASSKEY_SDK = "La API de Android, en compileSdk de packages/passkey/"
CI = STACK["CI"]
DESPLIEGUE = STACK["Despliegue"]
FLUTTER = STACK["Flutter"]
SVELTEKIT = STACK["SvelteKit"]


def menos(bloque: str, *fuera: str) -> dict[str, str]:
    """Devuelve un bloque sin las filas nombradas, que tienen que existir."""
    filas = dict(STACK[bloque])
    for fila in fuera:
        del filas[fila]
    return filas


# stack.md, «Android»: una sola versión de Gradle, AGP y Kotlin en Android y en
# Flutter. Gradle sale del wrapper canónico; AGP y Kotlin, de los plugins que declara el proyecto:
# el catálogo de versiones en Android y settings.gradle.kts en Flutter. Kotlin va en el plugin que
# declara cada pieza: Android usa el Kotlin integrado en AGP, que no admite kotlin.android, y la
# plantilla de Flutter lo desactiva y declara kotlin.android.
WRAPPER = Path("gradle/wrapper/gradle-wrapper.properties")
AGP = ANDROID["AGP"]
KOTLIN = ANDROID["Kotlin"]
PLUGINS_ANDROID = {
    "com.android.application": AGP,
    "com.autonomousapps.dependency-analysis": ANDROID["El plugin com.autonomousapps.dependency-analysis"],
    "org.jetbrains.kotlin.plugin.compose": KOTLIN,
    "org.jetbrains.kotlin.plugin.serialization": KOTLIN,
    "org.jlleitschuh.gradle.ktlint": ANDROID["El plugin org.jlleitschuh.gradle.ktlint"],
}
# Los que una app declara solo si los usa.
PLUGINS_OPCIONALES = {
    "com.google.devtools.ksp": ANDROID["KSP"],
    "com.google.dagger.hilt.android": ANDROID["Hilt"],
    "com.google.gms.google-services": ANDROID["El plugin com.google.gms.google-services"],
    "org.openapi.generator": ANDROID["El plugin org.openapi.generator"],
}
PLUGINS_FLUTTER = {"com.android.application": AGP, "org.jetbrains.kotlin.android": KOTLIN}
# La fila de cada biblioteca del catálogo: gana el prefijo más largo.
BIBLIOTECAS = {
    "androidx.activity:": ANDROID["activity-compose"],
    "androidx.compose:compose-bom": ANDROID["El BOM de Compose"],
    "androidx.core:core": ANDROID["androidx.core:core"],
    "androidx.credentials:": ANDROID["androidx.credentials"],
    "androidx.datastore:": ANDROID["DataStore"],
    "androidx.hilt:hilt-lifecycle-viewmodel-compose": ANDROID["androidx.hilt:hilt-lifecycle-viewmodel-compose"],
    "androidx.lifecycle:": ANDROID["Lifecycle"],
    "androidx.navigation3:": ANDROID["Navigation 3"],
    "androidx.paging:": ANDROID["Paging"],
    "androidx.test.ext:junit": ANDROID["androidx.test.ext:junit"],
    "androidx.test:runner": ANDROID["androidx.test:runner"],
    "androidx.work:": ANDROID["WorkManager"],
    "com.google.android.gms:play-services-auth-api-phone": ANDROID["play-services-auth-api-phone"],
    "com.google.dagger:": ANDROID["Hilt"],
    "com.google.firebase:firebase-bom": ANDROID["El BOM de Firebase"],
    "com.squareup.okhttp3:logging-interceptor": ANDROID["logging-interceptor"],
    "com.squareup.okhttp3:mockwebserver3": ANDROID["mockwebserver3"],
    "com.squareup.okhttp3:okhttp": ANDROID["OkHttp"],
    "com.squareup.retrofit2:converter-kotlinx-serialization": ANDROID["converter-kotlinx-serialization"],
    "com.squareup.retrofit2:converter-scalars": ANDROID["converter-scalars"],
    "com.squareup.retrofit2:retrofit": ANDROID["Retrofit"],
    "com.stripe:stripe-android": ANDROID["stripe-android"],
    "javax.inject:javax.inject": ANDROID["javax.inject"],
    "junit:junit": ANDROID["JUnit"],
    "org.jetbrains.kotlinx:kotlinx-coroutines-": ANDROID["kotlinx-coroutines-core"],
    "org.jetbrains.kotlinx:kotlinx-coroutines-test": ANDROID["kotlinx-coroutines-test"],
    "org.jetbrains.kotlinx:kotlinx-serialization-": ANDROID["kotlinx-serialization-json"],
    "org.maplibre.gl:android-sdk": ANDROID["MapLibre Android"],
}
# android.md, «Proyecto» y «Estilo»: lo que declara app/build.gradle.kts.
SDK = {
    "compileSdk": ANDROID["La API de Android, en compileSdk"],
    "ktlint": ANDROID["ktlint"],
    "minSdk": ANDROID["La API de Android, en minSdk"],
    "targetSdk": ANDROID["La API de Android, en targetSdk"],
}
PLUGIN_KTS = re.compile(r'id\("([\w.]+)"\)\s+version\s+"([^"]+)"')


def plugins_catalogo(catalogo: Path) -> dict[str, str]:
    datos = tomllib.loads(catalogo.read_text(encoding="utf-8"))
    versiones = datos.get("versions", {})
    declarados = {}
    for plugin in datos.get("plugins", {}).values():
        if isinstance(plugin, str):
            nombre, _, version = plugin.partition(":")
        else:
            nombre, version = plugin["id"], plugin.get("version", "")
            if isinstance(version, dict):
                version = versiones.get(version.get("ref"), "")
        declarados[nombre] = version
    return declarados


def versiones_bibliotecas(catalogo: Path, nombre: str) -> list[str]:
    """Compara con stack.md la versión de cada biblioteca y de cada plugin opcional del catálogo."""
    datos = tomllib.loads(catalogo.read_text(encoding="utf-8"))
    versiones = datos.get("versions", {})
    fallas = []
    for biblioteca in datos.get("libraries", {}).values():
        if isinstance(biblioteca, str):
            grupo, artefacto, *resto = biblioteca.split(":")
            modulo, version = f"{grupo}:{artefacto}", resto[0] if resto else ""
        else:
            modulo = biblioteca.get("module") or f"{biblioteca['group']}:{biblioteca['name']}"
            version = biblioteca.get("version", "")
            if isinstance(version, dict):
                version = versiones.get(version.get("ref"), "")
        prefijos = [prefijo for prefijo in BIBLIOTECAS if modulo.startswith(prefijo)]
        # Sin versión, la pone el BOM.
        if prefijos and version:
            esperada = BIBLIOTECAS[max(prefijos, key=len)]
            if version != esperada:
                fallas.append(f"stack.md: {nombre} declara {modulo} {version}, no {esperada}")
    for plugin, version in plugins_catalogo(catalogo).items():
        esperada = PLUGINS_OPCIONALES.get(plugin, version)
        if version != esperada:
            fallas.append(f"stack.md: {nombre} declara {plugin} {version}, no {esperada}")
    return fallas


def versiones_sdk(app: Path) -> list[str]:
    """Compara con stack.md las API de Android y el ktlint de app/build.gradle.kts."""
    build = app / "app/build.gradle.kts"
    texto = sin_comentarios(build.read_text(encoding="utf-8")) if build.exists() else ""
    compila = re.search(r"release\((\d+)\)\s*\{\s*minorApiLevel\s*=\s*(\d+)", texto)
    ktlint = re.search(r"ktlint\s*\{[^}]*\bversion(?:\.set\(|\s*=\s*)\"([^\"]+)\"", texto)
    declarados = {
        "compileSdk": f"{compila[1]}.{compila[2]}" if compila else None,
        "ktlint": ktlint[1] if ktlint else None,
    }
    for nivel in ("minSdk", "targetSdk"):
        coincide = re.search(rf"\b{nivel}\s*=\s*(\d+)", texto)
        declarados[nivel] = coincide[1] if coincide else None
    return [
        f"stack.md: {app.name}/app/build.gradle.kts declara {nombre} {declarados[nombre] or 'sin versión'}, no {version}"
        for nombre, version in SDK.items()
        if declarados[nombre] != version
    ]


def versiones_gradle(
    nombre: str, declarados: dict[str, str], plugins: dict[str, str]
) -> list[str]:
    fallas: list[str] = []
    for plugin, version in plugins.items():
        if declarados.get(plugin) != version:
            fallas.append(
                f"stack.md: {nombre} declara {plugin} {declarados.get(plugin, 'sin versión')}, no {version}"
            )
    return fallas


# plataformas/sveltekit.md, «Pruebas»: la versión de Playwright de stack.md en todo package.json
# del repositorio, porque cada versión descarga sus propios navegadores.
PLAYWRIGHT = SVELTEKIT["Playwright"]

# plataformas/sveltekit.md, «CSP»: lo que vite.config.ts fija de la CSP, con el objeto que lo
# contiene. script-src admite, además de 'self', los orígenes https de una pasarela de pago, y
# ninguna palabra clave como 'unsafe-inline' o 'strict-dynamic'.
Q = r"['\"]"
CSP = {
    "mode: 'hash'": ("csp", rf"\bmode\s*:\s*{Q}hash{Q}"),
    "script-src 'self'": (
        "directives",
        rf"{Q}script-src{Q}\s*:\s*\[\s*{Q}self{Q}(\s*,\s*{Q}https://[^'\"\s]+{Q})*\s*,?\s*\]",
    ),
    "object-src 'none'": ("directives", rf"{Q}object-src{Q}\s*:\s*\[\s*{Q}none{Q}\s*\]"),
    "base-uri 'none'": ("directives", rf"{Q}base-uri{Q}\s*:\s*\[\s*{Q}none{Q}\s*\]"),
    "form-action 'self'": ("directives", rf"{Q}form-action{Q}\s*:\s*\[\s*{Q}self{Q}\s*\]"),
    "style-src-attr 'unsafe-inline'": (
        "directives",
        rf"{Q}style-src-attr{Q}\s*:\s*\[\s*{Q}unsafe-inline{Q}\s*\]",
    ),
    "assetsInlineLimit: 0": ("build", r"\bassetsInlineLimit\s*:\s*0\b"),
}


def sin_comentarios(codigo: str) -> str:
    """El código JavaScript sin sus comentarios: una opción comentada no rige."""
    salida, i, comilla = [], 0, ""
    while i < len(codigo):
        letra = codigo[i]
        if comilla:
            salida.append(codigo[i : i + 2] if letra == "\\" else letra)
            if letra == "\\":
                i += 2
                continue
            if letra == comilla:
                comilla = ""
        elif letra in "'\"`":
            comilla = letra
            salida.append(letra)
        elif codigo.startswith("//", i):
            fin = codigo.find("\n", i)
            i = len(codigo) if fin < 0 else fin
            continue
        elif codigo.startswith("/*", i):
            fin = codigo.find("*/", i + 2)
            i = len(codigo) if fin < 0 else fin + 2
            continue
        else:
            salida.append(letra)
        i += 1
    return "".join(salida)


def objeto(codigo: str, clave: str) -> str:
    """El contenido del primer objeto literal de la clave, o vacío si no está."""
    coincide = re.search(rf"(?<![\w$]){clave}\s*:\s*\{{", codigo)
    if not coincide:
        return ""
    profundidad = 1
    for posicion in range(coincide.end(), len(codigo)):
        profundidad += {"{": 1, "}": -1}.get(codigo[posicion], 0)
        if profundidad == 0:
            return codigo[coincide.end() : posicion]
    return ""


def vite_sveltekit(vite: Path) -> list[str]:
    """Lo que vite.config.ts fija del proxy y de la CSP, sin contar lo comentado."""
    nombre = vite.parent.name
    codigo = sin_comentarios(vite.read_text(encoding="utf-8")) if vite.exists() else ""
    fallas = []
    # «Carga de datos»: server.proxy manda /api al servidor, también el WebSocket.
    api = objeto(objeto(objeto(codigo, "server"), "proxy"), rf"{Q}/api{Q}")
    if not (
        re.search(rf"\btarget\s*:\s*{Q}http://localhost:8000{Q}", api)
        and re.search(r"\bws\s*:\s*true\b", api)
    ):
        fallas.append(f"plataformas/sveltekit.md: {nombre}/vite.config.ts no manda /api al servidor")
    csp = objeto(codigo, "csp")
    bloques = {"csp": csp, "directives": objeto(csp, "directives"), "build": objeto(codigo, "build")}
    for requisito, (bloque, patron) in CSP.items():
        if not re.search(patron, bloques[bloque]):
            fallas.append(f"plataformas/sveltekit.md: {nombre}/vite.config.ts no fija {requisito}")
    return fallas


def versiones_playwright(repo: Path) -> list[str]:
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        if relativo.name != "package.json" or not (repo / relativo).is_file():
            continue
        datos = json.loads((repo / relativo).read_text(encoding="utf-8"))
        deps = {**datos.get("dependencies", {}), **datos.get("devDependencies", {})}
        for paquete in ("playwright", "@playwright/test"):
            if paquete in deps and deps[paquete] != PLAYWRIGHT:
                fallas.append(
                    f"stack.md: {relativo.as_posix()} declara {paquete} {deps[paquete]}, no {PLAYWRIGHT}"
                )
    return fallas


# plataformas/python.md, «Proyecto», y stack.md: una sola versión exacta de uv en todo
# pyproject.toml, la misma con que el servidor crea el entorno.
UV = STACK["Python"]["uv"]


def versiones_uv(repo: Path) -> list[str]:
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        if relativo.name != "pyproject.toml" or not (repo / relativo).is_file():
            continue
        datos = tomllib.loads((repo / relativo).read_text(encoding="utf-8"))
        declarada = datos.get("tool", {}).get("uv", {}).get("required-version")
        if declarada is None:
            fallas.append(f"plataformas/python.md: {relativo.as_posix()} no declara required-version")
        elif declarada != f"=={UV}":
            fallas.append(f"stack.md: {relativo.as_posix()} declara uv {declarada}, no =={UV}")
    return fallas


# plataformas/python.md, «Proyecto»: las dependencias y la configuración de pytest van en el
# pyproject.toml de la pieza. Cualquiera de los archivos de pytest le gana aunque esté vacío.
SUELTOS = ("requirements.txt", "pytest.ini", ".pytest.ini", "pytest.toml", ".pytest.toml")


def configuracion_suelta(repo: Path) -> list[str]:
    """Devuelve los archivos que dejan fuera de pyproject.toml lo que va en él."""
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        if relativo.name != "pyproject.toml" or not (repo / relativo).is_file():
            continue
        for nombre in SUELTOS:
            if (repo / relativo.parent / nombre).exists():
                suelto = (relativo.parent / nombre).as_posix()
                fallas.append(f"plataformas/python.md: {suelto}; va en pyproject.toml")
    return fallas


# stack.md: fija las versiones, y los manifiestos y los workflows de cada repositorio las siguen.
# Van por página, para saltar las de las páginas que están en desarrollo.
PYPI = {
    "OpenTelemetry": ("opentelemetry-api", "opentelemetry-sdk"),
    "PySide6 y Qt": ("pyside6",),
    "valkey-py": ("valkey",),
}


def pypi(filas: dict[str, str]) -> dict[str, str]:
    """Devuelve el requisito que declara pyproject.toml de cada fila de un bloque."""
    return {
        nombre: f">={version}"
        for fila, version in filas.items()
        for nombre in PYPI.get(fila, (fila.lower().replace("_", "-"),))
    }


def tope(version: str) -> str:
    """Devuelve la serie que sigue, con la que pyproject.toml acota uv_build."""
    mayor, menor, _ = version.split(".")
    return f"{mayor}.{int(menor) + 1}"


PYPROJECT = {
    "autenticacion.md": pypi(STACK["Autenticación"]),
    "fastapi.md": pypi(STACK["FastAPI"]),
    "flet.md": pypi(
        menos("Flet", "Flutter", "AGP", PASSKEY_SDK, "Pydantic", "Inno Setup", "appimagetool", "smart_auth")
    ),
    "postgres.md": pypi(menos("PostgreSQL", "PostgreSQL", "PostGIS")),
    "python.md": pypi(menos("Python", "Python", "uv")),
    "qt.md": pypi(STACK["Qt"]),
}
PYPROJECT["python.md"]["uv-build"] += f",<{tope(STACK['Python']['uv_build'])}"
REQUISITO = re.compile(r"^\s*([A-Za-z0-9._-]+)\s*(?:\[[^\]]*\])?\s*([^;]*)")
NPM_NOMBRES = {
    "ESLint": "eslint",
    "MapLibre GL JS": "maplibre-gl",
    "Paraglide": "@inlang/paraglide-js",
    "Prettier": "prettier",
    "Svelte": "svelte",
    "SvelteKit": "@sveltejs/kit",
    "TypeScript": "typescript",
    "UnoCSS": "unocss",
    "Vite": "vite",
    "Vitest": "vitest",
}
# Playwright va aparte: se exige en todo package.json, no solo en el de una superficie.
NPM = {
    NPM_NOMBRES.get(fila, fila): version
    for fila, version in menos("SvelteKit", "Node", "pnpm", "Playwright").items()
}
PNPM = SVELTEKIT["pnpm"]
PUB = menos("Flutter", "Flutter", "Dart", "flutter_localizations", "flutter_test") | {"smart_auth": STACK["Flet"]["smart_auth"]}
# plataformas/flutter.md, «Proyecto»: las mutations de Riverpod son experimentales y pueden cambiar
# sin una versión mayor, así que sus paquetes van sin ^.
EXACTOS = {"flutter_riverpod", "riverpod_annotation", "riverpod_generator"}
CONTENEDOR = "El contenedor "
ACCIONES = {fila: version for fila, version in CI.items() if not fila.startswith(CONTENEDOR)}
CONTENEDORES = {fila.removeprefix(CONTENEDOR): version for fila, version in CI.items() if fila.startswith(CONTENEDOR)}
# La versión de cada acción la exigen las páginas que la usan.
ENTRADAS = {
    "actions/setup-java": ({"android.md", "flutter.md", "java.md"}, "java-version", ANDROID["JDK"]),
    "actions/setup-node": ({"sveltekit.md"}, "node-version", SVELTEKIT["Node"]),
    "actions/setup-python": ({"python.md"}, "python-version", STACK["Python"]["Python"]),
}
# plataformas/flet.md: el índice de Flet para Android no trae el pydantic-core de la Pydantic del
# bloque de Python de stack.md.
FLET = {"pydantic": f"=={STACK['Flet']['Pydantic']}"}
# stack.md, «Versiones»: la plantilla y los scripts de Canone no declaran una versión que stack.md no
# estipule. Cada archivo lleva la de su fila en el grupo de su expresión.
PROGRAMAS = [
    (".github/workflows/infra.yml", r"rest-server_(\d[\d.]*\d)_linux", DESPLIEGUE["rest-server"]),
    (".github/workflows/infra.yml", r"playwright==([\d.]+)", STACK["FastAPI"]["Playwright"]),
    ("plantilla/android/gradle/wrapper/gradle-wrapper.properties", r"gradle-([\d.]+)-bin", ANDROID["Gradle"]),
    ("plantilla/flet/build-appimage.sh", r"appimagetool/releases/download/([\d.]+)/", STACK["Flet"]["appimagetool"]),
    ("plantilla/flutter/analysis_options.yaml", r"riverpod_lint: (\S+)", FLUTTER["riverpod_lint"]),
    ("plantilla/infra/caddy.pref", r"Pin: version (\d+\.\d+)\.\*", DESPLIEGUE["Caddy"]),
    ("plantilla/infra/packages.py", r"postgresql-(\d+)-postgis", STACK["PostgreSQL"]["PostgreSQL"]),
    ("plantilla/infra/packages.py", r"openjdk-(\d+)-jre", STACK["Java"]["Java"]),
    ("plantilla/infra/uv.py", r'^VERSION = "([^"]+)"', UV),
    (
        "plantilla/packages/passkey/src/flutter/flet_passkey/passkey/android/build.gradle.kts",
        r"androidx\.credentials:[\w-]+:([\d.]+)",
        ANDROID["androidx.credentials"],
    ),
    (
        "plantilla/packages/passkey/src/flutter/flet_passkey/passkey/android/build.gradle.kts",
        r"compileSdk = (\d+)",
        STACK["Flet"][PASSKEY_SDK],
    ),
    ("plantilla/receiver/backup.ps1", r'\$version = "([^"]+)"', DESPLIEGUE["rest-server"]),
    ("plantilla/receiver/backup.ps1", r"restic (\d[\d.]*\d)", DESPLIEGUE["restic"]),
    ("plantilla/receiver/backup.sh", r"^version=(\S+)", DESPLIEGUE["rest-server"]),
    ("plantilla/receiver/backup.sh", r"restic (\d[\d.]*\d)", DESPLIEGUE["restic"]),
    ("plantilla/scripts/java.py", r'^RELEASE = "(\d+)"', STACK["Java"]["Java"]),
    ("plantilla/scripts/java.py", r'"google-java-format",\s+"([^"]+)"', STACK["Java"]["google-java-format"]),
    ("plantilla/scripts/play.py", r"google-auth(?:\[\w+\])?>=([\d.]+)", STACK["FastAPI"]["google-auth"]),
    ("plantilla/scripts/play.py", r'required-version = "==([^"]+)"', UV),
    ("scripts/infra/browser.sh", r"playwright==([\d.]+)", STACK["FastAPI"]["Playwright"]),
]
METASPACE = "-XX:MaxMetaspaceSize=2g"


def versiones_pyproject(repo: Path, paginas: set[str]) -> list[str]:
    versiones = {
        nombre: version
        for pagina in sorted(paginas & PYPROJECT.keys())
        for nombre, version in PYPROJECT[pagina].items()
    }
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        if relativo.name != "pyproject.toml" or not (repo / relativo).is_file():
            continue
        datos = tomllib.loads((repo / relativo).read_text(encoding="utf-8"))
        proyecto = list(datos.get("project", {}).get("dependencies", []))
        requisitos = list(proyecto)
        requisitos += datos.get("build-system", {}).get("requires", [])
        for grupo in datos.get("dependency-groups", {}).values():
            requisitos += [r for r in grupo if isinstance(r, str)]
        es_flet = "flet.md" in paginas and "flet" in datos.get("tool", {})
        declarados: dict[str, set[str]] = {}
        for requisito in requisitos:
            coincide = REQUISITO.match(requisito)
            nombre = coincide[1].lower().replace("_", "-")
            declarado = coincide[2].replace(" ", "")
            extras = re.search(r"\[([^\]]*)\]", requisito)
            declarados.setdefault(nombre, set()).update(
                extra.strip() for extra in (extras[1].split(",") if extras else [])
            )
            esperado = versiones.get(nombre)
            if esperado is None:
                continue
            # plataformas/flet.md: flet build no lee uv.lock, así que [project] va con ==.
            if es_flet and requisito in proyecto:
                esperado = FLET.get(nombre, "==" + esperado.removeprefix(">="))
            if declarado != esperado:
                fallas.append(
                    f"stack.md: {relativo.as_posix()} declara {nombre}{declarado}, no {esperado}"
                )
        # Solo la pieza: un paquete de packages/ usa lo que le da la pieza que lo instala.
        if len(relativo.parts) == 2:
            for nombre, extras in EXTRAS.items():
                if nombre in declarados and nombre in versiones and not extras <= declarados[nombre]:
                    faltan = ", ".join(sorted(extras - declarados[nombre]))
                    fallas.append(f"stack.md: {relativo.as_posix()} declara {nombre} sin el extra {faltan}")
    return fallas


def versiones_package(superficie: Path, datos: dict, deps: dict[str, str]) -> list[str]:
    fallas = []
    if not re.fullmatch(rf"pnpm@{re.escape(PNPM)}(\+\S+)?", datos.get("packageManager", "")):
        fallas.append(f"stack.md: {superficie.name}/package.json no declara pnpm@{PNPM}")
    for paquete, version in NPM.items():
        if paquete in deps and deps[paquete] != version:
            fallas.append(
                f"stack.md: {superficie.name}/ declara {paquete} {deps[paquete]}, no {version}"
            )
    return fallas


# plataformas/sveltekit.md, «Carga de datos»: los tipos de la API se generan antes de dev y check.
API = "openapi-typescript ../server/openapi.json -o src/lib/api/schema.d.ts"


def scripts_package(superficie: Path, datos: dict) -> list[str]:
    scripts = datos.get("scripts", {})
    fallas = []
    if scripts.get("api") != API:
        fallas.append(f"plataformas/sveltekit.md: {superficie.name}/package.json no tiene el script api: {API}")
    for nombre in ("dev", "check"):
        if not scripts.get(nombre, "").startswith("pnpm api && "):
            fallas.append(f"plataformas/sveltekit.md: el script {nombre} de {superficie.name}/ no empieza por pnpm api &&")
    return fallas


# plataformas/flutter.md, «OpenAPI y clientes»: el modo por defecto de swagger_parser acepta un solo
# 2xx con cuerpo, y rechaza el 201 de un PUT que crea.
GENERACION_SWAGGER = {"serializer": "freezed", "http_client": "http", "response_mode": "all_statuses"}


def generacion_swagger(repo: Path) -> list[str]:
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        if relativo.name != "swagger_parser.yaml" or not (repo / relativo).is_file():
            continue
        texto = (repo / relativo).read_text(encoding="utf-8")
        bloque = re.search(r"^  generation:\n((?:    .*\n?)*)", texto, re.M)
        declarados = dict(re.findall(r"^    (\w+):[ \t]*(\S+)", bloque[1], re.M)) if bloque else {}
        for clave, valor in GENERACION_SWAGGER.items():
            if declarados.get(clave) != valor:
                fallas.append(
                    f"plataformas/flutter.md: {relativo.as_posix()} no lleva {clave}: {valor} en generation"
                )
    return fallas


def versiones_pubspec(repo: Path) -> list[str]:
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        if relativo.name != "pubspec.yaml" or not (repo / relativo).is_file():
            continue
        seccion = ""
        for linea in (repo / relativo).read_text(encoding="utf-8").splitlines():
            if coincide := re.match(r"(\w+):", linea):
                seccion = coincide[1]
            coincide = re.match(r"\s+(\w+):[ \t]*[\"']?([^\"'\s#]+)", linea)
            if not coincide:
                continue
            paquete, declarada = coincide.groups()
            if seccion in {"dependencies", "dev_dependencies", "dependency_overrides"} and paquete in PUB:
                version = PUB[paquete]
                if (declarada if paquete in EXACTOS else declarada.lstrip("^")) != version:
                    fallas.append(
                        f"stack.md: {relativo.as_posix()} declara {paquete} {declarada}, no {version}"
                    )
            # Solo la pieza: un paquete de packages/ declara el rango que admite.
            elif (seccion, paquete) == ("environment", "sdk") and len(relativo.parts) == 2:
                if declarada != f"^{FLUTTER['Dart']}":
                    fallas.append(f"stack.md: {relativo.as_posix()} declara sdk {declarada}, no ^{FLUTTER['Dart']}")
    return fallas


def versiones_programas() -> list[str]:
    fallas = []
    for ruta, expresion, version in PROGRAMAS:
        declaradas = set(re.findall(expresion, (CANONE / ruta).read_text(encoding="utf-8"), re.M))
        if declaradas != {version}:
            fallas.append(f"stack.md: {ruta} lleva {', '.join(sorted(declaradas)) or 'ninguna versión'}, no {version}")
    return fallas


def flutters(repo: Path) -> set[str]:
    """Devuelve el Flutter de cada tipo de pieza del repositorio: Flet construye con el que pide."""
    versiones = set()
    if repo == PLANTILLA or any(repo.glob("*/pubspec.yaml")):
        versiones.add(FLUTTER["Flutter"])
    for pyproject in repo.glob("*/pyproject.toml"):
        if "flet" in tomllib.loads(pyproject.read_text(encoding="utf-8")).get("tool", {}):
            versiones.add(STACK["Flet"]["Flutter"])
    return versiones


def versiones_workflows(repo: Path, paginas: set[str]) -> list[str]:
    fallas = []
    esperados = flutters(repo)
    for ruta in sorted((repo / ".github/workflows").glob("*.yml")):
        relativo = ruta.relative_to(repo).as_posix()
        texto = ruta.read_text(encoding="utf-8")
        pares = re.findall(r"uses:\s*([\w./-]+)@(\S+)", texto)
        usadas = {accion for accion, _ in pares}
        for accion, declarada in pares:
            if accion in ACCIONES and declarada != ACCIONES[accion]:
                fallas.append(f"stack.md: {relativo} usa {accion}@{declarada}, no @{ACCIONES[accion]}")
        for accion, (exigen, entrada, version) in ENTRADAS.items():
            valores = re.findall(rf"{entrada}:\s*[\"']?([^\"'\s]+)", texto)
            if exigen & paginas and accion in usadas and set(valores) != {version}:
                fallas.append(f"stack.md: {relativo} no declara {entrada} {version}")
        valores = set(re.findall(r"flutter-version:\s*[\"']?([^\"'\s]+)", texto))
        if esperados and "subosito/flutter-action" in usadas and valores != esperados:
            fallas.append(f"stack.md: {relativo} no declara flutter-version {' y '.join(sorted(esperados))}")
        for contenedor, etiqueta in re.findall(r"\b(?:image|container):\s*[\"']?([\w./-]+):([\w.-]+)", texto):
            esperada = CONTENEDORES.get(contenedor, etiqueta)
            if etiqueta != esperada:
                fallas.append(f"stack.md: {relativo} usa {contenedor}:{etiqueta}, no {esperada}")
    return fallas


# java.md, «Entrega» and «Pruebas»: release.yml builds each piece in Java, a folder of the root
# with dependencies.txt, and ci.yml builds it and starts it for the tests.
PIEZA_JAVA = re.compile(r"scripts/java\.py ([a-z][a-z0-9-]*) ")


def piezas_java(repo: Path) -> list[str]:
    carpetas = {p.name for p in repo.iterdir() if (p / "dependencies.txt").is_file()}
    workflows = repo / ".github/workflows"
    release, ci = (
        (workflows / nombre).read_text(encoding="utf-8") if (workflows / nombre).exists() else ""
        for nombre in ("release.yml", "ci.yml")
    )
    publicadas = set(PIEZA_JAVA.findall(release))
    fallas = [f"plataformas/java.md: release.yml no compila {p}/" for p in sorted(carpetas - publicadas)]
    fallas += [
        f"plataformas/java.md: release.yml compila {p}, que no es una carpeta con dependencies.txt"
        for p in sorted(publicadas - carpetas)
    ]
    for pieza in sorted(carpetas):
        arranca = rf"java -jar \S*{pieza}/build/{pieza}/{pieza}\.jar"
        if f"scripts/java.py {pieza} " not in ci or not re.search(arranca, ci):
            fallas.append(f"plataformas/java.md: ci.yml no compila y arranca {pieza}/")
    return fallas


# qt.md y flet.md, «Proyecto»: el árbol completo es la convención. Cada pieza nombra la carpeta
# de src/ en la que va el código, las carpetas que tiene ahí y los archivos que admite cada una,
# relativos a src/. Una carpeta que el árbol no tiene se nombra una sola vez.
ARBOLES = {
    "qt.md": (
        "app/",
        {"assets", "translations", "api", "services", "windows", "dialogs", "widgets", "models"},
        [
            r"app/(__init__|main|colors|theme)\.py",
            r"app/(icon\.png|resources\.qrc)",
            r"app/assets/.+",
            r"app/translations/[^/]+\.ts",
            r"app/api/([^/]+\.py|ruff\.toml)",
            r"app/services/([^/]+\.py|ruff\.toml|[^/]+/[^/]+\.py)",
            r"app/windows/(__init__|main_window)\.py",
            r"app/(dialogs|widgets|models)/[^/]+\.py",
        ],
    ),
    "flet.md": (
        "",
        {"assets", "api", "services", "locales", "views"},
        [
            r"(main|colors|theme)\.py",
            r"assets/icon\.png",
            r"api/([^/]+\.py|ruff\.toml)",
            r"services/([^/]+\.py|[^/]+/[^/]+\.py)",
            r"locales/[^/]+/LC_MESSAGES/{pieza}\.po",
            r"views/[^/]+\.py",
        ],
    ),
}
# qt.md y flet.md, «Proyecto» y «Tema»: los archivos de la pieza que se copian sin editar.
COPIAS_SRC = {
    "qt.md": [
        Path("src/app/api/ruff.toml"),
        Path("src/app/services/ruff.toml"),
        Path("src/app/services/language.py"),
        Path("tests/test_theme.py"),
        Path("tests/test_accessibility.py"),
    ],
    "flet.md": [Path("src/api/ruff.toml"), Path("tests/test_theme.py")],
}
# qt.md, «Proyecto»: un módulo de estas carpetas es una sola clase pública, con su nombre.
POR_CLASE = ("dialogs", "widgets", "models")


def piezas_python(repo: Path) -> dict[str, str]:
    """Devuelve las piezas de Qt y de Flet del repositorio, con su página."""
    piezas = {}
    for pyproject in sorted(repo.glob("*/pyproject.toml")):
        if "flet" in tomllib.loads(pyproject.read_text(encoding="utf-8")).get("tool", {}):
            piezas[pyproject.parent.name] = "flet.md"
    if (repo / "desktop").is_dir() and "desktop" not in piezas:
        piezas["desktop"] = "qt.md"
    return piezas


def fuera_del_arbol(repo: Path, pieza: str, pagina: str) -> list[str]:
    """Devuelve lo que hay en src/ de la pieza y su árbol no tiene."""
    raiz, carpetas, patrones = ARBOLES[pagina]
    patrones = [patron.format(pieza=re.escape(pieza)) for patron in patrones]
    base = f"{pieza}/src/"
    sobrantes: set[str] = set()
    for ruta in listar(repo):
        if not ruta.startswith(base):
            continue
        relativa = ruta.removeprefix(base)
        if any(re.fullmatch(patron, relativa) for patron in patrones):
            continue
        partes = relativa.removeprefix(raiz).split("/")
        if not relativa.startswith(raiz):
            primera = relativa.split("/")[0]
            sobrantes.add(base + primera + ("/" if "/" in relativa else ""))
        elif len(partes) > 1 and partes[0] not in carpetas:
            sobrantes.add(base + raiz + partes[0] + "/")
        else:
            sobrantes.add(ruta)
    return [f"plataformas/{pagina}: {ruta} no está en el árbol de «Proyecto»" for ruta in sorted(sobrantes)]


def serpiente(nombre: str) -> str:
    """Devuelve el nombre de una clase en snake_case, como su módulo."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", nombre).lower()


def modulos_por_clase(repo: Path, pieza: str) -> list[str]:
    """Devuelve los módulos de dialogs/, widgets/ y models/ que no son una sola clase."""
    fallas = []
    for ruta in listar(repo):
        carpeta = Path(ruta).parent
        if carpeta.parent.as_posix() != f"{pieza}/src/app" or carpeta.name not in POR_CLASE:
            continue
        if not ruta.endswith(".py") or ruta.endswith("/__init__.py"):
            continue
        arbol = ast.parse((repo / ruta).read_text(encoding="utf-8"))
        clases = [
            nodo.name
            for nodo in arbol.body
            if isinstance(nodo, ast.ClassDef) and not nodo.name.startswith("_")
        ]
        if [serpiente(clase) for clase in clases] != [Path(ruta).stem]:
            declara = ", ".join(clases) or "ninguna clase pública"
            fallas.append(f"plataformas/qt.md: {ruta} declara {declara}, no una sola clase con su nombre")
    return fallas


# plataformas/android.md, «Proyecto»: con el JDK 25, Android Lint agota 512 MB de Metaspace.
def metaspace_lint(proyecto: Path, nombre: str) -> list[str]:
    propiedades = proyecto / "gradle.properties"
    if propiedades.exists() and METASPACE in propiedades.read_text(encoding="utf-8"):
        return []
    return [f"plataformas/android.md: {nombre}/gradle.properties no lleva {METASPACE}"]


# ADR-0129: cada enlace a fuentes/ apunta a un archivo que existe, la sección que nombra un origen,
# como «[RFC 6749 §4.1.3](...)» o «[PEP 8, *Imports*](...)», existe en su archivo, y cada archivo de
# fuentes/ es el origen de alguna convención, salvo una lista de la que un programa toma valores.
FUENTE = re.compile(r"\[([^\]]*)\]\(\.\./fuentes/([^)#]+)[^)]*\)")
NUMERO = re.compile(r"§\s*([0-9A-Z](?:[0-9A-Za-z.]*[0-9A-Za-z])?)")
TITULO = re.compile(r",\s*\*([^*]+)\*")
ETIQUETA = re.compile(r"<[^>]+>")


# El número abre una línea, una etiqueta, un título de Markdown o una celda, como «| **7.2.4** |» de ASVS.
def tiene_numero(texto: str, numero: str) -> bool:
    return bool(re.search(rf"(?m)(?:^|>)[\s#|*]*{re.escape(numero)}\.?(?=[\s<*])", texto))


# En texto plano o en reStructuredText, un < de un ejemplo no abre una etiqueta: quitarla
# borraba todo hasta el siguiente >, con los títulos que caían en medio.
SIN_ETIQUETAS = {".rst", ".txt"}


# Lo que va entre acentos graves es código, no una etiqueta: el < de `Future<T>` no abre nada.
CODIGO = re.compile(r"(`[^`\n]*`)")


def tiene_titulo(texto: str, titulo: str, etiquetas: bool) -> bool:
    if etiquetas:
        partes = CODIGO.split(texto)
        texto = "".join(p if p.startswith("`") else ETIQUETA.sub(" ", p) for p in partes)
    plano = " ".join(texto.split()).casefold()
    return " ".join(titulo.split()).casefold() in plano


def origenes() -> list[str]:
    fallas: list[str] = []
    enlazados: set[str] = set()
    for pagina in sorted((CANONE / "plataformas").glob("*.md")):
        for enlace in FUENTE.finditer(pagina.read_text(encoding="utf-8")):
            nombre, fuente = enlace.groups()
            archivo = CANONE / "fuentes" / fuente
            if not archivo.is_file():
                fallas.append(f"plataformas/README.md: {pagina.name} enlaza fuentes/{fuente}, que no existe")
                continue
            enlazados.add(fuente)
            texto = archivo.read_text(encoding="utf-8", errors="replace")
            for numero in NUMERO.findall(nombre):
                if not tiene_numero(texto, numero):
                    fallas.append(f"plataformas/README.md: {pagina.name} cita §{numero}, que no está en fuentes/{fuente}")
            for titulo in TITULO.findall(nombre):
                if not tiene_titulo(texto, titulo, archivo.suffix not in SIN_ETIQUETAS):
                    fallas.append(f"plataformas/README.md: {pagina.name} cita *{titulo}*, que no está en fuentes/{fuente}")
    listas = set()
    for linea in (CANONE / "fuentes/README.md").read_text(encoding="utf-8").splitlines():
        celdas = [celda.strip() for celda in linea.split("|")]
        if len(celdas) == 5 and celdas[1].startswith("["):
            fuente = celdas[1][1 : celdas[1].index("]")]
            if "no fuente" in celdas[3]:
                listas.add(fuente)
            elif fuente not in enlazados:
                fallas.append(f"plataformas/README.md: fuentes/{fuente} no es el origen de ninguna convención")
    return fallas + estandar_de_secciones(listas) + un_origen(listas)


# plataformas/README.md, «Origen»: una convención tiene como origen una sola fuente, aunque nombre
# varias de sus secciones.
def un_origen(listas: set[str]) -> list[str]:
    fallas: list[str] = []
    for pagina in sorted((CANONE / "plataformas").glob("*.md")):
        if pagina.name == "README.md":
            continue
        lineas = pagina.read_text(encoding="utf-8").splitlines()
        for numero, linea in enumerate(lineas, start=1):
            fuentes = {
                f for n, f in FUENTE.findall(linea) if f not in listas and (NUMERO.search(n) or TITULO.search(n))
            }
            if len(fuentes) > 1:
                fallas.append(
                    f"plataformas/README.md: {pagina.name}, línea {numero}, toma su origen de"
                    f" {len(fuentes)} fuentes: {', '.join(sorted(fuentes))}"
                )
    return fallas


# ADR-0130: el párrafo «Estándar:» de una sección nombra los documentos que son origen de sus
# convenciones, y nada más: fuera del texto de sus enlaces no hay secciones, entradas ni «salvo».
# Una sección sin ningún origen no se compara: es de una página sin reescribir.
ENLACE = re.compile(r"\[[^\]]*\]\([^)]*\)")
MAS_QUE_DOCUMENTOS = re.compile(
    r"\bsalvo\b|\*[^*]+\*|`[^`]+`|\bsecci(?:ón|ones)\b|\bentradas?\b|\bpárrafos?\b|\benter[oa]s?\b",
    re.IGNORECASE,
)


def estandar_de_secciones(listas: set[str]) -> list[str]:
    fallas: list[str] = []
    for pagina in sorted((CANONE / "plataformas").glob("*.md")):
        if pagina.name == "README.md":
            continue
        for seccion in re.split(r"(?m)^## ", pagina.read_text(encoding="utf-8"))[1:]:
            titulo, _, cuerpo = seccion.partition("\n")
            nombrados: set[str] = set()
            origenes: set[str] = set()
            de_mas: list[str] = []
            for bloque in cuerpo.split("\n\n"):
                enlaces = [(n, f) for n, f in FUENTE.findall(bloque) if f not in listas]
                if bloque.strip().startswith("Estándar"):
                    nombrados.update(f for _, f in enlaces)
                    de_mas.extend(m.group() for m in MAS_QUE_DOCUMENTOS.finditer(ENLACE.sub("", bloque)))
                else:
                    # Un origen nombra su sección; un enlace sin sección es solo una referencia.
                    origenes.update(f for n, f in enlaces if NUMERO.search(n) or TITULO.search(n))
            if origenes and origenes != nombrados:
                faltan = ", ".join(sorted(origenes - nombrados)) or "nada"
                sobran = ", ".join(sorted(nombrados - origenes)) or "nada"
                fallas.append(
                    f"plataformas/README.md: {pagina.name} «{titulo.strip()}»: a «Estándar:» le falta {faltan}"
                    f" y le sobra {sobran}"
                )
            if origenes and de_mas:
                fallas.append(
                    f"plataformas/README.md: {pagina.name} «{titulo.strip()}»: «Estándar:» nombra más que"
                    f" documentos: {', '.join(sorted(set(de_mas)))}"
                )
    return fallas


# ADR-0136: cada línea de permissions es una función que install.py --allow acepta.
def funciones_permitidas() -> set[str]:
    arbol = ast.parse((PLANTILLA / "infra" / "install.py").read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(
            isinstance(destino, ast.Name) and destino.id == "FEATURES" for destino in nodo.targets
        ):
            return set(ast.literal_eval(nodo.value))
    raise SystemExit("plantilla/infra/install.py no declara FEATURES")


def permisos(repo: Path) -> list[str]:
    archivo = repo / "permissions"
    if not archivo.exists():
        return []
    validas = funciones_permitidas()
    return [
        f"repositorio.md: permissions, línea {numero}: {linea!r} no es una función de Permissions-Policy"
        for numero, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), start=1)
        if linea not in validas
    ]


# autenticacion.md, «Passkeys»: con passkey y una web, permissions las permite.
PASSKEY_FUNCIONES = ("publickey-credentials-create", "publickey-credentials-get")


def permisos_passkey(repo: Path) -> list[str]:
    metodos = repo / "server/src/app/methods.py"
    if not metodos.is_file() or not any((repo / web).is_dir() for web in ("web", "panel")):
        return []
    declarado = re.search(r"^METHODS\b.*$", metodos.read_text(encoding="utf-8"), re.M)
    if declarado is None or "Method.PASSKEY" not in declarado.group(0):
        return []
    archivo = repo / "permissions"
    lineas = archivo.read_text(encoding="utf-8").splitlines() if archivo.exists() else []
    return [
        f"autenticacion.md: permissions no permite {funcion}, y la web usa la passkey"
        for funcion in PASSKEY_FUNCIONES
        if funcion not in lineas
    ]


def copias(repo: Path, cuentas: bool = False) -> list[tuple[str, Path]]:
    """Devuelve cada archivo que el repositorio copia sin editar, con su canónico.

    Con `cuentas`, también los de un servidor con cuentas que todavía no las tiene.
    """
    paginas = vigentes()
    pares: list[tuple[str, Path]] = []

    # Un repositorio sin server/ no tiene por qué tener sus archivos canónicos.
    if (repo / "server").is_dir():
        pares.extend((rel.as_posix(), PLANTILLA / rel) for rel in CANONICOS)
    if (repo / "server/src/app/models/account").is_dir() or cuentas:
        pares.extend((rel.as_posix(), PLANTILLA / rel) for rel in CUENTAS)

    pares.append((".gitattributes", PLANTILLA / ".gitattributes"))

    # despliegue.md, «Versiones», y java.md: el que sube cada app de mobile/ a Play, el que firma y
    # entrega las versiones de Apple, y el que compila cada pieza en Java.
    for nombre in ("scripts/play.py", "scripts/apple.py", "scripts/java.py"):
        if (repo / nombre).exists():
            pares.append((nombre, PLANTILLA / nombre))

    for carpeta, lista in (("packages/sms", SMS), ("packages/passkey", PASSKEY)):
        if (repo / carpeta).is_dir():
            pares.extend((rel.as_posix(), PLANTILLA / rel) for rel in lista)

    # SvelteKit: solo para las superficies web que existan.
    for paquete in repo.glob("*/package.json") if "sveltekit.md" in paginas else []:
        datos = json.loads(paquete.read_text(encoding="utf-8"))
        if "@sveltejs/kit" in {**datos.get("dependencies", {}), **datos.get("devDependencies", {})}:
            pares.extend(
                (f"{paquete.parent.name}/{nombre}", PLANTILLA / "sveltekit" / nombre)
                for nombre in (".prettierrc", "knip.json", "pnpm-workspace.yaml", "static/theme.js", "src/lib/version.ts")
            )

    # Flutter: solo para las apps que existan.
    for pubspec in repo.glob("*/pubspec.yaml") if "flutter.md" in paginas else []:
        app = pubspec.parent
        pares.append((f"{app.name}/analysis_options.yaml", PLANTILLA / "flutter/analysis_options.yaml"))
        if (app / "android/settings.gradle.kts").exists():
            pares.append((f"{app.name}/android/{WRAPPER.as_posix()}", PLANTILLA / "android" / WRAPPER))

    # Android: solo para las apps que existan.
    for settings in repo.glob("*/settings.gradle.kts") if "android.md" in paginas else []:
        app = settings.parent
        pares.append((f"{app.name}/.editorconfig", PLANTILLA / "android/.editorconfig"))
        pares.append((f"{app.name}/{WRAPPER.as_posix()}", PLANTILLA / "android" / WRAPPER))

    # qt.md y flet.md: las pruebas canónicas van en toda pieza; un archivo de api/ o de services/,
    # solo en la pieza que tiene esa carpeta.
    for pieza, pagina in piezas_python(repo).items():
        if pagina in paginas:
            plantilla = PLANTILLA / pagina.removesuffix(".md")
            pares.extend(
                (f"{pieza}/{rel.as_posix()}", plantilla / rel)
                for rel in COPIAS_SRC[pagina]
                if rel.parts[0] == "tests" or (repo / pieza / rel).parent.is_dir()
            )

    # transversal.md, «Tema»: con un cliente. Si los colores de la marca no se pueden leer, lo dice
    # colores_generados().
    tokens = generador()
    try:
        clientes = tokens.outputs(repo)
    except tokens.TokenError:
        clientes = {}
    if clientes:
        pares.append(("scripts/tokens.py", PLANTILLA / "scripts/tokens.py"))
    return pares


def revisar(repo: Path) -> list[str]:
    fallas: list[str] = []
    paginas = vigentes()

    for nombre, canonico in copias(repo):
        fallas.extend(comparar(repo / nombre, canonico, nombre))
    if (repo / "server/src/app/models/account").is_dir():
        fallas.extend(catalogos(repo))

    fallas.extend(piezas_java(repo))

    for carpeta in sorted(p for p in repo.iterdir() if p.is_dir()):
        if carpeta.name.startswith("."):
            continue
        if not nombre_valido(carpeta.name) and not (carpeta / "dependencies.txt").is_file():
            fallas.append(f"repositorio.md: {carpeta.name}/ no es un nombre de pieza")

    if not (repo / ".gitignore").exists():
        fallas.append("repositorio.md: falta .gitignore en el raíz")

    readme = repo / "README.md"
    if not readme.exists():
        fallas.append("repositorio.md: falta README.md en el raíz")
    elif not re.search(
        r"^Estado: en (desarrollo|producción)$", readme.read_text(encoding="utf-8"), re.M
    ):
        fallas.append("repositorio.md: README.md no declara si está en desarrollo o en producción")

    fallas.extend(permisos(repo))
    fallas.extend(permisos_passkey(repo))
    fallas.extend(negaciones(repo, listar(repo)))

    ci = repo / ".github/workflows/ci.yml"
    if not ci.exists():
        fallas.append("repositorio.md: falta .github/workflows/ci.yml")
    elif not re.search(r"^\s+schedule:\s*\n\s+- cron:", ci.read_text(encoding="utf-8"), re.M):
        fallas.append("repositorio.md: .github/workflows/ci.yml no corre cada semana (falta schedule)")

    fallas.extend(configuracion_suelta(repo))

    servidor = repo / "server"
    if servidor.is_dir():
        if not (servidor / "pyproject.toml").exists():
            fallas.append("plataformas/python.md: falta server/pyproject.toml")
        if (servidor / "app").is_dir():
            fallas.append("plataformas/fastapi.md: el paquete va en server/src/app/, no en server/app/")
        if not (servidor / ".gitignore").exists():
            fallas.append("repositorio.md: server/ no tiene su propio .gitignore")

    # SvelteKit: solo para las superficies web que existan.
    for paquete in repo.glob("*/package.json"):
        if "node_modules" in str(paquete):
            continue
        superficie = paquete.parent
        # El .gitignore de la superficie es lo único que ignora node_modules/: el del raíz
        # ya no lo tapa, así que el olvido tiene que romper CI.
        ignore = superficie / ".gitignore"
        if not ignore.exists() or "node_modules" not in ignore.read_text(encoding="utf-8"):
            fallas.append(
                f"repositorio.md: {superficie.name}/ no ignora node_modules/ en su .gitignore"
            )
        datos = json.loads(paquete.read_text(encoding="utf-8"))
        deps = {**datos.get("dependencies", {}), **datos.get("devDependencies", {})}
        if "@sveltejs/kit" not in deps or "sveltekit.md" not in paginas:
            continue
        # pnpm/action-setup toma de aquí la versión de pnpm, y falla si no la encuentra.
        fallas.extend(versiones_package(superficie, datos, deps))
        fallas.extend(scripts_package(superficie, datos))
        eslint = superficie / "eslint.config.js"
        reglas = sin_comentarios(eslint.read_text(encoding="utf-8")) if eslint.exists() else ""
        # La ruta del .gitignore puede ir en una variable, como la escribe sv.
        if not (re.search(r"\bincludeIgnoreFile\s*\(", reglas) and ".gitignore" in reglas):
            fallas.append(f"plataformas/sveltekit.md: {superficie.name}/eslint.config.js no usa includeIgnoreFile")
        ignorados = superficie / ".prettierignore"
        if not ignorados.exists() or "pnpm-lock.yaml" not in ignorados.read_text(encoding="utf-8").split():
            fallas.append(f"plataformas/sveltekit.md: {superficie.name}/.prettierignore no ignora pnpm-lock.yaml")
        for svelte in sorted((superficie / "src").rglob("*.svelte")):
            if re.search(r"svelte-ignore[^>]*\ba11y_", svelte.read_text(encoding="utf-8")):
                relativo = svelte.relative_to(superficie.parent).as_posix()
                fallas.append(f"plataformas/sveltekit.md: {relativo} apaga una advertencia a11y_ con svelte-ignore")
        fallas.extend(vite_sveltekit(superficie / "vite.config.ts"))
        if "@sveltejs/adapter-static" not in deps:
            fallas.append(f"plataformas/sveltekit.md: {superficie.name}/ no usa adapter-static")
        uno = superficie / "uno.config.ts"
        if not uno.exists():
            fallas.append(f"plataformas/sveltekit.md: {superficie.name}/ no tiene uno.config.ts")
        elif not re.search(
            r"\bseparators\s*:\s*\[\s*['\"]:['\"]\s*\]", sin_comentarios(uno.read_text(encoding="utf-8"))
        ):
            fallas.append(f"plataformas/sveltekit.md: {superficie.name}/uno.config.ts no fija separators: [':']")
        # sveltekit.md, «Carga de datos»: el layout raíz recarga la página cuando sale un build nuevo.
        layout = superficie / "src/routes/+layout.svelte"
        texto = layout.read_text(encoding="utf-8") if layout.exists() else ""
        codigo = sin_comentarios(re.sub(r"<!--.*?-->", "", texto, flags=re.S))
        if not re.search(r"\breloadOnNewVersion\s*\(\s*\)", codigo):
            fallas.append(f"plataformas/sveltekit.md: {superficie.name}/src/routes/+layout.svelte no llama a reloadOnNewVersion()")

    # Flutter: solo para las apps que existan.
    for pubspec in repo.glob("*/pubspec.yaml") if "flutter.md" in paginas else []:
        app = pubspec.parent
        settings = app / "android/settings.gradle.kts"
        if settings.exists():
            declarados = dict(PLUGIN_KTS.findall(settings.read_text(encoding="utf-8")))
            fallas.extend(versiones_gradle(f"{app.name}/android", declarados, PLUGINS_FLUTTER))

    # Android: solo para las apps que existan.
    for settings in repo.glob("*/settings.gradle.kts") if "android.md" in paginas else []:
        app = settings.parent
        catalogo = app / "gradle/libs.versions.toml"
        if not catalogo.exists():
            fallas.append(f"plataformas/android.md: falta {app.name}/gradle/libs.versions.toml")
            continue
        declarados = plugins_catalogo(catalogo)
        fallas.extend(versiones_gradle(app.name, declarados, PLUGINS_ANDROID))
        fallas.extend(versiones_bibliotecas(catalogo, app.name))
        fallas.extend(versiones_sdk(app))
        fallas.extend(metaspace_lint(app, app.name))

    # qt.md, «Widgets»: la interfaz se construye en código, también sin un .ui que compile pyside6-uic.
    if "qt.md" in paginas:
        for ui in listar(repo):
            if ui.startswith("desktop/") and ui.endswith(".ui"):
                fallas.append(f"plataformas/qt.md: {ui} es un .ui; la interfaz se construye en código")

    for pieza, pagina in piezas_python(repo).items():
        if pagina not in paginas:
            continue
        fallas.extend(fuera_del_arbol(repo, pieza, pagina))
        if pagina == "qt.md":
            fallas.extend(modulos_por_clase(repo, pieza))

    docs = repo / "docs"
    if docs.is_dir():
        permitidos = {"README.md", "arquitectura", "adr", "planes"}
        sueltos = sorted(p.name for p in docs.iterdir() if p.name not in permitidos)
        if sueltos:
            fallas.append(
                "documentacion.md: docs/ tiene archivos fuera de la convención: "
                + ", ".join(sueltos)
            )

    fallas.extend(colores_generados(repo))
    fallas.extend(nombres_largos(repo))
    fallas.extend(configuracion_con_repositorio(repo))
    if "sveltekit.md" in paginas:
        fallas.extend(versiones_playwright(repo))
    fallas.extend(versiones_uv(repo))
    fallas.extend(versiones_pyproject(repo, paginas))
    if "flutter.md" in paginas:
        fallas.extend(versiones_pubspec(repo))
        fallas.extend(generacion_swagger(repo))
    fallas.extend(versiones_workflows(repo, paginas))

    return fallas


# transversal.md, «Distribución»: cada pieza que se publica declara una variable por plataforma,
# RELEASE_<PIEZA>_<PLATAFORMA>, con true o false. Una que falta, que vale otra cosa o que no es de
# ninguna pieza falla: con un valor por defecto, una plataforma dejaría de publicarse sin aviso.
ESCRITORIO = ("LINUX", "MACOS", "WINDOWS")
MOVIL = ("ANDROID", "IOS")


def plataformas_por_pieza(repo: Path) -> dict[str, tuple[str, ...]]:
    piezas: dict[str, tuple[str, ...]] = {}
    for carpeta in sorted(p for p in repo.iterdir() if p.is_dir() and not p.name.startswith(".")):
        pyproject = carpeta / "pyproject.toml"
        flet = pyproject.exists() and "flet" in tomllib.loads(
            pyproject.read_text(encoding="utf-8")
        ).get("tool", {})
        if carpeta.name == "desktop":
            piezas[carpeta.name] = ESCRITORIO
        elif (carpeta / "pubspec.yaml").exists() or flet:
            piezas[carpeta.name] = MOVIL
        elif (carpeta / "settings.gradle.kts").exists():
            piezas[carpeta.name] = ("ANDROID",)
    return piezas


def variables_release(repo: Path, variables: dict[str, str]) -> list[str]:
    esperadas = {
        f"RELEASE_{pieza.upper().replace('-', '_')}_{plataforma}"
        for pieza, plataformas in plataformas_por_pieza(repo).items()
        for plataforma in plataformas
    }
    fallas = []
    for nombre in sorted(esperadas):
        if nombre not in variables:
            fallas.append(f"transversal.md: falta la variable {nombre}, con true o false")
        elif variables[nombre] not in ("true", "false"):
            fallas.append(f"transversal.md: la variable {nombre} vale {variables[nombre]!r}, no true ni false")
    for nombre in sorted(set(variables) - esperadas):
        if nombre.startswith("RELEASE_"):
            fallas.append(f"transversal.md: la variable {nombre} no es de ninguna pieza que se publica")
    return fallas


# autenticacion.md, «Contraseñas»: la lista de bloqueo de la plantilla son las contraseñas de la lista del
# NCSC con 8 puntos de código o más después de NFC, en minúsculas de casefold, sin repetir y en orden.
NCSC = CANONE / "fuentes" / "seclists" / "100k-most-used-passwords-NCSC.txt"
BLOQUEO = PLANTILLA / "server" / "src" / "app" / "blocklist.txt"


def lista_de_bloqueo() -> str:
    """Deriva de la lista del NCSC el texto de la lista de bloqueo."""
    contrasenas = set()
    for linea in NCSC.read_text(encoding="utf-8").splitlines():
        normalizada = unicodedata.normalize("NFC", linea)
        if len(normalizada) >= 8:
            contrasenas.add(normalizada.casefold())
    return "".join(f"{contrasena}\n" for contrasena in sorted(contrasenas))


def bloqueo() -> list[str]:
    """Comprueba que la lista de bloqueo de la plantilla salga de la del NCSC."""
    if BLOQUEO.read_text(encoding="utf-8") != lista_de_bloqueo():
        return ["autenticacion.md: plantilla/server/src/app/blocklist.txt no sale de la lista del NCSC; se escribe con scripts/bloqueo.py"]
    return []


# README.md y documentacion.md, «Formato»: un ADR aceptado del repositorio nombra en «Se aparta de»
# cada incumplimiento del que se aparta, con el texto que reporta este script.
SE_APARTA = re.compile(r"^- \*\*Se aparta de:\*\* `(.+)`\s*$", re.M)
ACEPTADA = re.compile(r"^- \*\*Estado:\*\* Aceptada", re.M)


def desviaciones(repo: Path) -> dict[str, str]:
    """Devuelve cada incumplimiento del que el repositorio se aparta, con el ADR que lo dice."""
    apartados: dict[str, str] = {}
    for adr in sorted((repo / "docs/adr").glob("[0-9]*.md")):
        texto = adr.read_text(encoding="utf-8")
        if ACEPTADA.search(texto):
            for incumplimiento in SE_APARTA.findall(texto):
                apartados[incumplimiento] = adr.name
    return apartados


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--todos", type=Path, help="directorio que contiene los repositorios")
    parser.add_argument("--canone", action="store_true", help="comprueba las páginas, la plantilla y los workflows de canone")
    parser.add_argument("--variables", help="las variables de GitHub Actions del repositorio, en JSON")
    args = parser.parse_args()

    # La consola de Windows no es UTF-8 y los nombres de archivo llevan acentos.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.canone:
        fallas = origenes()
        # La plantilla sigue todas las páginas, también las que están en desarrollo.
        fallas += versiones_pyproject(PLANTILLA, PAGINAS)
        fallas += versiones_pubspec(PLANTILLA)
        fallas += versiones_programas()
        fallas += versiones_workflows(PLANTILLA, PAGINAS)
        fallas += versiones_workflows(CANONE, PAGINAS)
        fallas += negaciones(CANONE, listar(CANONE))
        fallas += bloqueo()
        fallas += sin_clasificar()
        fallas += colores_plantilla()
        fallas += repetidas()
        print(f"\ncanone: {len(fallas)} incumplimientos")
        for falla in fallas:
            print(f"  - {falla}")
        return 1 if fallas else 0
    if args.todos:
        repos = [
            p
            for p in sorted(args.todos.iterdir())
            if (p / ".git").exists() and p.resolve() != CANONE and not p.name.startswith(".")
        ]
    elif args.repo:
        repos = [args.repo]
    else:
        parser.error("hace falta --repo o --todos")

    total = 0
    for repo in repos:
        fallas = revisar(repo)
        if args.variables is not None:
            fallas += variables_release(repo, json.loads(args.variables))
        apartados = desviaciones(repo)
        cuentan = [falla for falla in fallas if falla not in apartados] + [
            f"documentacion.md: docs/adr/{adr} se aparta de «{incumplimiento}», que no es un incumplimiento"
            for incumplimiento, adr in apartados.items()
            if incumplimiento not in fallas
        ]
        total += len(cuentan)
        print(f"\n{repo.name}: {len(cuentan)} incumplimientos")
        for falla in cuentan:
            print(f"  - {falla}")
        for falla in fallas:
            if falla in apartados:
                print(f"  · se aparta por docs/adr/{apartados[falla]}: {falla}")

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
