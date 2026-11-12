# -*- coding: utf-8 -*-
"""Cuenta los enunciados normativos que plataformas/ toma de cada fuente de fuentes/.

    python scripts/contar_enunciados.py              # una línea por fuente
    python scripts/contar_enunciados.py 63b          # las fuentes cuyo nombre contiene «63b», con sus enunciados
    python scripts/contar_enunciados.py --secciones rfc/rfc9110.txt
    python scripts/contar_enunciados.py --entradas   # las entradas que usa plantilla/

Cada fuente se recorta al alcance que citan las páginas (UNIDADES) y se cuenta con un modo:

- dart, asvs, wcag, yml, androidrec, vocab, n3: la unidad que numera la fuente (regla, requisito,
  criterio, recomendación, evento o entrada). Exacto.
- up: oraciones con MUST, SHALL, SHOULD, REQUIRED o RECOMMENDED. Incluye los requisitos dirigidos
  al navegador u otro actor: es un techo.
- bs: oraciones con must o should, para las especificaciones que no los escriben en mayúsculas.
- low: oraciones con un verbo normativo o que empiezan en imperativo. Heurística: hay que revisar
  la lista a mano.

Ningún modo descuenta lo que la página escribe por su cuenta, deja sin efecto o dirige a otro actor
(plataformas/README.md, «Selección de fuentes», requisito «Aporta»).
"""
from __future__ import annotations

import glob
import html
import os
import re
import sys
import tomllib
from pathlib import Path

CANONE = Path(__file__).resolve().parent.parent
F = str(CANONE / 'fuentes') + '/'
PLANTILLA = CANONE / 'plantilla'

def strip_tags(s):
    s = re.sub(r'<em class="rfc2119"[^>]*>(.*?)</em>', lambda m: m.group(1).upper(), s, flags=re.S)
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return html.unescape(s)

def parse(path):
    """Devuelve lista de (nivel, numero, titulo, texto)."""
    t = open(F + path, encoding='utf8', errors='ignore').read()
    ext = os.path.splitext(path)[1]
    heads = []  # (nivel, num, titulo, pos_inicio_texto)
    if ext in ('.html', '.bs'):
        out = []
        last = 0
        for m in re.finditer(r'<h([1-6])\b[^>]*>(.*?)</h\1>', t, flags=re.S):
            out.append(('T', t[last:m.start()]))
            title = re.sub(r'\s+', ' ', strip_tags(m.group(2))).strip()
            out.append(('H', int(m.group(1)), title))
            last = m.end()
        out.append(('T', t[last:]))
        return build(out, strip_tags)
    if ext in ('.sgml', '.xml') and 'systemd' not in path:
        out = []; last = 0; depth = 0
        for m in re.finditer(r'<(/?)(sect\d|section|chapter|simplesect|refsect\d)\b[^>]*>(\s*<title>(.*?)</title>)?', t, flags=re.S):
            if m.group(1):
                depth -= 1; continue
            out.append(('T', t[last:m.start()]))
            depth += 1
            title = re.sub(r'\s+', ' ', strip_tags(m.group(4) or '')).strip()
            out.append(('H', depth, title))
            last = m.end()
        out.append(('T', t[last:]))
        return build(out, strip_tags)
    if ext == '.qdoc':
        out = []; last = 0
        for m in re.finditer(r'^\s*\\(section(\d)|title|fn|property|enum)\s+(.*)$', t, flags=re.M):
            out.append(('T', t[last:m.start()]))
            lvl = int(m.group(2)) + 1 if m.group(2) else (1 if m.group(1) == 'title' else 9)
            out.append(('H', lvl, m.group(3).strip()))
            last = m.end()
        out.append(('T', t[last:]))
        return build(out, lambda s: re.sub(r'\\\w+(\{[^}]*\})?', lambda m: m.group(1)[1:-1] if m.group(1) else ' ', s))
    if ext == '.rst':
        lines = t.split('\n'); out = []; buf = []; order = []
        i = 0
        while i < len(lines):
            l = lines[i]
            nx = lines[i + 1] if i + 1 < len(lines) else ''
            if l.strip() and re.fullmatch(r'([=\-~^"\'`#*+])\1{2,}\s*', nx) and len(nx.strip()) >= len(l.strip()) - 2:
                ch = nx.strip()[0]
                over = i > 0 and re.fullmatch(re.escape(ch) + '{3,}', lines[i - 1].strip() or 'x')
                key = ch + ('o' if over else '')
                if key not in order: order.append(key)
                out.append(('T', '\n'.join(buf))); buf = []
                out.append(('H', order.index(key) + 1, l.strip()))
                i += 2; continue
            buf.append(l); i += 1
        out.append(('T', '\n'.join(buf)))
        return build(out, lambda s: s)
    if ext == '.md':
        out = []; buf = []; code = False
        for l in t.split('\n'):
            if l.startswith('```'): code = not code
            m = None if code else re.match(r'^(#{1,6})\s+(.*)$', l)
            if m:
                out.append(('T', '\n'.join(buf))); buf = []
                out.append(('H', len(m.group(1)), re.sub(r'\{[:#][^}]*\}', '', m.group(2)).strip()))
            else: buf.append(l)
        out.append(('T', '\n'.join(buf)))
        return build(out, lambda s: s)
    # txt: RFC, NIST, FHS
    out = []; buf = []
    for l in t.split('\n'):
        m = re.match(r'^ ?(?:Appendix\s+)?([0-9A-Z]+(?:\.\d+)*)\.?\s+(\S.*)$', l)
        if m and not re.search(r'\.\s?\.\s?\.|(?<!Level)\s\d+$', l) and (m.group(1)[0].isdigit() or l.startswith('Appendix')) and len(l) < 90:
            out.append(('T', '\n'.join(buf))); buf = []
            num = m.group(1)
            out.append(('H', num.count('.') + 1, num + ' ' + m.group(2).strip()))
        else: buf.append(l)
    out.append(('T', '\n'.join(buf)))
    return build(out, lambda s: s)

def build(out, clean):
    secs = []  # [nivel, titulo, texto]
    cur = [0, '(inicio)', '']
    for x in out:
        if x[0] == 'H':
            secs.append(cur); cur = [x[1], x[2], '']
        else:
            cur[2] += clean(x[1])
    secs.append(cur)
    return secs

def select(secs, inc=None, exc=()):
    """inc: lista de patrones de título (número o texto). None = todo."""
    def match(title, pats):
        for p in pats:
            if re.match(r'^[0-9A-Z](\.\d+)*$', p):
                if re.match(r'^' + re.escape(p) + r'(\s|\.)', title + ' ') and (title.startswith(p + ' ') or title.startswith(p + '.')):
                    return True
            elif p.lower() in title.lower():
                return True
        return False
    res = []; on = None; off = None
    for lvl, title, text in secs:
        if off is not None and lvl <= off: off = None
        if on is not None and lvl <= on: on = None
        if inc is None:
            pass
        elif on is None and match(title, inc):
            on = lvl
        if off is None and match(title, exc):
            off = lvl
        if (inc is None or on is not None) and off is None:
            res.append((title, text))
    return res

KW_UP = re.compile(r'\b(MUST|SHALL|SHOULD|REQUIRED|RECOMMENDED)\b')
KW_LOW = re.compile(r"\b(must|should|shall|never|avoid|do not|don't|recommend(?:ed|s)?|required|prefer|make sure|ensure|always)\b", re.I)
IMP = re.compile(r"^\s*(?:[-*+]|\d+\.)?\s*\**(Use|Avoid|Prefer|Don't|Do not|Do|Keep|Make|Never|Always|Put|Write|Place|Name|Declare|Limit|Store|Validate|Ensure|Set|Consider|Separate|Expose|Inject|Create|Define|Provide|Add|Include|Remove|Return|Follow|Leave|Only|Verify|Treat|Check|Reject|Apply|Restrict)\b")

def sentences(text):
    text = re.sub(r'```.*?```', ' ', text, flags=re.S)
    parts = []
    for block in re.split(r'\n\s*\n|\n\s*(?=[-*+]\s|\d+\.\s|\|)', text):
        b = re.sub(r'\s+', ' ', block).strip()
        if not b: continue
        parts += [s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z`*\[])', b) if s.strip()]
    return parts

def count(text, mode):
    n = 0; ss = []
    for s in sentences(text):
        if mode == 'up':
            ok = bool(KW_UP.search(s))
        else:
            ok = bool(KW_LOW.search(s) or IMP.match(s))
        if ok: n += 1; ss.append(s)
    return n, ss


# (fuente, incluir (None = entera), excluir, modo)
UNIDADES = [
 # android
 ('android/kotlin-style-guide.md', None, [], 'low'),
 ('kotlin/coding-conventions.md', ['Avoid redundant constructs', 'Idiomatic use of language features'], [], 'low'),
 ('android/architecture.md', None, [], 'low'),
 ('android/architecture-recommendations.md', None, [], 'androidrec'),
 ('android/ui-layer.md', None, [], 'low'),
 ('android/data-layer.md', None, [], 'low'),
 ('android/coroutines-best-practices.md', None, [], 'low'),
 ('android/hilt.md', None, [], 'low'),
 ('compose/state.md', None, [], 'low'),
 ('compose/architecture.md', None, [], 'low'),
 ('android/accessibility-apps.md', None, [], 'low'),
 ('android/accessibility-principles.md', None, [], 'low'),
 ('android/datastore.md', None, [], 'low'),
 ('android/keystore.md', None, [], 'low'),
 ('android/sms-retriever-request.md', ['Start the SMS retriever', 'Receive verification messages', 'Send the one-time code'], [], 'low'),
 ('android/localization.md', None, [], 'low'),
 ('android/credential-manager-prerequisites.md', None, [], 'low'),
 ('android/create-passkeys.md', None, [], 'low'),
 ('android/sign-in-with-passkeys.md', None, [], 'low'),
 ('android/notification-permission.md', None, [], 'low'),
 ('android/notification-channels.md', None, [], 'low'),
 ('android/testing-fundamentals.md', None, [], 'low'),
 # despliegue
 ('fhs/fhs-3.0.txt', ['3.7', '3.15', '3.17', '4.6', '4.9', '5.8'], [], 'fhs'),
 ('owasp/HTTP_Headers.md', None, ['Access-Control-Allow-Origin', 'Secure File Download Headers'], 'low'),
 ('owasp/WebSocket_Security.md', ['Infrastructure Configuration', 'WebSocket Protocol Configuration', 'Origin Header Validation', 'Additional CSWSH Protections', 'Message-Level Authorization', 'Input Validation', 'Service Tunneling Risks', 'Denial-of-Service Protection', 'Framework-Specific Best Practices', 'Always Use WSS', 'Session Management'], ['Security Monitoring and Logging'], 'low'),
 ('rfc/rfc8656.txt', ['3.1', '7.2', '21.1.1', '21.1.6', '21.1.7', '21.2', '21.3', '21.4'], [], 'up'),
 ('nist/sp800-41r1.txt', ['4'], [], 'low'),
 ('nist/ir7966.txt', ['3.4', '5.1'], [], 'low'),
 ('postgresql/backup.sgml', ['SQL Dump'], [], 'low'),
 ('valkey/admin.md', None, [], 'low'),
 ('valkey/security.md', None, [], 'low'),
 # fastapi
 ('sqlalchemy/session_basics.rst', None, [], 'low'),
 ('sqlalchemy/asyncio.rst', None, [], 'low'),
 ('alembic/autogenerate.rst', None, [], 'low'),
 ('owasp/File_Upload.md', None, [], 'low'),
 ('nist/sp800-63b-4.txt', ['2.1','2.2','2.4','3.1.1','3.1.3','3.1.6','3.1.7','3.2','4','5','B'], ['3.1.3.1','3.1.3.4','3.1.6.1','3.1.7.1','3.2.3','3.2.6','3.2.10','3.2.11','3.2.13','3.1.7.3','4.2.2.3'], 'up'),
 ('owasp/Password_Storage.md', None, [], 'low'),
 ('standard-webhooks/standard-webhooks.md', None, [], 'bs'),
 ('rfc/rfc6585.txt', ['4'], [], 'up'),
 ('openapi/openapi-3.1.2.md', ['Operation Object', 'Responses Object'], [], 'up'),
 ('owasp/Third_Party_Payment_Gateway_Integration.md', ['What Can Go Wrong at Each Step', 'Logging and Monitoring'], [], 'low'),
 ('w3c/webauthn-3.html', ['5.4', '5.5', '6.1.1', '6.1.3', '7', '13.1', '13.4', '14.6'], [], 'up'),
 ('owasp/Authorization.md', None, [], 'low'),
 ('rfc/rfc9110.txt', ['15', '4.3.4', '12.5.4', '9.2', '9.3', '3.3', '11', '10.1.5'], [], 'up'),
 ('rfc/rfc8030.txt', ['5'], [], 'up'),
 ('owasp/Logging.md', None, [], 'low'),
 ('owasp/Logging_Vocabulary.md', None, [], 'vocab'),
 ('rfc/rfc9700.txt', None, [], 'up'),
 ('owasp/ASVS_V7_Session_Management.md', None, [], 'asvs'),
 ('owasp/ASVS_V3_Web_Frontend_Security.md', None, [], 'asvs'),
 # flutter
 ('dart/effective-dart-index.md', None, [], 'dart'),
 ('dart/effective-dart-style.md', None, [], 'dart'),
 ('dart/effective-dart-documentation.md', None, [], 'dart'),
 ('dart/effective-dart-usage.md', None, [], 'dart'),
 ('dart/effective-dart-design.md', None, [], 'dart'),
 ('flutter/app-architecture-concepts.md', None, [], 'low'),
 ('flutter/app-architecture-guide.md', None, [], 'low'),
 ('flutter/app-architecture-recommendations.md', None, [], 'low'),
 ('flutter/architecture-recommendations.yml', None, [], 'yml'),
 ('flutter/state-mgmt-simple.md', None, [], 'low'),
 ('pub/provider/README.md', None, [], 'low'),
 ('pub/shared_preferences/README.md', None, [], 'low'),
 ('pub/flutter_secure_storage/README.md', None, [], 'low'),
 ('flutter/accessibility.md', None, [], 'low'),
 ('flutter/internationalization.md', None, [], 'low'),
 # postgres
 ('postgresql/ddl.sgml', ['The System Catalog Schema', 'Primary Keys', 'System Columns', 'Check Constraints', 'Not-Null Constraints', 'Foreign Keys', 'Modifying Tables'], [], 'low'),
 ('postgis/using_postgis_dataman.xml', ['Geography Data Type', 'GiST Indexes'], [], 'low'),
 ('postgresql/indices.sgml', ['Introduction', 'Multicolumn Indexes', 'Unique Indexes', 'Partial Indexes', 'Index-Only Scans and Covering Indexes'], [], 'low'),
 ('postgresql/datatype.sgml', ['Character Types', 'Date/Time Types', 'Integer Types', 'Arbitrary Precision Numbers', 'Network Address Types'], [], 'low'),
 ('postgresql/json.sgml', None, [], 'low'),
 # python
 ('pytest/goodpractices.rst', ['Install package in a virtual environment', 'Choosing a test layout', 'Do not run via setuptools', "Using pytest's strict mode"], [], 'low'),
 ('python/pep-0008.rst', None, [], 'low'),
 ('python/pep-0257.rst', None, [], 'low'),
 ('typing/best_practices.rst', None, [], 'low'),
 ('typing/modernizing.rst', None, [], 'low'),
 ('python/asyncio-dev.rst', None, [], 'low'),
 # qt
 ('pyside6/considerations.rst', None, [], 'low'),
 ('qt/layout.qdoc', None, [], 'low'),
 ('qt/model-view-programming.qdoc', None, [], 'low'),
 ('qt/accessible.qdoc', None, ['Accessibility for Qt Quick Applications'], 'low'),
 ('qt/threads.qdoc', None, [], 'low'),
 # sveltekit
 ('sveltekit/project-structure.md', None, [], 'low'),
 ('sveltekit/load.md', None, [], 'low'),
 ('sveltekit/page-options.md', None, [], 'low'),
 ('svelte/best-practices.md', None, [], 'low'),
 ('sveltekit/state-management.md', None, [], 'low'),
 ('svelte/state.md', None, [], 'low'),
 ('svelte/props.md', None, [], 'low'),
 ('sveltekit/accessibility.md', None, [], 'low'),
 ('owasp/Content_Security_Policy.md', None, [], 'low'),
 ('unocss/presets-wind4.md', None, [], 'low'),
 ('unocss/integrations-vite.md', ['`global`', 'Svelte', 'Sveltekit'], ['svelte-scoped'], 'low'),
 ('paraglide/basics.md', None, [], 'low'),
 ('paraglide/compiling-messages.md', None, [], 'low'),
 ('paraglide/strategy.md', None, [], 'low'),
 ('w3c/push-api.html', ['Permission', 'PushManager interface', 'PushMessageData interface', 'Events', 'Push subscription', 'Declarative push message', 'PushSubscriptionOptions Interface', 'PushSubscription interface', 'PushEncryptionKeyName enumeration'], [], 'up'),
 ('whatwg/notifications.bs', None, [], 'bs'),
 ('sveltekit/adapter-static.md', None, [], 'low'),
 # transversal
 ('w3c/wcag22.html', None, [], 'wcag'),
 ('wicg/sms-one-time-codes.bs', None, [], 'bs'),
 ('rfc/rfc9457.txt', None, [], 'up'),
 ('rfc/rfc7493.txt', ['4.3', '2.2', '2.1', '2.3', '3', '4.1', '4.2', '4.4'], [], 'up'),
 ('rfc/rfc5646.txt', ['2', '4'], [], 'up'),
 ('osm/attribution-guidelines.md', None, [], 'low'),
 ('rfc/rfc7946.txt', ['Geometry Object', 'Coordinate Reference System', 'GeoJSON Types Are Not Extensible'], [], 'up'),
 ('google-aip/aip-0158.md', None, [], 'bs'),
 ('rfc/rfc6749.txt', ['2', '3', '4.1', '5'], [], 'up'),
 ('rfc/rfc7636.txt', None, [], 'up'),
 ('rfc/rfc8252.txt', None, [], 'up'),
 ('rfc/rfc8292.txt', ['2'], [], 'up'),
 ('dtcg/format.html', None, [], 'up'),
 ('dtcg/color.html', None, [], 'up'),
 ('dtcg/resolver.html', None, [], 'up'),
]

def run(u, dump=False):
    f, inc, exc, mode = u
    secs = parse(f)
    sel = select(secs, inc, exc)
    text = '\n\n'.join(t for _, t in sel)
    if mode == 'dart':
        n = sum(1 for title, _ in sel if re.match(r"^(DO|DON'T|PREFER|AVOID|CONSIDER)\b", title))
        return n, [title for title, _ in sel if re.match(r"^(DO|DON'T|PREFER|AVOID|CONSIDER)\b", title)], sel
    if mode == 'asvs':
        rows = re.findall(r'^\| \*\*(\d+\.\d+\.\d+)\*\* \| (.*?) \| (\d) \|', open(F + f, encoding='utf8').read(), flags=re.M)
        l1 = [r for r in rows if r[2] == '1' and not (r[0] == '3.2.1' or r[0].startswith('3.4.'))]
        return len(l1), [r[0] + ' ' + r[1] for r in l1], sel
    if mode == 'androidrec':
        t = open(F + f, encoding='utf8').read()
        items = re.findall(r'^(.*?)\*\*(Strongly recommended|Recommended[^*]*)\*\* \|', t, flags=re.M)
        return len(items), [a.strip()[:120] for a, b in items], sel
    if mode == 'vocab':
        t = open(F + f, encoding='utf8').read().split('## The Vocabulary', 1)[1]
        items = re.findall(r'^### (.*)$', t, flags=re.M)
        return len(items), items, sel
    if mode == 'n3':
        return 3, ['urls', 'username', 'credential'], sel
    if mode == 'yml':
        t = open(F + f, encoding='utf8').read()
        items = re.findall(r'recommendation:\s*(.*)$', t, flags=re.M)
        return len(items), items, sel
    if mode == 'fhs':
        mode = 'low'
    if mode == 'bs':
        ss = [s for s in sentences(text) if re.search(r'\b(must|should|MUST|SHOULD)\b', s)]
        return len(ss), ss, sel
    if mode == 'wcag':
        ss = [t for t, x in sel if re.match(r'^Success Criterion', t) and re.search(r'\(Level AA?\)', x[:300])]
        return len(ss), ss, sel
    n, ss = count(text, mode)
    return n, ss, sel


def entradas():
    """Las entradas de las fuentes citadas por entradas que usa plantilla/."""
    res = {}
    doc = set(re.findall(r'<term><varname>(\w+)=</varname>', open(F + 'systemd/systemd.exec.xml', encoding='utf8').read()))
    usadas = set()
    for f in glob.glob(str(PLANTILLA / 'infra' / '*.service')) + glob.glob(str(PLANTILLA / 'infra' / '*.conf')):
        for l in open(f, encoding='utf8'):
            m = re.match(r'^(\w+)=', l)
            if m and m.group(1) in doc: usadas.add(m.group(1))
    res['systemd/systemd.exec.xml'] = sorted(usadas)
    claves, grupos, flet = set(), set(), set()
    def recorrer(d, prefijo):
        for k, v in d.items():
            if isinstance(v, dict): recorrer(v, prefijo + k + '.')
            else: flet.add(prefijo + k)
    for f in glob.glob(str(PLANTILLA / '*' / 'pyproject.toml')):
        t = tomllib.load(open(f, 'rb'))
        claves |= {'project.' + k for k in t.get('project', {})}
        claves |= {'build-system.' + k for k in t.get('build-system', {})}
        if 'dependency-groups' in t: grupos.add('dependency-groups')
        if 'flet' in t.get('tool', {}): recorrer(t['tool']['flet'], 'tool.flet.')
    res['pypa/pyproject-toml.rst'] = sorted(claves)
    res['pypa/dependency-groups.rst'] = sorted(grupos)
    res['flet/publish.md'] = sorted(flet)
    spec = open(PLANTILLA / 'qt' / 'pysidedeploy.spec', encoding='utf8').read()
    res['pyside6/deployment-pyside6-deploy.rst'] = re.findall(r'^(\w+)\s*=', spec, flags=re.M)
    return res


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    args = sys.argv[1:]
    if args[:1] == ['--secciones']:
        for lvl, title, text in parse(args[1]):
            print(lvl, '|', title[:100], '|', len(text))
    elif args[:1] == ['--entradas']:
        for f, e in entradas().items():
            print(f'{len(e):5d}  {f}  {", ".join(e)}')
    else:
        only = args[0] if args else None
        for u in UNIDADES:
            if only and only not in u[0]: continue
            n, ss, sel = run(u)
            print(f'{n:5d}  {u[0]}  {u[3]}')
            if only:
                print('  SECCIONES:', [t[:50] for t, _ in sel])
                for s in ss: print('   -', s[:300])
