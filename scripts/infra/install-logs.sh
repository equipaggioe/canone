#!/bin/sh
# Runs install.py --logs on a Debian 13 with systemd running, and a central end in another
# namespace: the flags go together, the journal and PostgreSQL arrive through the tunnel, the
# uploader keeps retrying while the central end is down, a second run keeps the key, a run without
# --logs fails, and journald deletes an entry within a file of its retention. install.py runs as
# root, with umask 077 and an account that already administers, so it asks no password.
#
#     sh install-logs.sh <install.py>
set -eu
install=$1
work=$(mktemp -d)
upload=systemd-journal-upload.service
retry=/etc/systemd/system/systemd-journal-upload.service.d/demo.conf
pids=
cleanup() {
    status=$?
    for pid in $pids; do kill "$pid" 2>/dev/null || true; done
    ip netns del central 2>/dev/null || true
    if [ -f "$work/retry.conf" ]; then mv "$work/retry.conf" "$retry"; fi
    rm -rf "$work" /etc/systemd/journald.conf.d/99-retention.conf
    systemctl daemon-reload
    systemctl restart systemd-journald.service
    exit "$status"
}
trap cleanup EXIT
step() { printf '\n== %s\n' "$*"; }
received() {
    journalctl --directory="$work/received" --output=cat 2>/dev/null | grep -c -- "$1" || true
}
arrives() {
    i=0
    until [ "$(received "$1")" -ge 1 ]; do
        i=$((i + 1))
        if [ "$i" -ge "$2" ]; then echo "$1 did not arrive"; exit 1; fi
        sleep 1
    done
}
receiver() {
    ip netns exec central /usr/lib/systemd/systemd-journal-remote --listen-http=10.77.0.1:19532 \
        --output="$work/received/" --split-mode=host &
    receiver=$!
    pids="$pids $receiver"
}
fails() { if "$@" 2> "$work/error"; then exit 1; fi; }
# Whoever deploys may have a strict umask, and install.py does not take it.
umask 077
for name in a b; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
run() {
    python3 "$install" demo demo.example 64mb --admin operador \
        --key "$(cat "$work/a.pub")" --key "$(cat "$work/b.pub")" "$@"
}
logs() { run --logs 192.0.2.1:51820 --logs-key "$(cat "$work/central.pub")" --logs-ip 10.77.0.2; }
# An account that already administers: install.py only adds its keys, and asks no password.
id operador > /dev/null 2>&1 || useradd --create-home --groups sudo operador

step "The central end, at 192.0.2.1, which stands for the internet"
ip netns add central
ip -n central link set lo up
ip link add to-central type veth peer name central netns central
ip addr add 192.0.2.2/24 dev to-central
ip link set to-central up
ip -n central addr add 192.0.2.1/24 dev central
ip -n central link set central up
wg genkey > "$work/central.key"
wg pubkey < "$work/central.key" > "$work/central.pub"
ip -n central link add wg0 type wireguard
ip -n central addr add 10.77.0.1/24 dev wg0
ip netns exec central wg set wg0 listen-port 51820 private-key "$work/central.key"
ip -n central link set wg0 up
mkdir "$work/received"
receiver

step "The three flags go together"
fails run --logs-key x
grep -x -- '--logs-key and --logs-ip need --logs.' "$work/error"
fails run --logs 192.0.2.1:51820
grep -x -- '--logs needs --logs-key and --logs-ip.' "$work/error"

step "The first run brings up the tunnel and the uploader, and prints the key"
logs | tee "$work/first.log"
key=$(sed -n 's/^The key of this machine, for equipaggio: //p' "$work/first.log")
test -n "$key"
test "$(stat -c %a /etc/wireguard/logs.conf)" = 600
ip netns exec central wg set wg0 peer "$key" allowed-ips 10.77.0.2/32
systemctl is-enabled wg-quick@logs.service "$upload"
systemctl is-active valkey-server@demo.service

step "An entry arrives, in the file of 10.77.0.2"
logger -t install-logs "first-$$"
arrives "first-$$" 60
ls "$work/received" | grep -q '^remote-10\.77\.0\.2'

step "PostgreSQL writes to the journal, not to /var/log/postgresql, and its log arrives"
runuser -u postgres -- psql -Xqc "DO \$\$ BEGIN RAISE LOG 'postgres-$$'; END \$\$" > /dev/null
arrives "postgres-$$" 60
journalctl -u postgresql@17-main.service --output=cat | grep -q -- "postgres-$$"
if grep -q -- "postgres-$$" /var/log/postgresql/postgresql-17-main.log; then exit 1; fi

step "With the central end down, the uploader keeps retrying, and sends once it is back"
kill "$receiver"
before=$(systemctl show -P NRestarts "$upload")
logger -t install-logs "down-$$"
i=0
until [ "$(systemctl show -P NRestarts "$upload")" -ge $((before + 7)) ]; do
    i=$((i + 1))
    if [ "$i" -ge 120 ]; then echo "fewer than 7 retries"; exit 1; fi
    sleep 1
done
if systemctl is-failed --quiet "$upload"; then exit 1; fi
receiver
arrives "down-$$" 120

step "Without StartLimitIntervalSec=0, the unit of Debian ends failed"
mv "$retry" "$work/retry.conf"
systemctl daemon-reload
kill "$receiver"
systemctl restart "$upload"
i=0
until systemctl is-failed --quiet "$upload"; do
    i=$((i + 1))
    if [ "$i" -ge 60 ]; then echo "the unit did not fail"; exit 1; fi
    sleep 1
done
mv "$work/retry.conf" "$retry"
systemctl daemon-reload
systemctl reset-failed "$upload"
receiver

step "A second run keeps the key, and the journal keeps arriving"
logs | tee "$work/second.log"
test "$(sed -n 's/^The key of this machine, for equipaggio: //p' "$work/second.log")" = "$key"
test "$(stat -c %a /etc/wireguard/logs.conf)" = 600
logger -t install-logs "second-$$"
arrives "second-$$" 60

step "A run without --logs fails on a machine that sends"
cp /etc/wireguard/logs.conf "$work/before.conf"
fails run
grep -qF 'This machine sends its journal to equipaggio, so it needs --logs.' "$work/error"
cmp /etc/wireguard/logs.conf "$work/before.conf"

step "journald reads the template: on disk, 365 days, a file per day"
config=$(systemd-analyze cat-config systemd/journald.conf)
echo "$config" | grep -qx 'Storage=persistent'
echo "$config" | grep -qx 'MaxRetentionSec=365day'
echo "$config" | grep -qx 'MaxFileSec=1day'
test -f "/var/log/journal/$(cat /etc/machine-id)/system.journal"

step "Scaled down to 20 s and a file of 5 s, an entry goes after 15 s and within 30 s, unrotated by hand"
printf '[Journal]\nMaxRetentionSec=20s\nMaxFileSec=5s\n' > /etc/systemd/journald.conf.d/99-retention.conf
systemctl restart systemd-journald.service
journalctl --rotate
logger -t install-logs "old-$$"
kept() { journalctl --output=cat | grep -c -- "old-$$" || true; }
i=0
while [ "$(kept)" -ge 1 ]; do
    i=$((i + 1))
    if [ "$i" -ge 30 ]; then echo "still kept after 30 s"; exit 1; fi
    # A machine always writes, and journald rotates and deletes when it does.
    logger -t install-logs "tick-$i"
    sleep 1
done
echo "deleted after ${i} s"
test "$i" -ge 15
