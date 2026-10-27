#!/bin/sh
# Runs coturn with the config behind a one-to-one NAT, as on a machine whose interface has only a
# private address, and relays between two clients outside: without external-ip coturn hands out
# its private address, and the other client cannot reach it; with the line install.py --turn-ip
# writes, it hands out the public one.
#
#     sh coturn-nat.sh <turnserver.conf>
set -eu
here=$(dirname "$0")
config=$(mktemp)
mapped=$(mktemp)
turn=
peer=
cleanup() {
    status=$?
    for pid in $turn $peer; do kill "$pid" 2>/dev/null || true; done
    for namespace in turn nat outside; do ip netns del "$namespace" 2>/dev/null || true; done
    rm -f "$config" "$mapped"
    exit "$status"
}
trap cleanup EXIT
for namespace in turn nat outside; do
    ip netns add "$namespace"
    ip -n "$namespace" link set lo up
done
ip link add turn type veth peer name inside
ip link add public type veth peer name outside
ip link set turn netns turn
ip link set inside netns nat
ip link set public netns nat
ip link set outside netns outside
# 10.20.0.2 is the private address of coturn, and 1.2.3.1 its public one, on the NAT.
ip -n turn addr add 10.20.0.2/24 dev turn
ip -n nat addr add 10.20.0.1/24 dev inside
ip -n nat addr add 1.2.3.1/24 dev public
ip -n outside addr add 1.2.3.2/24 dev outside
ip -n turn link set turn up
ip -n nat link set inside up
ip -n nat link set public up
ip -n outside link set outside up
ip -n turn route add default via 10.20.0.1
ip netns exec nat sysctl -qw net.ipv4.ip_forward=1
ip netns exec nat nft -f - <<'EOF'
table ip nat {
	chain prerouting {
		type nat hook prerouting priority dstnat;
		ip daddr 1.2.3.1 dnat to 10.20.0.2
	}
	chain postrouting {
		type nat hook postrouting priority srcnat;
		ip saddr 10.20.0.0/24 snat to 1.2.3.1
	}
}
EOF
ip netns exec outside turnutils_peer > /dev/null &
peer=$!
user=0
relays() {
    expected=$1
    sed -e s/SECRETO/secret/ -e s/DOMINIO/example.com/ "$2" > "$config"
    ip netns exec turn turnserver -c "$config" --log-file=stdout > /dev/null &
    turn=$!
    sleep 2
    user=$((user + 1))
    if ip netns exec outside timeout 20 \
        turnutils_uclient -u "user$user" -W secret -c -y -n 10 1.2.3.1 > /dev/null 2>&1
    then actual=yes
    else actual=no
    fi
    kill "$turn"
    wait "$turn" 2> /dev/null || true
    turn=
    if [ "$actual" != "$expected" ]; then
        echo "two clients through coturn behind a NAT, $3: relay $actual, and should be $expected" >&2
        exit 1
    fi
}
relays no "$1" "without external-ip"
private=$(ip netns exec turn python3 -c "
import sys
sys.path.insert(0, '$here/../../plantilla/infra')
import install
print(install.private_ip())
")
cat "$1" > "$mapped"
echo "external-ip=1.2.3.1/$private" >> "$mapped"
relays yes "$mapped" "with external-ip=1.2.3.1/$private"
