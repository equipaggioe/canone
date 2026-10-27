#!/bin/sh
# Loads the ruleset in a server namespace and probes it from a client namespace.
#
#     sh nftables.sh <ruleset>
set -eu
here=$(dirname "$0")
listener=
cleanup() {
    status=$?
    if [ -n "$listener" ]; then kill "$listener" 2>/dev/null || true; fi
    ip netns del server 2>/dev/null || true
    ip netns del client 2>/dev/null || true
    exit "$status"
}
trap cleanup EXIT
ip netns add server
ip netns add client
ip link add server type veth peer name client
ip link set server netns server
ip link set client netns client
ip -n server addr add 10.9.0.1/24 dev server
ip -n client addr add 10.9.0.2/24 dev client
ip -n server link set server up
ip -n client link set client up
ip netns exec server nft -f "$1"
ip netns exec server python3 "$here/network.py" listen &
listener=$!
sleep 1
ip netns exec client python3 "$here/network.py" probe 10.9.0.1
ip netns exec server python3 "$here/network.py" out 10.9.0.2
