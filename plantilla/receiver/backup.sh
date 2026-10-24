#!/bin/sh
# ADR-0078: the receiver asks the server of a product for its backup, and keeps it in <folder>.
#
#     ./backup.sh <app> <host> <folder>
#
# rest-server, ssh and curl are on the PATH. From canone: plataformas/despliegue.md.
set -eu
# The server adds backups, but cannot delete or rewrite them.
rest-server --path "$3" --listen 127.0.0.1:8001 --append-only --no-auth &
rest=$!
trap 'kill "$rest"' EXIT
tries=50
until curl --silent --output /dev/null http://127.0.0.1:8001/; do
    tries=$((tries - 1))
    if [ "$tries" -eq 0 ] || ! kill -0 "$rest" 2>/dev/null; then
        echo "rest-server does not listen on 127.0.0.1:8001" >&2
        exit 1
    fi
    sleep 0.2
done
# Without the tunnel, ssh ends instead of asking for the backup.
ssh -T -o ExitOnForwardFailure=yes -R 127.0.0.1:8001:127.0.0.1:8001 "$1-receiver@$2"
