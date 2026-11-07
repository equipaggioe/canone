#!/bin/sh
# Runs the deploy.py that install.py installs on a Debian 13, with releases served from this machine
# in place of GitHub: the first version migrates and goes live, the live tag does not go in again,
# an unhealthy version goes back to the previous and leaves nothing, a failed migration leaves
# nothing, a checksum signed by a key outside allowed_signers or of another version installs
# nothing, releases/ keeps the five newest, and a kept version goes live again with its installers
# only if its migrations are those of the active one. A private repository deploys only with
# --private and its token, which does not follow the redirect of a download to another host. The
# server reads the credentials of credentials.py, and the daily purge and sweep run on what goes
# live. The database.py that install.py installs empties the database only on a machine set up with
# --development, with the extensions of install.py, and migrate runs the migrations of the active
# version. The account that administers reads as <app>_read, also over a tunnel to the socket, and
# changes nothing. Each deployment runs the seeders after the migrations without duplicating a row,
# a seeder that fails undoes the migrations and leaves the previous version, and the example data
# loads only on a machine in development. uv finds every package in UV_CACHE_DIR, filled before the
# machine lost its network.
#
#     sh deploy.sh <canone>
set -eu
canone=$1
work=$(mktemp -d)
api=$work/api
desktop="desktop-linux.bin desktop-windows.exe desktop-macos.zip"
pids=
cleanup() {
    status=$?
    for pid in $pids; do kill "$pid" 2>/dev/null || true; done
    # The output of the last command that was meant to fail.
    if [ "$status" -ne 0 ] && [ -f "$work/error" ]; then cat "$work/error"; fi
    rm -rf "$work"
    exit "$status"
}
trap cleanup EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" > "$work/error" 2>&1; then exit 1; fi; }
current() { basename "$(readlink /srv/demo/current)"; }
healthy() { test "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/api/health)" = 204; }
for name in a b s1 s2 x; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
key() { cat "$work/$1.pub"; }
# An account that already administers: install.py only adds its keys, and asks no password.
id operador > /dev/null 2>&1 || useradd --create-home --groups sudo operador
# setup [<flag>]: install.py, and its deploy.py with GitHub answering from this machine.
setup() {
    python3 "$canone/plantilla/infra/install.py" demo demo.example 64mb --admin operador \
        --key "$(key a)" --key "$(key b)" --signer "$(key s1)" --signer "$(key s2)" \
        --owner owner --desktop linux --desktop windows --desktop macos "$@"
    sed 's#https://api.github.com#http://127.0.0.1:9000#' /usr/local/lib/demo/deploy.py \
        > "$work/deploy.py"
}
setup
# The fields of Settings besides the database_url of install.py.
python3 "$canone/plantilla/infra/credentials.py" demo <<'EOF'
health_token=test-health-token
min_client_versions={}
page_token_key=0FDyrOoVgPY9sMS6gmeGBYIwTWh_I11LIzZMzu4z4wY=
EOF
deploy() { UV_OFFLINE=1 python3 "$work/deploy.py" "$1"; }

# release <version> <signing key> [<function that changes the tree>]: what release.yml publishes.
release() {
    tree=$work/tree-$1
    assets=$api/assets/$1
    mkdir -p "$tree/web" "$assets"
    tar -C "$canone/plantilla" --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache \
        --exclude=.ruff_cache -cf - server | tar -C "$tree" -xf -
    sed -i 's/PRODUCTO/demo/' "$tree/server/alembic/versions/d34c1b992b0b_event_log.py"
    echo "$1" > "$tree/web/index.html"
    if [ $# -ge 3 ]; then "$3" "$tree"; fi
    tar -czf "$assets/demo-$1.tar.gz" -C "$tree" .
    for name in $desktop; do echo "$name $1" > "$assets/$name"; done
    (cd "$assets" && sha256sum -- *) > "$work/sums"
    mv "$work/sums" "$assets/demo-$1.sha256"
    sign "$1" "$2"
}
sign() {
    rm -f "$api/assets/$1/demo-$1.sha256.sig"
    ssh-keygen -Y sign -q -n deploy -f "$work/$2" "$api/assets/$1/demo-$1.sha256"
    python3 - "$api" "$1" <<'EOF'
import json
import sys
from pathlib import Path

api, version = Path(sys.argv[1]), sys.argv[2]
folder = api / "assets" / version
assets = [
    {"name": path.name, "url": f"http://127.0.0.1:9000/assets/{version}/{path.name}"}
    for path in sorted(folder.iterdir())
]
tags = api / "repos/owner/demo/releases/tags"
tags.mkdir(parents=True, exist_ok=True)
(tags / version).write_text(json.dumps({"assets": assets}), encoding="utf-8")
EOF
}
broken() { echo 'raise RuntimeError("broken")' >> "$1/server/src/app/main.py"; }
failing() {
    cat > "$1/server/alembic/versions/ffffffffffff_fail.py" <<'EOF'
"""A migration that fails."""

revision = "ffffffffffff"
down_revision = "d34c1b992b0b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    raise RuntimeError("the migration fails")


def downgrade() -> None:
    pass
EOF
}
# seeding <tree>: a seeder and an example that each write one event, once.
seeding() {
    for kind in seeders mock_data; do
        cat > "$1/server/src/app/$kind/events.py" <<EOF2
"""Write the event $kind, once."""

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


async def seed_event(session: AsyncSession) -> None:
    """Write the event if it is missing."""
    await session.execute(
        sa.text(
            "INSERT INTO event_log (action, level, trace_id) SELECT '$kind', 'info', 't' "
            "WHERE NOT EXISTS (SELECT FROM event_log WHERE action = '$kind')"
        )
    )
EOF2
    done
}
# breaking <tree>: a new migration, and a seeder that fails after it.
breaking() {
    migrating "$1"
    cat > "$1/server/alembic/versions/dddddddddddd_table.py" <<'EOF2'
"""A table, which the failing seeder undoes."""

from alembic import op

revision = "dddddddddddd"
down_revision = "eeeeeeeeeeee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TABLE undone (id int)")


def downgrade() -> None:
    op.execute("DROP TABLE undone")
EOF2
    cat > "$1/server/src/app/seeders/broken.py" <<'EOF2'
"""A seeder that fails."""

from sqlalchemy.ext.asyncio import AsyncSession


async def seed_broken(session: AsyncSession) -> None:
    """Fail."""
    raise RuntimeError("the seeder fails")
EOF2
}
migrating() {
    cat > "$1/server/alembic/versions/eeeeeeeeeeee_noop.py" <<'EOF'
"""A migration that changes nothing."""

revision = "eeeeeeeeeeee"
down_revision = "d34c1b992b0b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
EOF
}

mkdir -p "$api"
# GitHub: the API on 9000 and its downloads, redirected to another host. With $work/token, the
# repository is private: without a token it answers 404, and with another token, 401.
cat > "$work/github.py" <<'EOF'
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

api, token = Path(sys.argv[1]), Path(sys.argv[2])


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *arguments):
        pass

    def send_file(self):
        path = api / self.path.lstrip("/")
        if not path.is_file():
            self.send_error(404)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class Api(Handler):
    def do_GET(self):
        if token.exists():
            given = self.headers.get("Authorization")
            if given is None:
                self.send_error(404)
                return
            if given != f"Bearer {token.read_text(encoding='utf-8')}":
                self.send_error(401)
                return
        if self.path.startswith("/assets/"):
            self.send_response(302)
            self.send_header("Location", f"http://localhost:9001{self.path}")
            self.end_headers()
            return
        self.send_file()


class Downloads(Handler):
    def do_GET(self):
        # The token is for the API, and another host must not receive it.
        if "Authorization" in self.headers:
            self.send_error(403)
            return
        self.send_file()


servers = [
    ThreadingHTTPServer(("127.0.0.1", 9000), Api),
    ThreadingHTTPServer(("127.0.0.1", 9001), Downloads),
]
for server in servers:
    threading.Thread(target=server.serve_forever).start()
EOF
python3 "$work/github.py" "$api" "$work/token" &
pids="$pids $!"
until curl -s -o /dev/null http://127.0.0.1:9000/; do sleep 0.2; done

step "The first version migrates, goes live and publishes its installers"
release v1.0.0 s1
deploy v1.0.0
test "$(current)" = v1.0.0
healthy
test "$(runuser -u postgres -- psql -XAt --dbname=demo -c "SELECT to_regclass('event_log')")" = event_log
test "$(cat /srv/demo/downloads/desktop-linux.bin)" = "desktop-linux.bin v1.0.0"

step "The purge and the sweep run every day, and each ends well"
for task in purge sweep; do
    systemctl is-active --quiet "demo-$task.timer"
    systemctl show --property=TimersCalendar --value "demo-$task.timer" | grep -qF 'OnCalendar=*-*-* 00:00:00 ;'
    systemctl start "demo-$task.service"
done

step "The live tag does not go in again"
fails deploy v1.0.0
grep -qF 'v1.0.0 is already live' "$work/error"

step "An unhealthy version without migrations goes back to the previous and is deleted, signed by the second key"
release v1.0.1 s2 broken
fails deploy v1.0.1
grep -qF 'current is back on v1.0.0' "$work/error"
test ! -e /srv/demo/releases/v1.0.1
test "$(current)" = v1.0.0
healthy
test "$(cat /srv/demo/downloads/desktop-linux.bin)" = "desktop-linux.bin v1.0.0"

step "A failed migration deletes the version, and the previous one runs again"
release v1.0.2 s1 failing
fails deploy v1.0.2
test ! -e /srv/demo/releases/v1.0.2
test "$(current)" = v1.0.0
healthy

step "A checksum signed by a key outside allowed_signers installs nothing"
release v1.0.3 x
fails deploy v1.0.3
grep -qF 'ssh-keygen -Y find-principals' "$work/error"
test ! -e /srv/demo/releases/v1.0.3

step "The signed checksums of another version install nothing"
release v1.0.4 s1
cp "$api/assets/v1.0.0/demo-v1.0.0.sha256" "$api/assets/v1.0.4/demo-v1.0.4.sha256"
sign v1.0.4 s1
fails deploy v1.0.4
grep -qF 'the signed checksums do not name demo-v1.0.4.tar.gz' "$work/error"
test ! -e /srv/demo/releases/v1.0.4
test "$(current)" = v1.0.0

step "releases/ keeps the five newest, the active one among them"
for patch in 0 1 2 3 4 5; do
    release "v1.1.$patch" s2
    deploy "v1.1.$patch"
done
test "$(current)" = v1.1.5
healthy
test "$(ls /srv/demo/releases | tr '\n' ' ')" = "v1.1.1 v1.1.2 v1.1.3 v1.1.4 v1.1.5 "
test "$(cat /srv/demo/downloads/desktop-linux.bin)" = "desktop-linux.bin v1.1.5"

# systemd starts a unit at most five times in 10 s, and the steps above restart demo.service
# once per version.
sleep 10
step "A kept version with the same migrations goes live again, with its installers"
deploy v1.1.3
test "$(current)" = v1.1.3
healthy
test "$(cat /srv/demo/downloads/desktop-linux.bin)" = "desktop-linux.bin v1.1.3"
test ! -e /srv/demo/releases/v1.1.3/downloads
deploy v1.1.5
test "$(current)" = v1.1.5
test "$(cat /srv/demo/downloads/desktop-linux.bin)" = "desktop-linux.bin v1.1.5"

step "A kept version with other migrations does not go live again"
release v1.1.6 s1 migrating
deploy v1.1.6
test "$(current)" = v1.1.6
fails deploy v1.1.5
grep -qF 'v1.1.5 has other migrations than v1.1.6' "$work/error"
test "$(current)" = v1.1.6
healthy
test "$(cat /srv/demo/downloads/desktop-linux.bin)" = "desktop-linux.bin v1.1.6"

sleep 10
step "A private repository answers 404 without --private, and 401 with another token"
printf %s test-github-token > "$work/token"
release v1.2.0 s1 migrating
fails deploy v1.2.0
grep -qF ': 404 Not Found' "$work/error"
setup --private
echo github_token=another-token | python3 "$canone/plantilla/infra/credentials.py" demo
fails deploy v1.2.0
grep -qF ': 401 Unauthorized' "$work/error"
test ! -e /srv/demo/releases/v1.2.0
test "$(current)" = v1.1.6

step "With its token it deploys, and the token does not follow a download to another host"
echo github_token=test-github-token | python3 "$canone/plantilla/infra/credentials.py" demo
deploy v1.2.0
test "$(current)" = v1.2.0
healthy
test "$(cat /srv/demo/downloads/desktop-linux.bin)" = "desktop-linux.bin v1.2.0"

sleep 10
step "Without the mark of development, database.py empty changes nothing"
database() { python3 /usr/local/lib/demo/database.py "$@"; }
fails database empty
grep -qF '/etc/demo/development does not exist' "$work/error"
healthy
test "$(runuser -u postgres -- psql -XAt --dbname=demo -c "SELECT to_regclass('event_log')")" = event_log

step "With --development, empty stops the server and leaves the database and the files empty, with the extensions of install.py"
setup --private --development --extension pgcrypto
test -e /etc/demo/development
echo photo > /var/lib/demo/files/photo
mkdir -p /var/lib/demo/files/album
database empty
fails systemctl is-active --quiet demo.service
test "$(runuser -u postgres -- psql -XAt --dbname=demo -c "SELECT count(*) FROM pg_tables WHERE schemaname = 'public'")" = 0
test "$(runuser -u postgres -- psql -XAt --dbname=demo -c "SELECT extname FROM pg_extension WHERE extname = 'pgcrypto'")" = pgcrypto
test -d /var/lib/demo/files
test -z "$(ls -A /var/lib/demo/files)"

step "migrate runs the migrations of the active version and starts the server"
database migrate
test "$(current)" = v1.2.0
healthy
test "$(runuser -u postgres -- psql -XAt --dbname=demo -c "SELECT to_regclass('event_log')")" = event_log

step "The account that administers reads as demo_read, over a tunnel to the socket, and changes nothing"
read_as() { runuser -u "$1" -- psql -XAt --dbname=demo --username=demo_read -c "$2"; }
read_as operador "SELECT version_num FROM alembic_version" > /dev/null
fails read_as operador "UPDATE alembic_version SET version_num = 'x'"
fails read_as operador "SELECT count(*) FROM event_log"
fails read_as operador "CREATE TABLE other (id int)"
fails read_as nobody "SELECT 1"
fails runuser -u operador -- psql -XAt --dbname=demo --username=demo_owner -c "SELECT 1"
# PostgreSQL sees the account that sshd runs the tunnel with.
mkdir "$work/tunnel"
ssh -i "$work/a" -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
    -o UserKnownHostsFile="$work/known_hosts" -N \
    -L "$work/tunnel/.s.PGSQL.5432:/run/postgresql/.s.PGSQL.5432" operador@127.0.0.1 &
pids="$pids $!"
until [ -S "$work/tunnel/.s.PGSQL.5432" ]; do sleep 0.2; done
tunnel() { psql -XAt --host="$work/tunnel" --dbname=demo --username="$1" -c "$2"; }
test "$(tunnel demo_read "SELECT current_user")" = demo_read
fails tunnel demo_read "DELETE FROM alembic_version"
fails tunnel demo_owner "SELECT 1"

step "install.py without --development deletes the mark, and empty fails again"
setup --private
test ! -e /etc/demo/development
fails database empty
healthy

sleep 10
step "Each deployment runs the seeders after the migrations, and they write each row once"
events() { runuser -u postgres -- psql -XAt --dbname=demo -c "SELECT count(*) FROM event_log WHERE action = '$1'"; }
seeded() { migrating "$1"; seeding "$1"; }
release v1.3.0 s1 seeded
deploy v1.3.0
test "$(events seeders)" = 1
release v1.3.1 s1 seeded
deploy v1.3.1
test "$(events seeders)" = 1
database seed
test "$(events seeders)" = 1
test "$(events mock_data)" = 0
healthy

step "A seeder that fails undoes the migrations, and the previous version runs again"
release v1.3.2 s1 breaking
fails deploy v1.3.2
test ! -e /srv/demo/releases/v1.3.2
test "$(current)" = v1.3.1
test -z "$(runuser -u postgres -- psql -XAt --dbname=demo -c "SELECT to_regclass('undone')")"
test "$(runuser -u postgres -- psql -XAt --dbname=demo -c "SELECT version_num FROM alembic_version")" = eeeeeeeeeeee
healthy

step "The example data loads only with the mark of development"
fails database seed --mock
grep -qF '/etc/demo/development does not exist' "$work/error"
test "$(events mock_data)" = 0
setup --private --development
database seed --mock
test "$(events mock_data)" = 1
