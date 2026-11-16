#!/bin/sh
# Runs uninstall.py on a Debian 13 that install.py set up, one level at a time and installing again
# after each: database drops the database, its roles, their credentials and its line of pg_hba, and
# keeps the rest of the app; app takes every unit, site, credential, account and folder of the app;
# machine takes the swap, uv and the files install.py writes for the whole machine, keeps the
# packages and what install.py overwrote in them, and install.py runs again on it. A reinstall that
# does not change the configuration of journald does not restart it. Every level
# keeps the account that administers, its keys and 00-<app>.conf, and root locked.
#
#     sh uninstall.sh <canone>
set -eu
infra=$1/plantilla/infra
work=$(mktemp -d)
cleanup() {
    status=$?
    if [ "$status" -ne 0 ] && [ -f "$work/error" ]; then cat "$work/error"; fi
    rm -rf "$work"
    exit "$status"
}
trap cleanup EXIT
step() { printf '\n== %s\n' "$*"; }
# Under set -e a command after ! never stops the script: not does.
not() { if "$@"; then echo "should have failed: $*"; exit 1; fi; }
fails() { if "$@" > "$work/error" 2>&1; then exit 1; fi; }
for name in a b s1 s2; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
key() { cat "$work/$1.pub"; }
install() {
    python3 "$infra/install.py" demo demo.example 64mb --admin operador --key "$(key a)" \
        --key "$(key b)" --signer "$(key s1)" --signer "$(key s2)" --owner owner
    echo 'health_token=t-1' | python3 "$infra/credentials.py" demo
}
uninstall() { python3 "$infra/uninstall.py" demo "$1"; }
sql() { runuser -u postgres -- psql -XAtc "$1"; }
installed() { dpkg-query --show --showformat '${db:Status-Status}' "$1" 2>/dev/null | grep -qx installed; }
# The way in that every level keeps.
kept() {
    id operador > /dev/null
    grep -qF "$(key a)" /etc/ssh/authorized_keys/operador
    test -f /etc/ssh/sshd_config.d/00-demo.conf
    test "$(passwd --status root | cut -d ' ' -f 2)" = L
}
# An account that already administers: install.py only adds its keys, and asks no password.
id operador > /dev/null 2>&1 || useradd --create-home --groups sudo operador
install

step "--dry-run prints what it would do, and does nothing"
python3 "$infra/uninstall.py" demo app --dry-run > "$work/plan"
grep -qxF 'DROP DATABASE demo WITH (FORCE);' "$work/plan"
grep -qxF 'rm -r /etc/demo' "$work/plan"
grep -qxF 'userdel demo' "$work/plan"
test "$(sql "SELECT 1 FROM pg_database WHERE datname = 'demo'")" = 1
test -d /etc/demo
id demo > /dev/null

step "database drops the database, its roles, their credentials and its line of pg_hba"
uninstall database
test -z "$(sql "SELECT 1 FROM pg_database WHERE datname = 'demo'")"
test -z "$(sql "SELECT 1 FROM pg_roles WHERE rolname IN ('demo', 'demo_owner', 'demo_read')")"
test ! -e /etc/credstore.encrypted/demo/database_url
test ! -e /etc/credstore.encrypted/demo-migrate
not grep -q demo_read /etc/postgresql/17/main/pg_hba.conf /etc/postgresql/17/main/pg_ident.conf

step "and keeps the rest of the app, which install.py completes again"
test -f /etc/credstore.encrypted/demo/health_token
test -f /etc/systemd/system/demo.service
test "$(systemctl is-active demo.service || true)" != active
kept
# The configuration of journald did not change, so install.py does not restart it.
journald=$(systemctl show --property=ExecMainStartTimestampMonotonic --value systemd-journald.service)
install
test "$(sql "SELECT 1 FROM pg_database WHERE datname = 'demo'")" = 1
test "$(systemctl show --property=ExecMainStartTimestampMonotonic --value systemd-journald.service)" = "$journald"

step "app takes every unit, site, credential, account and folder of the app"
uninstall app
test -z "$(find /etc/systemd/system /etc/caddy/sites /etc/credstore.encrypted -name 'demo*')"
for path in /etc/demo /srv/demo /var/lib/demo /usr/local/lib/demo /usr/local/sbin/demo-deploy /usr/local/sbin/demo-database /etc/sysusers.d/demo.conf \
    /etc/valkey/valkey-demo.conf /etc/ssh/sshd_config.d/demo-receiver.conf; do
    test ! -e "$path"
done
for account in demo demo_owner demo-receiver; do fails id "$account"; done
test "$(systemctl is-active valkey-server@demo.service || true)" != active
test -z "$(sql "SELECT 1 FROM pg_database WHERE datname = 'demo'")"
kept
sshd -t

step "machine takes uv and the files of install.py for the machine, and keeps the packages"
install
# What uv.py leaves; this machine has no network to download it.
touch /usr/local/bin/uv
uninstall machine
for path in /usr/local/bin/uv /etc/apt/apt.conf.d/52automatic-reboot /etc/sysctl.d/valkey.conf \
    /etc/demo /srv/demo; do
    test ! -e "$path"
done
for name in caddy postgresql valkey-server nftables unattended-upgrades python3 sudo; do
    installed "$name"
done
for path in /etc/caddy/Caddyfile /etc/nftables.conf /etc/apt/apt.conf.d/20auto-upgrades; do
    test -f "$path"
done
test "$(sysctl -n vm.overcommit_memory)" = 0
kept

step "and install.py installs the app again on it"
install
test "$(sql "SELECT 1 FROM pg_database WHERE datname = 'demo'")" = 1
test "$(sysctl -n vm.overcommit_memory)" = 1
