#!/bin/sh
# Runs packages.py on a Debian 13: --list names the packages of each option and installs nothing,
# --all names those of every option, and without --list it installs all of them, so each name
# exists in Debian 13, and Caddy comes from its repository, in the series of caddy.pref.
#
#     sh packages.sh <canone>
set -eu
canone=$1
program=$canone/plantilla/infra/packages.py
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
step() { printf '\n== %s\n' "$*"; }
# Under set -e a command after ! never stops the script: not does.
not() { if "$@"; then echo "should have failed: $*"; exit 1; fi; }
installed() { dpkg-query -W -f '${Status}' "$1" 2>/dev/null | grep -qx 'install ok installed'; }

step "--list names the base packages and installs nothing"
python3 "$program" --list > "$work/base"
# The packages of every machine that «Máquina» of despliegue.md names.
printf '%s\n' caddy postgresql valkey-server restic sudo python3 nftables unattended-upgrades \
    systemd-timesyncd ca-certificates | sort > "$work/named"
sort "$work/base" | cmp - "$work/named"
not grep -qx coturn "$work/base"
not grep -qx postgresql-17-postgis-3 "$work/base"
not grep -qx openjdk-21-jre-headless "$work/base"
not grep -qx chromium-headless-shell "$work/base"
not installed caddy

step "--list adds the package of each option, and an extension of postgresql adds none"
python3 "$program" --list --extension postgis --extension pg_trgm --turn --logs --java demo \
    --browser attempt=minutely > "$work/all"
grep -qx postgresql-17-postgis-3 "$work/all"
grep -qx coturn "$work/all"
grep -qx systemd-journal-remote "$work/all"
grep -qx wireguard-tools "$work/all"
grep -qx openjdk-21-jre-headless "$work/all"
grep -qx chromium-headless-shell "$work/all"
test "$(wc -l < "$work/all")" -eq "$(($(wc -l < "$work/base") + 6))"

step "--all names the packages of every option"
python3 "$program" --list --all > "$work/every"
cmp "$work/all" "$work/every"

step "without --list it installs each package"
python3 "$program" --all
while read -r name; do
    installed "$name" || { echo "$name is not installed"; exit 1; }
done < "$work/all"

step "Caddy comes from its repository, in the series of caddy.pref, and unattended-upgrades updates it"
series=$(sed -n 's/^Pin: version \(..*\)\*$/\1/p' "$canone/plantilla/infra/caddy.pref")
version=$(dpkg-query -W -f '${Version}' caddy)
case "$version" in "$series"*) ;; *) echo "caddy $version is not of the series $series"; exit 1 ;; esac
apt-config dump | grep -qF 'Unattended-Upgrade::Origins-Pattern:: "origin=cloudsmith/caddy/stable";'
