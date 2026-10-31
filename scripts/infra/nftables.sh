#!/bin/sh
# Loads the ruleset in a server namespace and probes it from a client namespace, also from a source
# that is never valid. With the rules of TURN, it puts them where the ruleset includes them, as
# install.py --turn does, and probes them from Teredo and 6to4.
#
#     sh nftables.sh <ruleset> [<turn rules>]
set -eu
here=$(dirname "$0")
listener=
cleanup() {
    status=$?
    if [ -n "$listener" ]; then kill "$listener" 2>/dev/null || true; fi
    ip netns del server 2>/dev/null || true
    ip netns del client 2>/dev/null || true
    rm -f /etc/nftables.d/turn.nft
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
ip -n server addr add 169.254.9.1/16 dev server
ip -n client addr add 169.254.9.2/16 dev client
# fd09::/64 stands for the internet, and the other two for Teredo and 6to4.
for network in fd09 2001:0:102:302 2002:102:302; do
    ip -n server addr add "$network::1/64" dev server nodad
    ip -n client addr add "$network::2/64" dev client nodad
done
ip -n server link set server up
ip -n client link set client up
if [ $# -gt 1 ]; then
    mkdir -p /etc/nftables.d
    cp "$2" /etc/nftables.d/turn.nft
fi
ip netns exec server nft -f "$1"
ip netns exec server python3 "$here/network.py" listen &
listener=$!
sleep 1
ip netns exec client python3 "$here/network.py" probe 10.9.0.1 ${2:+turn}
ip netns exec client python3 "$here/network.py" invalid 10.9.0.1 169.254.9.2
if [ $# -gt 1 ]; then
    ip netns exec client python3 "$here/network.py" tunneled fd09::1 fd09::2
fi
ip netns exec server python3 "$here/network.py" out 10.9.0.2
