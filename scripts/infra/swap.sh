#!/bin/sh
# Runs swap.py on a machine with less swap than memory: it leaves as much swap as memory, with
# /swapfile of root and mode 600 in /etc/fstab once; run again it changes nothing; and a /swapfile
# that falls short is made again.
#
#     sh swap.sh <canone>
set -eu
canone=$1
program=$canone/plantilla/infra/swap.py
step() { printf '\n== %s\n' "$*"; }
kib() { awk -v field="$1:" '$1 == field {print $2}' /proc/meminfo; }
enough() { test "$(kib SwapTotal)" -ge "$(kib MemTotal)"; }
lines() { grep -c '^/swapfile ' /etc/fstab || true; }

step "with less swap than memory it creates /swapfile"
! enough
python3 "$program"
enough
test "$(stat -c '%a %U' /swapfile)" = "600 root"
swapon --show=NAME --noheadings | grep -qx /swapfile
test "$(lines)" -eq 1

step "run again it changes nothing"
python3 "$program" | grep -q "already as much swap as memory"
test "$(lines)" -eq 1

step "a /swapfile that falls short is made again"
swapoff /swapfile
rm /swapfile
fallocate -l 64M /swapfile
chmod 600 /swapfile
mkswap /swapfile > /dev/null
swapon /swapfile
! enough
python3 "$program"
enough
test "$(lines)" -eq 1
