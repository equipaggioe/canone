#!/bin/sh
# ADR-0078: the receiver asks the server of a product for its backup, and keeps it in <folder>.
# Then it forgets what passed its retention and checks its copy, with the password of the
# repository in <password file>: the server only adds.
#
#     ./backup.sh <app> <host> <folder> <password file>
#
# rest-server 0.15.0, from its release on GitHub, restic 0.18.0, ssh and curl are on the PATH.
# From canone: plataformas/despliegue.md.
set -eu
version=0.15.0
case "$(restic version)" in
    "restic 0.18.0 "*) ;;
    *) echo "restic is not 0.18.0" >&2; exit 1 ;;
esac
if ! server=$(command -v rest-server); then
    echo "rest-server is not installed" >&2
    exit 1
fi
case "$("$server" --version)" in
    *" rest-server $version "*) ;;
    *) echo "rest-server is not $version" >&2; exit 1 ;;
esac
# The server adds backups, but cannot delete or rewrite them.
"$server" --path "$3" --listen 127.0.0.1:8001 --append-only --no-auth &
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
repository="$3/$1"
# The server is done, and a backup cut short leaves its lock.
restic --repo "$repository" --password-file "$4" unlock --remove-all
restic --repo "$repository" --password-file "$4" forget --group-by= --keep-within-daily 7d --keep-within-weekly 1m --keep-within-monthly 1y --prune
restic --repo "$repository" --password-file "$4" check --read-data-subset 5%
