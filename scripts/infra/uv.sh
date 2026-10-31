#!/bin/sh
# Runs uv.py on a Debian 13: an archive that does not match its SHA-256, served from this machine
# in place of GitHub, installs nothing and leaves the uv there was, and the archive of GitHub
# installs in /usr/local/bin, owned by root, the uv that each pyproject.toml of the template
# requires, also over itself.
#
#     sh uv.sh <canone>
set -eu
canone=$1
work=$(mktemp -d)
pid=
cleanup() {
    status=$?
    if [ -n "$pid" ]; then kill "$pid" 2>/dev/null || true; fi
    # The output of the last command that was meant to fail.
    if [ "$status" -ne 0 ] && [ -f "$work/error" ]; then cat "$work/error"; fi
    rm -rf "$work"
    exit "$status"
}
trap cleanup EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" > "$work/error" 2>&1; then exit 1; fi; }
version=$(python3 -c '
import sys, tomllib
with open(sys.argv[1], "rb") as file:
    print(tomllib.load(file)["tool"]["uv"]["required-version"].removeprefix("=="))
' "$canone/plantilla/server/pyproject.toml")
releases=https://github.com/astral-sh/uv/releases/download
archive=uv-$(uname -m)-unknown-linux-gnu.tar.gz
installed() { /usr/local/bin/uv --version | grep -Eq "^uv $version( |$)"; }

# The archive of GitHub with one more byte, served from this machine.
mkdir -p "$work/releases/$version"
curl -fsSL -o "$work/releases/$version/$archive" "$releases/$version/$archive"
printf x >> "$work/releases/$version/$archive"
python3 -m http.server --bind 127.0.0.1 --directory "$work/releases" 9000 > /dev/null 2>&1 &
pid=$!
until curl -s -o /dev/null http://127.0.0.1:9000/; do sleep 0.1; done
sed "s#$releases#http://127.0.0.1:9000#" "$canone/plantilla/infra/uv.py" > "$work/uv.py"

step "an archive that does not match installs nothing"
test ! -e /usr/local/bin/uv
fails python3 "$work/uv.py"
grep -q "does not match its SHA-256" "$work/error"
test ! -e /usr/local/bin/uv
test ! -e /usr/local/bin/uv.new

step "the archive of GitHub installs the version of pyproject.toml"
python3 "$canone/plantilla/infra/uv.py"
installed
test "$(stat -c '%a %U' /usr/local/bin/uv)" = "755 root"

step "an archive that does not match leaves the uv there was"
fails python3 "$work/uv.py"
installed

step "it installs again over itself"
python3 "$canone/plantilla/infra/uv.py"
installed
test ! -e /usr/local/bin/uv.new
