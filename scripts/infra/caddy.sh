#!/bin/sh
# Runs the Caddyfile and the sites of plantilla/infra in Caddy, with a server on 8000 that counts
# what reaches it: each host serves its piece with the headers, /api/* carries them too and is not
# cached, a body over its limit gets 413, by its Content-Length or cut by request_body, and never
# reaches the server whole, and /downloads/ serves the installers. Caddy signs its own certificates.
#
#     sh caddy.sh <canone>
set -eu
canone=$1
work=$(mktemp -d)
pids=
cleanup() {
    status=$?
    for pid in $pids; do kill "$pid" 2>/dev/null || true; done
    rm -rf "$work"
    exit "$status"
}
trap cleanup EXIT
step() { printf '\n== %s\n' "$*"; }
# The placeholders take values like those install.py writes.
mkdir -p "$work/caddy/sites"
printf '{\n\tlocal_certs\n\tskip_install_trust\n}\n' | cat - "$canone/plantilla/infra/Caddyfile" > "$work/caddy/Caddyfile"
for site in "$canone"/plantilla/infra/PRODUCTO-*.caddy; do
    sed -e s/PRODUCTO/app/g -e s/DOMINIO/example.com/g -e "s/PERMISOS/camera=(), geolocation=(self)/g" \
        "$site" > "$work/caddy/sites/$(basename "$site")"
done
for piece in web panel landing; do
    mkdir -p "/srv/app/current/$piece"
    echo "$piece" > "/srv/app/current/$piece/index.html"
done
mkdir -p /srv/app/downloads
echo installer > /srv/app/downloads/desktop-linux.bin
# The server answers 200 with the size of the body it read, and logs each request.
cat > "$work/server.py" <<'EOF'
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def body(self) -> int:
        if self.headers.get("Transfer-Encoding") == "chunked":
            size = 0
            while chunk := int(self.rfile.readline().split(b";")[0], 16):
                size += len(self.rfile.read(chunk))
                self.rfile.readline()
            self.rfile.readline()
            return size
        return len(self.rfile.read(int(self.headers.get("Content-Length", 0))))

    def answer(self) -> None:
        size = self.body()
        print(self.command, self.path, size, file=sys.stderr, flush=True)
        text = str(size).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(text)))
        self.end_headers()
        self.wfile.write(text)

    do_GET = do_POST = answer

    def log_message(self, *args: object) -> None:
        pass


HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
EOF
python3 "$work/server.py" 2> "$work/server.log" &
pids="$pids $!"
caddy run --config "$work/caddy/Caddyfile" > "$work/caddy.log" 2>&1 &
pids="$pids $!"
https() {
    host=$1
    shift
    curl -sk --resolve "$host:443:127.0.0.1" --resolve "$host:80:127.0.0.1" "$@"
}
i=0
until https app.example.com -o /dev/null https://app.example.com/; do
    i=$((i + 1))
    if [ "$i" -ge 50 ]; then cat "$work/caddy.log"; exit 1; fi
    sleep 0.2
done
status() { https app.example.com -o /dev/null -w '%{http_code}' "$@"; }
reached() { grep -c -- "$1" "$work/server.log" || true; }
headers() {
    grep -qix 'strict-transport-security: max-age=63072000; includeSubDomains; preload' "$1"
    grep -qix 'x-content-type-options: nosniff' "$1"
    grep -qix 'x-frame-options: DENY' "$1"
    grep -qix "content-security-policy: frame-ancestors 'none'" "$1"
    grep -qix 'referrer-policy: strict-origin-when-cross-origin' "$1"
    grep -qix 'cross-origin-opener-policy: same-origin' "$1"
    grep -qix 'cross-origin-resource-policy: same-site' "$1"
    grep -qix 'permissions-policy: camera=(), geolocation=(self)' "$1"
    if grep -qi '^server:' "$1"; then exit 1; fi
    if grep -qi '^cross-origin-embedder-policy:' "$1"; then exit 1; fi
}

step "Each host serves its piece, with the headers"
for pair in example.com:landing app.example.com:web panel.example.com:panel; do
    host=${pair%%:*}
    https "$host" -D "$work/headers" -o "$work/body" "https://$host/"
    test "$(cat "$work/body")" = "${pair#*:}"
    tr -d '\r' < "$work/headers" > "$work/clean"
    headers "$work/clean"
done

step "HTTP goes to HTTPS"
test "$(https app.example.com -o /dev/null -w '%{http_code} %{redirect_url}' http://app.example.com/)" = "308 https://app.example.com/"

step "/api/* reaches the server with the headers, and is not cached nor indexed"
https app.example.com -D "$work/headers" -o /dev/null https://app.example.com/api/ping
tr -d '\r' < "$work/headers" > "$work/clean"
headers "$work/clean"
grep -qix 'cache-control: no-store' "$work/clean"
grep -qix 'x-robots-tag: noindex, nofollow' "$work/clean"
test "$(reached 'GET /api/ping')" = 1

step "A body up to its limit reaches the server: 1 MB, and 10 MB in multipart"
head -c 1000000 /dev/zero > "$work/1mb"
head -c 9999000 /dev/zero > "$work/10mb"
test "$(status -H 'Content-Type: application/json' --data-binary @"$work/1mb" https://app.example.com/api/small)" = 200
test "$(reached 'POST /api/small 1000000')" = 1
test "$(status -F file=@"$work/10mb" https://app.example.com/api/upload)" = 200
test "$(reached 'POST /api/upload')" = 1

step "Over the limit, 413 by its Content-Length, and nothing reaches the server"
head -c 1000001 /dev/zero > "$work/1mb+"
head -c 10000001 /dev/zero > "$work/10mb+"
test "$(status -H 'Content-Type: application/json' --data-binary @"$work/1mb+" https://app.example.com/api/big)" = 413
test "$(status -F file=@"$work/10mb+" https://app.example.com/api/huge)" = 413
test "$(reached /api/big)" = 0
test "$(reached /api/huge)" = 0

step "Over the limit without a Content-Length, request_body cuts it with 413"
test "$(status --http1.1 -H 'Content-Type: application/json' -H 'Transfer-Encoding: chunked' --data-binary @"$work/1mb+" https://app.example.com/api/chunked)" = 413
if grep -q 'POST /api/chunked 1000001' "$work/server.log"; then exit 1; fi

step "/downloads/ serves the installers"
test "$(https app.example.com https://app.example.com/downloads/desktop-linux.bin)" = installer
