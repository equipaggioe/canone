#!/bin/sh
# Runs install.py --mail on a Debian 13 with systemd running, with the internet in another
# namespace: Postfix takes from outside, over STARTTLS, only the mail for its host, and hands it to
# the app with its secret; the app hands it email on 127.0.0.1:25, Postfix delivers it unchanged to
# the server of the recipient and sends the app a notice of each result, also when that server
# announces DSN, which it does not without its two options; with the app down it keeps the notice
# and delivers it once the app is back; a second run keeps the secret, and a run without --mail
# closes 25 and takes the program.
#
#     sh mail.sh <canone>
set -eu
here=$(cd "$(dirname "$0")" && pwd)
install=$1/plantilla/infra/install.py
work=$(mktemp -d)
host=mail.demo.example
program=/usr/local/lib/demo/mail
pids=
app=
cleanup() {
    status=$?
    for pid in $pids $app; do kill "$pid" 2>/dev/null || true; done
    ip netns del outside 2>/dev/null || true
    rm -rf "$work"
    exit "$status"
}
trap cleanup EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" 2> "$work/error"; then exit 1; fi; }
# Wait until a file of the folder has the text.
arrives() {
    i=0
    until grep -rqF -- "$2" "$1" 2>/dev/null; do
        i=$((i + 1))
        if [ "$i" -ge 60 ]; then echo "$2 did not arrive in $1"; postqueue -p; exit 1; fi
        sleep 1
    done
}
for name in a b s1 s2; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
run() {
    python3 "$install" demo demo.example 64mb --admin operador \
        --key "$(cat "$work/a.pub")" --key "$(cat "$work/b.pub")" \
        --signer "$(cat "$work/s1.pub")" --signer "$(cat "$work/s2.pub")" --owner owner "$@"
}
secret() { sed -n 's/^SECRET = "\(.*\)"$/\1/p' "$program"; }
serve() {
    python3 "$here/mailserver.py" app "$work/notices" "$(secret)" &
    app=$!
    sleep 1
}
# Send from outside: helo, sender, recipient and message, over STARTTLS.
send() { ip netns exec outside python3 "$here/mailserver.py" send 192.0.2.2 "$@"; }
# An account that already administers: install.py only adds its keys, and asks no password.
id operador > /dev/null 2>&1 || useradd --create-home --groups sudo operador
mkdir "$work/notices" "$work/received"

step "--mail takes a host name"
fails run --mail Mail_Demo
grep -qF 'is not a host name in lowercase' "$work/error"

step "install.py --mail installs Postfix for its host, with the program of the app and its secret"
run --mail "$host"
test "$(postconf -h myhostname)" = "$host"
test "$(postconf -h relay_domains)" = "$host"
test "$(stat -c '%a %U %G' "$program")" = '750 root demo'
test -n "$(secret)"
systemd-creds decrypt --name=app_mail_secret /etc/credstore.encrypted/demo/mail_secret - |
    grep -qxF "$(secret)"
systemctl is-active --quiet postfix.service
test -e /etc/nftables.d/mail.nft

step "A second run keeps the secret"
before=$(secret)
run --mail "$host"
test "$(secret)" = "$before"

step "The internet, at 192.0.2.1, with the server of the recipients"
ip netns add outside
ip -n outside link set lo up
ip link add to-outside type veth peer name outside netns outside
ip addr add 192.0.2.2/24 dev to-outside
ip link set to-outside up
ip -n outside addr add 192.0.2.1/24 dev outside
ip -n outside link set outside up
ip netns exec outside python3 "$here/mailserver.py" mx "$work/received" &
pids="$pids $!"
# The test has no DNS: remote.example goes to that server.
postconf -e "transport_maps = inline:{ $host=notice:, remote.example=smtp:[192.0.2.1]:25 }"
postfix reload
serve

step "From outside, over STARTTLS, the mail for the host reaches the app, with X-Original-To"
send sender@remote.example "rebote+late@$host" 'late bounce'
arrives "$work/notices" "X-Original-To: rebote+late@$host"
arrives "$work/notices" 'late bounce'

step "From outside, the mail for another domain is refused"
fails send sender@remote.example someone@remote.example 'relay'
grep -qF '554' "$work/error"

step "The app hands over on 127.0.0.1:25; Postfix delivers it unchanged and notices relayed"
python3 "$here/mailserver.py" submit "rebote+one@$host" ana@remote.example
arrives "$work/received" 'Contraseña de ejemplo'
arrives "$work/received" 'RCPT TO:<ana@remote.example>'
arrives "$work/notices" "X-Original-To: rebote+one@$host"
arrives "$work/notices" 'Action: relayed'
# The server announced DSN, and Postfix kept the notice of success to itself.
if grep -rqi 'NOTIFY=' "$work/received"; then echo "Postfix passed NOTIFY on"; exit 1; fi

step "A refusal of the server of the recipient goes to the app as a failed notice"
python3 "$here/mailserver.py" submit "rebote+two@$host" nadie@remote.example
arrives "$work/notices" "X-Original-To: rebote+two@$host"
arrives "$work/notices" 'Status: 5.1.1'

step "Without its two options, Postfix passes NOTIFY on, notices nothing and converts the body"
postconf -X smtp_discard_ehlo_keywords disable_mime_output_conversion
postfix reload
rm -f "$work/received/"*
python3 "$here/mailserver.py" submit "rebote+three@$host" ana@remote.example
arrives "$work/received" 'NOTIFY=SUCCESS'
arrives "$work/received" 'Contrase=C3=B1a'
sleep 5
if grep -rqF "rebote+three@$host" "$work/notices"; then echo "a notice arrived"; exit 1; fi
postconf -e smtp_discard_ehlo_keywords=dsn disable_mime_output_conversion=yes
postfix reload

step "With the app down, Postfix keeps the mail, and delivers it once the app is back"
kill "$app"
app=
send sender@remote.example "rebote+later@$host" 'while down'
i=0
until postqueue -j | grep -qF "rebote+later@$host"; do
    i=$((i + 1))
    if [ "$i" -ge 60 ]; then echo "the mail is not in the queue"; exit 1; fi
    sleep 1
done
if grep -rqF 'while down' "$work/notices"; then exit 1; fi
serve
postqueue -f
arrives "$work/notices" 'while down'

step "A run without --mail closes 25 and takes the program"
run
test ! -e /etc/nftables.d/mail.nft
test ! -e "$program"
