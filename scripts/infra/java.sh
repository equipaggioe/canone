#!/bin/sh
# Runs a piece in Java under the unit of install.py --java, on a Debian 13 with systemd running:
# without --java there is no unit and deploy.py restarts no piece; a name that cannot name a unit
# fails; with --java the unit is enabled and deploy.py restarts it; the piece runs its jar from the
# current version, answers on loopback, reaches only localhost, stops without failing and keeps an
# exposure of 2.0 or less; and uninstall.py app takes the unit.
#
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

step "With --java the unit is enabled, and deploy.py restarts it"
run --java ping
test -f /etc/systemd/system/demo-java@.service
systemctl is-enabled --quiet demo-java@ping.service
grep -qxF "JAVA: tuple[str, ...] = ('ping',)" /usr/local/sbin/demo-deploy

step "The piece runs its jar from the current version, on loopback"
mkdir -p "$work/ping/src"
: > "$work/ping/dependencies.txt"
cat > "$work/ping/src/Ping.java" << 'EOF'
import com.sun.net.httpserver.HttpServer;
import java.net.InetAddress;
import java.net.InetSocketAddress;

public class Ping {
    public static void main(String[] args) throws Exception {
        var server = HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), 8099), 0);
        server.createContext("/", exchange -> { exchange.sendResponseHeaders(204, -1); exchange.close(); });
        server.start();
    }
}
EOF
python3 "$canone/plantilla/scripts/java.py" "$work/ping" Ping "$work/out"
mkdir -p /srv/demo/releases/v0.0.1
cp -r "$work/out/ping" /srv/demo/releases/v0.0.1/
ln -sfn /srv/demo/releases/v0.0.1 /srv/demo/current
systemctl start demo-java@ping.service
for attempt in $(seq 30); do
    code=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8099/ || true)
    [ "$code" = 204 ] && break
    sleep 1
done
test "$code" = 204

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
