#!/bin/sh
# Runs a backup on a Debian 13 that install.py set up, asked by a receiver in another namespace
# with plantilla/receiver/backup.sh: without the tunnel nothing starts, the receiver keeps the dump
# and the files and the server cannot delete them, the key of the receiver opens no shell nor
# another tunnel, a backup cut in the middle does not stop the next, a backup cut by its time limit
# fails, and what restic restores goes back on the database install.py creates. The receiver logs
# in as the account receptora, with the restic-rest-server of Debian 13, and the server is 192.0.2.2.
#
#     sh backup.sh <canone>
set -eu
canone=$1
work=$(mktemp -d)
repo=$work/repo
limit=/etc/systemd/system/demo-backup.service.d/limit.conf
password=backup-password-$$
pids=
cleanup() {
    status=$?
    for pid in $pids; do kill "$pid" 2>/dev/null || true; done
    # The output of the last command that was meant to fail.
    if [ "$status" -ne 0 ] && [ -f "$work/error" ]; then cat "$work/error"; fi
    ip netns del receiver 2>/dev/null || true
    rm -rf "$work" "$(dirname "$limit")"
    systemctl daemon-reload
    exit "$status"
}
trap cleanup EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" > "$work/error" 2>&1; then exit 1; fi; }
# As the receiver: in its namespace, with its account.
receptora() { ip netns exec receiver runuser -u receptora -- "$@"; }
ssh_receiver() { receptora ssh -T -o BatchMode=yes "$@" demo-receiver@192.0.2.2; }
backups() { RESTIC_PASSWORD=$password restic --no-cache --repo "$repo/demo" snapshots --json | python3 -c 'import json, sys; print(len(json.load(sys.stdin)))'; }
invocation() { systemctl show --property=InvocationID --value demo-backup.service; }
for name in a b s1 s2; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
key() { cat "$work/$1.pub"; }
# An account that already administers: install.py only adds its keys, and asks no password.
id operador > /dev/null 2>&1 || useradd --create-home --groups sudo operador
python3 "$canone/plantilla/infra/install.py" demo demo.example 64mb --admin operador \
    --key "$(key a)" --key "$(key b)" --signer "$(key s1)" --signer "$(key s2)" --owner owner
echo "restic_password=$password" | python3 "$canone/plantilla/infra/credentials.py" demo

step "The receiver, at 192.0.2.1, with its key in /etc/demo/receivers"
ip netns add receiver
ip -n receiver link set lo up
ip link add to-receiver type veth peer name receiver netns receiver
ip addr add 192.0.2.2/24 dev to-receiver
ip link set to-receiver up
ip -n receiver addr add 192.0.2.1/24 dev receiver
ip -n receiver link set receiver up
useradd --create-home receptora
runuser -u receptora -- sh -c 'mkdir -m 700 ~/.ssh && ssh-keygen -q -t ed25519 -N "" -f ~/.ssh/id_ed25519'
cat ~receptora/.ssh/id_ed25519.pub >> /etc/demo/receivers
echo "192.0.2.2 $(cat /etc/ssh/ssh_host_ed25519_key.pub)" > ~receptora/.ssh/known_hosts
chown receptora: ~receptora/.ssh/known_hosts
install -d -o receptora "$repo"
chmod 755 "$work"

step "Data in the database and in the files"
runuser -u demo_owner -- psql -X -v ON_ERROR_STOP=1 --dbname=demo \
    -c "CREATE TABLE place (id int PRIMARY KEY, name text)" -c "INSERT INTO place VALUES (1, 'first-$$')"
install -d -o demo -g demo /var/lib/demo/files
echo "file-$$" > /var/lib/demo/files/one

step "Without the tunnel, nothing starts"
before=$(invocation)
fails ssh_receiver
grep -qxF 'backup: no tunnel on 127.0.0.1:8001' "$work/error"
test "$(invocation)" = "$before"
test ! -e /var/lib/demo/last-backup

step "The receiver asks, and keeps the dump and the files"
receptora sh "$canone/plantilla/receiver/backup.sh" demo 192.0.2.2 "$repo" | tee "$work/first"
grep -qxF 'backup: success' "$work/first"
test "$(backups)" = 1
first=$(stat -c %Y /var/lib/demo/last-backup)

step "A second backup adds a snapshot and moves last-backup"
sleep 1
receptora sh "$canone/plantilla/receiver/backup.sh" demo 192.0.2.2 "$repo" > /dev/null
test "$(backups)" = 2
test "$(stat -c %Y /var/lib/demo/last-backup)" -gt "$first"

step "With the flags of backup.sh, rest-server lets restic add but not delete"
flags=$(sed -n 's/^"$server" \(.*\) &$/\1/p' "$canone/plantilla/receiver/backup.sh" | sed "s#\"\$3\"#$repo#")
test -n "$flags"
# setpriv execs rest-server, so kill reaches it, and the repository stays the one of receptora.
# shellcheck disable=SC2086
ip netns exec receiver setpriv --reuid=receptora --regid=receptora --init-groups \
    restic-rest-server $flags > /dev/null 2>&1 &
rest=$!
pids="$pids $rest"
until receptora curl -s -o /dev/null http://127.0.0.1:8001/; do sleep 0.2; done
remote=rest:http://127.0.0.1:8001/demo/
fails receptora env RESTIC_PASSWORD="$password" restic --no-cache --repo "$remote" forget --keep-last 1 --prune
test "$(backups)" = 2
kill "$rest"

step "The key of the receiver opens no shell nor another tunnel"
fails receptora ssh -T -o BatchMode=yes demo-receiver@192.0.2.2 sh -c "echo shell-$$"
if grep -qF "shell-$$" "$work/error"; then exit 1; fi
fails receptora ssh -T -o BatchMode=yes -o ExitOnForwardFailure=yes \
    -R 127.0.0.1:9001:127.0.0.1:9001 demo-receiver@192.0.2.2
fails receptora ssh -o BatchMode=yes -W 127.0.0.1:22 demo-receiver@192.0.2.2 < /dev/null
grep -qF 'administratively prohibited' "$work/error"

step "A backup cut while it holds its lock, as by a reboot, does not stop the next one"
head -c 200000000 /dev/urandom > /var/lib/demo/files/big
receptora sh "$canone/plantilla/receiver/backup.sh" demo 192.0.2.2 "$repo" > "$work/cut" 2>&1 &
cut=$!
i=0
until [ -n "$(ls "$repo/demo/locks")" ]; do
    i=$((i + 1))
    if [ "$i" -ge 300 ]; then echo "restic took no lock"; exit 1; fi
    sleep 0.1
done
systemctl kill --signal=SIGKILL demo-backup.service
if wait "$cut"; then exit 1; fi
rm /var/lib/demo/files/big
receptora sh "$canone/plantilla/receiver/backup.sh" demo 192.0.2.2 "$repo" | tee "$work/next"
grep -qxF 'backup: success' "$work/next"
test "$(backups)" = 3

step "A backup that reaches its time limit fails, scaled down from 4 h to 5 s"
mkdir -p "$(dirname "$limit")"
printf '[Service]\nTimeoutStartSec=5s\n' > "$limit"
systemctl daemon-reload
# The tunnel opens, but no rest-server answers behind it, and restic retries.
fails ssh_receiver -o ExitOnForwardFailure=yes -R 127.0.0.1:8001:127.0.0.1:8001
grep -qxF 'backup: timeout' "$work/error"
rm "$limit"
systemctl daemon-reload

step "What restic restores goes back on the database install.py creates"
RESTIC_PASSWORD=$password restic --no-cache --repo "$repo/demo" restore latest --target "$work/restore" > /dev/null
runuser -u postgres -- dropdb demo
python3 -c "import sys; sys.path.insert(0, '$canone/plantilla/infra'); import install; install.create_database('demo', [])"
chmod 755 "$work/restore" "$work/restore/var" "$work/restore/var/lib" "$work/restore/var/lib/demo-dump"
runuser -u demo_owner -- pg_restore --exit-on-error --dbname=demo "$work/restore/var/lib/demo-dump/demo.dump"
test "$(runuser -u demo_owner -- psql -XAt --dbname=demo -c "SELECT name FROM place")" = "first-$$"
test "$(cat "$work/restore/var/lib/demo/files/one")" = "file-$$"
