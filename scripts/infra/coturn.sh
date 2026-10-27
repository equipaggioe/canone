#!/bin/sh
# Runs coturn with the config in a turn namespace and relays from an outside namespace: it relays
# to a peer on the internet, and not to a private or loopback one, with another secret, or past
# the quota of a credential.
#
#     sh coturn.sh <turnserver.conf>
set -eu
here=$(dirname "$0")
config=$(mktemp)
pids=
cleanup() {
    status=$?
    for pid in $pids; do kill "$pid" 2>/dev/null || true; done
    ip netns del turn 2>/dev/null || true
    ip netns del outside 2>/dev/null || true
    rm -f "$config"
    exit "$status"
}
trap cleanup EXIT
python3 "$here/peers.py" "$1" "$here/../../fuentes/iana"
ip netns add turn
ip netns add outside
ip link add turn type veth peer name outside
ip link set turn netns turn
ip link set outside netns outside
# 1.2.3.0/24 and 2001:4860::/64 stand for the internet, and 10.9.1.0/24 for a private network.
ip -n turn addr add 1.2.3.1/24 dev turn
ip -n turn addr add 10.9.1.1/24 dev turn
ip -n turn addr add 2001:4860::1/64 dev turn nodad
ip -n outside addr add 1.2.3.2/24 dev outside
ip -n outside addr add 10.9.1.2/24 dev outside
ip -n outside addr add 2001:4860::2/64 dev outside nodad
for namespace in turn outside; do
    ip -n "$namespace" link set lo up
    ip -n "$namespace" link set "$namespace" up
done
sed -e s/SECRETO/secret/ -e s/DOMINIO/example.com/ "$1" > "$config"
ip netns exec turn turnserver -c "$config" --log-file=stdout > /dev/null &
pids="$pids $!"
# One peer outside, and one on the loopback of the machine of coturn.
for namespace in outside turn; do
    ip netns exec "$namespace" turnutils_peer > /dev/null &
    pids="$pids $!"
done
sleep 2
user=0
relays() {
    expected=$1
    shift
    user=$((user + 1))
    if ip netns exec outside timeout 20 turnutils_uclient -u "user$user" -c -n 10 "$@" > /dev/null 2>&1
    then actual=yes
    else actual=no
    fi
    if [ "$actual" != "$expected" ]; then
        echo "turnutils_uclient $*: relays $actual, and should be $expected" >&2
        exit 1
    fi
}
relays yes -W secret -e 1.2.3.2 1.2.3.1
relays yes -W secret -x -e 2001:4860::2 2001:4860::1
relays no -W other -e 1.2.3.2 1.2.3.1
relays no -W secret -e 10.9.1.2 1.2.3.1
relays no -W secret -e 127.0.0.1 1.2.3.1
relays no -W secret -e 0.0.0.0 1.2.3.1
relays no -W secret -x -e ::1 2001:4860::1
relays no -W secret -x -e ::ffff:127.0.0.1 2001:4860::1
# Each client of turnutils_uclient takes two allocations, and a credential holds ten.
relays yes -W secret -m 5 -e 1.2.3.2 1.2.3.1
relays no -W secret -m 6 -e 1.2.3.2 1.2.3.1
