#!/bin/sh
# Runs uninstall.py on a Debian 13 that install.py set up, one level at a time and installing again
# after each: database drops the database, its roles, their credentials and its line of pg_hba, and
# keeps the rest of the app; app takes every unit, site, credential, account and folder of the app;
# machine purges the packages of packages.py but sudo and those of their families, with their data,
# and keeps one whose purge would take a package someone installed by hand. Every level keeps the
# account that administers, its keys and 00-<app>.conf, and root locked.
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
    grep -qF "$(key a)" ~operador/.ssh/authorized_keys
    test -f /etc/ssh/sshd_config.d/00-demo.conf
    test "$(passwd --status root | cut -d ' ' -f 2)" = L
}
# An account that already administers: install.py only adds its keys, and asks no password.
id operador > /dev/null 2>&1 || useradd --create-home --groups sudo operador
install

step "--dry-run prints what it would do, and does nothing"
python3 "$infra/uninstall.py" demo app --dry-run > "$work/plan"
grep -qxF 'DROP DATABASE demo WITH (FORCE);' "$work/plan"
grep -qxF 'rm -r /srv/demo' "$work/plan"
grep -qxF 'userdel demo' "$work/plan"
test "$(sql "SELECT 1 FROM pg_database WHERE datname = 'demo'")" = 1
test -d /srv/demo
id demo > /dev/null

step "database drops the database, its roles, their credentials and its line of pg_hba"
uninstall database
test -z "$(sql "SELECT 1 FROM pg_database WHERE datname = 'demo'")"
test -z "$(sql "SELECT 1 FROM pg_roles WHERE rolname IN ('demo', 'demo_owner', 'demo_read')")"
test ! -e /etc/credstore.encrypted/demo/database_url
test ! -e /etc/credstore.encrypted/demo-migrate
! grep -q demo_read /etc/postgresql/17/main/pg_hba.conf /etc/postgresql/17/main/pg_ident.conf

step "and keeps the rest of the app, which install.py completes again"
test -f /etc/credstore.encrypted/demo/health_token
test -f /etc/systemd/system/demo.service
test "$(systemctl is-active demo.service || true)" != active
kept
install
test "$(sql "SELECT 1 FROM pg_database WHERE datname = 'demo'")" = 1

step "app takes every unit, site, credential, account and folder of the app"
uninstall app
test -z "$(find /etc/systemd/system /etc/caddy/sites /etc/credstore.encrypted -name 'demo*')"
for path in /etc/demo /srv/demo /var/lib/demo /usr/local/lib/demo /etc/sysusers.d/demo.conf \
    /etc/valkey/valkey-demo.conf /etc/ssh/sshd_config.d/demo-receiver.conf; do
    test ! -e "$path"
done
for account in demo demo_owner demo-receiver; do fails id "$account"; done
test "$(systemctl is-active valkey-server@demo.service || true)" != active
test -z "$(sql "SELECT 1 FROM pg_database WHERE datname = 'demo'")"
kept
sshd -t

step "machine purges the packages of packages.py but sudo, with their data"
install
# As on a machine of a provider: by hand, what the image brings by priority, ssh, and what
# packages.py installs; the rest, pulled by them. debootstrap marks every package by hand.
apt-mark auto $(dpkg-query --show --showformat '${Package}\n') > /dev/null
image=$(dpkg-query --show --showformat '${Package} ${Priority}\n' |
    awk '$2 == "required" || $2 == "important" {print $1}')
asked=$(for name in $(python3 "$infra/packages.py" --list --all); do
    if installed "$name"; then echo "$name"; fi
done)
apt-mark manual $image openssh-server $asked > /dev/null
mkdir -p "$work/keeper/DEBIAN"
printf 'Package: keeper\nVersion: 1\nArchitecture: all\nMaintainer: ci\nDepends: restic\nDescription: ci\n' \
    > "$work/keeper/DEBIAN/control"
dpkg-deb --build "$work/keeper" "$work/keeper.deb" > /dev/null
dpkg --install "$work/keeper.deb" > /dev/null
uninstall machine > "$work/output"
grep -qxF 'restic stays: apt would also remove keeper.' "$work/output"
installed restic
installed keeper
for name in caddy postgresql postgresql-17 valkey-server valkey-tools nftables unattended-upgrades; do
    ! installed "$name"
done
installed sudo
for path in /etc/caddy /var/lib/postgresql /etc/postgresql /var/lib/valkey /usr/local/bin/uv \
    /etc/apt/apt.conf.d/20auto-upgrades /etc/sysctl.d/valkey.conf /etc/demo; do
    test ! -e "$path"
done
test "$(sysctl -n vm.overcommit_memory)" = 0
kept
