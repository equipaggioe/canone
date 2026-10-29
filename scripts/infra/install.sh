#!/bin/sh
# Runs install.py on a Debian 13 with systemd running: a new machine needs two --signer, which
# go to allowed_signers for the namespace deploy.py checks and are only added afterwards; it fails
# without systemd-timesyncd enabled or without ca-certificates; apt reads the automatic reboot at 04:00; credentials.py
# encrypts each field where its unit loads it; Valkey opens only its socket, for the group of the
# app, with its maxmemory; and root has no password, and an account of the app does not administer.
# install.py runs as root, with an account that already administers, so it asks no password.
#
#     sh install.sh <canone>
set -eu
install=$1/plantilla/infra/install.py
credentials=$1/plantilla/infra/credentials.py
work=$(mktemp -d)
signers=/etc/demo/allowed_signers
certificates=/etc/ssl/certs/ca-certificates.crt
cleanup() {
    status=$?
    systemctl enable --quiet systemd-timesyncd.service
    if [ -f "$work/certificates" ]; then mv "$work/certificates" "$certificates"; fi
    rm -rf "$work"
    exit "$status"
}
trap cleanup EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" 2> "$work/error"; then exit 1; fi; }
for name in a b s1 s2 s3 x; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
key() { cat "$work/$1.pub"; }
run() {
    python3 "$install" demo demo.example 64mb --admin operador --key "$(key a)" --key "$(key b)" \
        --owner owner "$@"
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

step "Without ca-certificates, it fails"
mv "$certificates" "$work/certificates"
fails run
grep -qxF 'ca-certificates is not installed, and deploy.py would not reach GitHub.' "$work/error"
mv "$work/certificates" "$certificates"

step "apt reboots by itself at 04:00 when a package asks for it"
test "$(apt-config dump --format '%v%n' Unattended-Upgrade::Automatic-Reboot)" = true
test "$(apt-config dump --format '%v%n' Unattended-Upgrade::Automatic-Reboot-Time)" = 04:00

step "credentials.py encrypts each field in the folder and under the name its unit loads it with"
credentials() { python3 "$credentials" demo; }
decrypt() { systemd-creds decrypt --name="$1" "/etc/credstore.encrypted/$2" -; }
printf 'health_token=t-1\nrestic_password=r-1\ngithub_token=g-1\n' | credentials
test "$(decrypt app_health_token demo/health_token)" = t-1
test "$(decrypt restic_password demo-backup/restic_password)" = r-1
test "$(decrypt github_token demo-deploy/github_token)" = g-1

step "It writes only the fields it reads, and nothing when a line is wrong"
echo 'health_token=t-2' | credentials
test "$(decrypt app_health_token demo/health_token)" = t-2
test "$(decrypt restic_password demo-backup/restic_password)" = r-1
for input in 'health_token=t-3\nnot a field' 'Health=x' 'health_token=' 'a=1\na=2' '# only a comment'; do
    printf '%b\n' "$input" | fails credentials
done
test "$(decrypt app_health_token demo/health_token)" = t-2
for field in database_url turn_secret; do
    echo "$field=x" | fails credentials
    grep -qxF "install.py writes $field." "$work/error"
done

step "Valkey listens only on its socket, which only the group of the app opens, with its maxmemory"
socket=/run/valkey-demo/valkey-server.sock
test "$(stat -c '%G %a' "$socket")" = "demo 770"
test "$(runuser -u demo -- valkey-cli -s "$socket" ping)" = PONG
fails runuser -u nobody -- valkey-cli -s "$socket" ping
setting() { runuser -u demo -- valkey-cli -s "$socket" --raw config get "$1" | tail -n 1; }
test "$(setting port)" = 0
test "$(setting maxmemory)" = 67108864
test "$(setting maxmemory-policy)" = noeviction
test "$(systemctl is-enabled valkey-server.service || true)" = disabled
test "$(sysctl -n vm.overcommit_memory)" = 1

step "root has no password, and the account that administers is not one of the app"
test "$(passwd --status root | cut -d ' ' -f 2)" = L
for account in demo demo_owner demo-receiver; do
    fails python3 "$install" demo demo.example 64mb --admin "$account" --key "$(key a)" \
        --key "$(key b)" --owner owner
    grep -qxF "$account is an account of the app, not the one that administers." "$work/error"
done
