#!/bin/sh
# Runs deploy.py on a Debian 13 that install.py set up, with releases served from this machine in
# place of GitHub: the first version migrates and goes live, a tag goes in once, an unhealthy
# version goes back to the previous, a failed migration leaves nothing, a checksum signed by a key
# outside allowed_signers or of another version installs nothing, and releases/ keeps the five
# newest. uv finds every package in UV_CACHE_DIR, filled before the machine lost its network.
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
python3 "$canone/plantilla/infra/install.py" demo demo.example 64mb --admin operador \
    --key "$(key a)" --key "$(key b)" --signer "$(key s1)" --signer "$(key s2)"
# The fields of Settings that consola writes, besides the database_url of install.py.
credential() {
    printf %s "$2" | systemd-creds encrypt --name="app_$1" - "/etc/credstore.encrypted/demo/$1"
}
credential health_token test-health-token
credential min_client_versions '{}'
credential page_token_key 0FDyrOoVgPY9sMS6gmeGBYIwTWh_I11LIzZMzu4z4wY=
# The repository of the product is demo, and GitHub answers from this machine.
sed -e 's/PRODUCTO/demo/g' -e 's/OWNER/owner/g' -e 's#https://api.github.com#http://127.0.0.1:9000#' \
    "$canone/plantilla/scripts/deploy.py" > "$work/deploy.py"
deploy() { UV_OFFLINE=1 python3 "$work/deploy.py" "$1"; }

# release <version> <signing key> [<function that changes the tree>]: what release.yml publishes.
release() {
    tree=$work/tree-$1
    assets=$api/assets/$1
    mkdir -p "$tree/web" "$tree/scripts" "$assets"
    tar -C "$canone/plantilla" --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache \
        --exclude=.ruff_cache -cf - server | tar -C "$tree" -xf -
    sed -i 's/PRODUCTO/demo/' "$tree/server/alembic/versions/d34c1b992b0b_event_log.py"
    cp "$work/deploy.py" "$tree/scripts/"
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

mkdir -p "$api"
python3 -m http.server --bind 127.0.0.1 9000 --directory "$api" > /dev/null 2>&1 &
pids="$pids $!"
until curl -s -o /dev/null http://127.0.0.1:9000/; do sleep 0.2; done

step "The first version migrates, goes live and publishes its installers"
release v1.0.0 s1
deploy v1.0.0
test "$(current)" = v1.0.0
healthy
test "$(runuser -u postgres -- psql -XAt --dbname=demo -c "SELECT to_regclass('event_log')")" = event_log
test "$(cat /srv/demo/downloads/desktop-linux.bin)" = "desktop-linux.bin v1.0.0"

step "A tag goes in once"
fails deploy v1.0.0
grep -qF '/srv/demo/releases/v1.0.0 already exists' "$work/error"

step "An unhealthy version without migrations goes back to the previous, signed by the second key"
release v1.0.1 s2 broken
fails deploy v1.0.1
grep -qF 'current is back on v1.0.0' "$work/error"
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
