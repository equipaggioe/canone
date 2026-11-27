#!/bin/sh
# Runs Python with the system call filter of each unit that runs the app: numpy imports, and its
# OpenBLAS calls mbind, which the filter would deny without its exception (ADR-0149). Without the
# exception the same import dies, so the check bites.
#
#     sh seccomp.sh <canone>
set -eu
canone=$1
infra=$canone/plantilla/infra
step() { printf '\n== %s\n' "$*"; }
venv=$(mktemp -d)
trap 'rm -rf "$venv"' EXIT
python3 -m venv "$venv"
"$venv/bin/pip" install --quiet numpy==2.5.4
# The sandboxing of a unit that systemd-run can take as properties.
sandboxing() {
  grep -E '^(SystemCallFilter|SystemCallArchitectures|MemoryDenyWriteExecute)=' "$1"
}
# Imports numpy with the sandboxing of the unit; with "drop", without the mbind exception.
imports() {
  properties=$(sandboxing "$1")
  if [ "${2:-}" = drop ]; then
    properties=$(printf '%s\n' "$properties" | grep -vx 'SystemCallFilter=mbind')
  fi
  set -- --quiet --wait --pipe
  while IFS= read -r line; do
    set -- "$@" -p "$line"
  done <<LINES
$properties
LINES
  systemd-run "$@" "$venv/bin/python" -c "import numpy" > /dev/null 2>&1
}
for unit in PRODUCTO.service PRODUCTO-migrate@.service PRODUCTO-mock@.service \
    PRODUCTO-purge.service PRODUCTO-sweep.service PRODUCTO-task@.service \
    PRODUCTO-browser@.service PRODUCTO-worker@.service; do
  step "$unit imports numpy"
  # The filter is there, with its exception: without them the check proves nothing.
  sandboxing "$infra/$unit" | grep -qx 'SystemCallFilter=~@privileged @resources'
  sandboxing "$infra/$unit" | grep -qx 'SystemCallFilter=mbind'
  imports "$infra/$unit"
  step "$unit without the mbind exception does not"
  # Under set -e, a command after ! never stops the script: the if does.
  if imports "$infra/$unit" drop; then exit 1; fi
done
