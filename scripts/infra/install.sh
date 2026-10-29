#!/bin/sh
# Runs install.py on a Debian 13 with systemd running: a new machine needs two --signer, which
# go to allowed_signers for the namespace deploy.py checks and are only added afterwards; it fails
# without systemd-timesyncd enabled; and apt reads the automatic reboot at 04:00. install.py runs
# as root, with an account that already administers, so it asks no password.
#
#     sh install.sh <canone>
set -eu
install=$1/plantilla/infra/install.py
work=$(mktemp -d)
signers=/etc/demo/allowed_signers
trap 'status=$?; systemctl enable --quiet systemd-timesyncd.service; rm -rf "$work"; exit "$status"' EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" 2> "$work/error"; then exit 1; fi; }
for name in a b s1 s2 s3 x; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
key() { cat "$work/$1.pub"; }
run() {
    python3 "$install" demo demo.example 64mb --admin operador --key "$(key a)" --key "$(key b)" "$@"
}
# An account that already administers: install.py only adds its keys, and asks no password.
id operador > /dev/null 2>&1 || useradd --create-home --groups sudo operador

step "A new machine needs two --signer, and each must be a key"
fails run --signer "$(key s1)"
grep -qF 'A new machine needs two --signer: yours and one kept elsewhere.' "$work/error"
test ! -s "$signers"
fails run --signer "$(key s1)" --signer "not a key"
test ! -s "$signers"

step "Each signer signs for the namespace deploy, and no other"
run --signer "$(key s1)" --signer "$(key s2)"
test "$(grep -c '^deploy namespaces="deploy" ssh-ed25519 ' "$signers")" = 2
echo release > "$work/sums"
for name in s1 s2; do
    ssh-keygen -Y sign -q -n deploy -f "$work/$name" "$work/sums"
    ssh-keygen -Y verify -q -f "$signers" -I deploy -n deploy -s "$work/sums.sig" < "$work/sums"
    rm "$work/sums.sig"
done
ssh-keygen -Y sign -q -n other -f "$work/s1" "$work/sums"
fails ssh-keygen -Y verify -q -f "$signers" -I deploy -n other -s "$work/sums.sig" < "$work/sums"
rm "$work/sums.sig"
ssh-keygen -Y sign -q -n deploy -f "$work/x" "$work/sums"
fails ssh-keygen -Y verify -q -f "$signers" -I deploy -n deploy -s "$work/sums.sig" < "$work/sums"

step "Afterwards --signer only adds, once"
run
test "$(wc -l < "$signers")" = 2
run --signer "$(key s3)" --signer "$(key s1)"
test "$(wc -l < "$signers")" = 3
grep -qF "$(key s3)" "$signers"

step "Without systemd-timesyncd enabled, it fails"
systemctl disable --quiet systemd-timesyncd.service
fails run
grep -qxF 'systemd-timesyncd is not enabled, and the clock would drift.' "$work/error"
systemctl enable --quiet systemd-timesyncd.service

step "apt reboots by itself at 04:00 when a package asks for it"
test "$(apt-config dump --format '%v%n' Unattended-Upgrade::Automatic-Reboot)" = true
test "$(apt-config dump --format '%v%n' Unattended-Upgrade::Automatic-Reboot-Time)" = 04:00
