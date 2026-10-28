#!/bin/sh
# Uploads a journal from a machine namespace to a central namespace, through the tunnel of the
# template: it arrives, in the file of the address of its key, and another key that claims the same
# address does not reach the receiver.
#
#     sh logs.sh <logs.conf> <journal-upload.conf>
set -eu
work=$(mktemp -d)
pids=
cleanup() {
    status=$?
    for pid in $pids; do kill "$pid" 2>/dev/null || true; done
    for namespace in central machine other; do ip netns del "$namespace" 2>/dev/null || true; done
    rm -rf "$work" /etc/systemd/journal-upload.conf.d/00-app.conf
    exit "$status"
}
trap cleanup EXIT
for namespace in central machine other; do
    ip netns add "$namespace"
    ip -n "$namespace" link set lo up
done
# 192.0.2.0/24 and 198.51.100.0/24 stand for the internet.
ip link add central type veth peer name machine
ip link add central-other type veth peer name other
ip link set central netns central
ip link set central-other netns central
ip link set machine netns machine
ip link set other netns other
ip -n central addr add 192.0.2.1/24 dev central
ip -n central addr add 198.51.100.1/24 dev central-other
ip -n machine addr add 192.0.2.2/24 dev machine
ip -n other addr add 198.51.100.2/24 dev other
ip -n central link set central up
ip -n central link set central-other up
ip -n machine link set machine up
ip -n other link set other up
umask 077
for name in central machine other; do
    wg genkey > "$work/$name.key"
    wg pubkey < "$work/$name.key" > "$work/$name.pub"
done
# The central end knows only the key of the machine, at 10.77.0.2.
ip -n central link add wg0 type wireguard
ip -n central addr add 10.77.0.1/24 dev wg0
ip netns exec central wg set wg0 listen-port 51820 private-key "$work/central.key" \
    peer "$(cat "$work/machine.pub")" allowed-ips 10.77.0.2/32
ip -n central link set wg0 up
mkdir "$work/received"
ip netns exec central /usr/lib/systemd/systemd-journal-remote --listen-http=10.77.0.1:19532 \
    --output="$work/received/" --split-mode=host &
pids="$pids $!"
# Each sender brings up the tunnel of the template, as install.py writes it.
up() {
    mkdir "$work/$1"
    sed -e "s|LLAVE|$(cat "$work/$1.key")|" -e "s|TUNEL|10.77.0.2|" \
        -e "s|CENTRAL|$(cat "$work/central.pub")|" -e "s|EXTREMO|$2:51820|" "$3" > "$work/$1/logs.conf"
    ip netns exec "$1" wg-quick up "$work/$1/logs.conf"
}
up machine 192.0.2.1 "$1"
up other 198.51.100.1 "$1"
mkdir -p /etc/systemd/journal-upload.conf.d
install -m 644 "$2" /etc/systemd/journal-upload.conf.d/00-app.conf
# A journal with one entry from each sender.
journal() {
    printf '__REALTIME_TIMESTAMP=%s000000\n__MONOTONIC_TIMESTAMP=1\n_BOOT_ID=%s\nMESSAGE=%s\n\n' \
        "$(date +%s)" "$(tr -d - < /proc/sys/kernel/random/boot_id)" "$2" \
        | /usr/lib/systemd/systemd-journal-remote --output="$work/$1.journal" -
}
upload() {
    timeout --signal=KILL 20 ip netns exec "$1" /usr/lib/systemd/systemd-journal-upload \
        --file="$work/$1.journal" --save-state="$work/$1.state" --follow=no
}
received() {
    journalctl --directory="$work/received" --output=cat "MESSAGE=$1" | wc -l
}
journal machine from-machine
journal other from-other
sleep 1
upload machine
test "$(received from-machine)" = 1
ls "$work/received" | grep -q '^remote-10\.77\.0\.2'
if upload other; then exit 1; fi
test "$(received from-other)" = 0
