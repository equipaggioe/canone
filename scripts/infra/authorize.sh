#!/bin/sh
# Runs authorize.py as root on a Debian 13: it adds the key to /root/.ssh/authorized_keys once,
# with modes 700 and 600, keeps the keys that were there, and writes nothing for a line that is not
# a key.
#
#     sh authorize.sh <canone>
set -eu
program=$1/plantilla/infra/authorize.py
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" 2> "$work/error"; then exit 1; fi; }
keys=/root/.ssh/authorized_keys
for name in a b; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
key() { cat "$work/$1.pub"; }
rm -rf /root/.ssh

step "it adds the key with modes 700 and 600"
python3 "$program" "$(key a)"
test "$(stat -c '%a' /root/.ssh)" = 700
test "$(stat -c '%a' "$keys")" = 600
grep -qxF "$(key a)" "$keys"

step "run again it adds nothing, and another key goes after the first"
python3 "$program" "$(key a)"
python3 "$program" "$(key b)"
test "$(wc -l < "$keys")" = 2
test "$(head -n 1 "$keys")" = "$(key a)"

step "a line that is not a key writes nothing"
fails python3 "$program" "not a key"
grep -qxF 'That is not a public key, and nothing was written.' "$work/error"
fails python3 "$program" "$(key a)
$(key b)"
test "$(wc -l < "$keys")" = 2
