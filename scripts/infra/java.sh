#!/bin/sh
# Runs a piece in Java under the unit of install.py --java, on a Debian 13 with systemd running:
# without --java there is no unit and deploy.py restarts no piece; a name that cannot name a unit
# fails; with --java the unit is enabled; the piece runs its jar from the current version, answers
# on loopback, restarts with the restart of deploy.py, reaches only localhost, stops without failing
# and keeps an exposure of 2.0 or less; and uninstall.py app takes the unit. The piece is scripts/infra/ping/,
# which the CI builds outside the machine, as release.yml does:
#
#     python3 <canone>/plantilla/scripts/java.py ping Ping ping/build    (in scripts/infra/)
#     sh java.sh <canone>
set -eu
canone=$1
install=$canone/plantilla/infra/install.py
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" 2> "$work/error"; then exit 1; fi; }
for name in a b s1 s2; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
key() { cat "$work/$1.pub"; }
run() {
    python3 "$install" demo demo.example 64mb --admin operador --key "$(key a)" --key "$(key b)" \
        --signer "$(key s1)" --signer "$(key s2)" --owner owner "$@"
}
id operador > /dev/null 2>&1 || useradd --create-home --groups sudo operador

step "Without --java there is no unit, and deploy.py restarts no piece"
run
test ! -e /etc/systemd/system/demo-java@.service
grep -qxF 'JAVA: tuple[str, ...] = ()' /usr/local/sbin/demo-deploy

step "A name that cannot name a unit fails"
fails run --java Ping
grep -qF "is not a piece in Java" "$work/error"

step "With --java the unit is enabled, and deploy.py names it"
run --java ping
test -f /etc/systemd/system/demo-java@.service
systemctl is-enabled --quiet demo-java@ping.service
grep -qxF "JAVA: tuple[str, ...] = ('ping',)" /usr/local/sbin/demo-deploy

step "The piece runs its jar from the current version, on loopback"
mkdir -p /srv/demo/releases/v0.0.1
cp -r "$canone/scripts/infra/ping/build/ping" /srv/demo/releases/v0.0.1/
ln -sfn /srv/demo/releases/v0.0.1 /srv/demo/current
systemctl start demo-java@ping.service
for attempt in $(seq 30); do
    code=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8099/ || true)
    [ "$code" = 204 ] && break
    sleep 1
done
test "$code" = 204

step "deploy.py restarts it"
# restart() of the deploy.py that install.py wrote. This machine has no server, so restart() fails
# on the server, after the piece.
before=$(systemctl show -p InvocationID --value demo-java@ping.service)
python3 - <<'EOF'
import importlib.machinery
import importlib.util
import subprocess

loader = importlib.machinery.SourceFileLoader("deploy", "/usr/local/sbin/demo-deploy")
deploy = importlib.util.module_from_spec(importlib.util.spec_from_loader("deploy", loader))
loader.exec_module(deploy)
deploy.HEALTH_SECONDS = 1
try:
    deploy.restart()
except (deploy.Unhealthy, subprocess.CalledProcessError):
    pass
EOF
test "$(systemctl show -p InvocationID --value demo-java@ping.service)" != "$before"
systemctl is-active --quiet demo-java@ping.service
systemctl stop demo.service

step "It reaches only localhost"
systemctl show -p IPAddressDeny --value demo-java@ping.service | grep -qF '0.0.0.0/0'
systemctl show -p IPAddressAllow --value demo-java@ping.service | grep -qF '127.0.0.0/8'

step "It stops without failing, and keeps its exposure"
systemctl stop demo-java@ping.service
test "$(systemctl show -p Result --value demo-java@ping.service)" = success
systemd-analyze security --threshold=20 demo-java@ping.service > /dev/null

step "uninstall.py app takes the unit"
python3 "$canone/plantilla/infra/uninstall.py" demo app
test ! -e /etc/systemd/system/demo-java@.service
test ! -e /etc/systemd/system/multi-user.target.wants/demo-java@ping.service
