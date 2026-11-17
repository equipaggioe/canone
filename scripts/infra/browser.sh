#!/bin/sh
# Runs a task of install.py --browser on a Debian 13 with systemd running (ADR-0172): without
# --browser there is no unit; a task named in --task and in --browser, one with a unit of its own,
# and --browser without chromium-headless-shell fail; with --browser the timer runs on its
# calendar and ends a round at its limit; the task drives the Chromium of Debian with Playwright,
# as the server account; without each exception of its filter, or with MemoryDenyWriteExecute=,
# the same task dies; a reinstall without --browser takes the timer, and uninstall.py app the
# unit. uv finds Playwright in UV_CACHE_DIR, filled before the machine lost its network.
#
#     sh browser.sh <canone>
set -eu
canone=$1
install=$canone/plantilla/infra/install.py
unit=$canone/plantilla/infra/PRODUCTO-browser@.service
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" 2> "$work/error"; then exit 1; fi; }
for name in a b s1 s2; do ssh-keygen -q -t ed25519 -N '' -f "$work/$name"; done
key() { cat "$work/$1.pub"; }
run() {
    python3 "$install" demo demo.example 64mb --admin operador --key "$(key a)" --key "$(key b)" \
        --signer "$(key s1)" --signer "$(key s2)" --owner owner "$@"
}
id operador > /dev/null 2>&1 || useradd --create-home --groups sudo operador
service=demo-browser@probe.service
drop_in=/etc/systemd/system/$service.d
# probe: start the task once and print its result. systemd refuses a sixth start in ten seconds,
# and the checks start it more often.
probe() {
    systemctl reset-failed "$service"
    systemctl start "$service" || true
    systemctl show --property=Result --value "$service"
}

step "Without --browser there is no unit"
run
test ! -e /etc/systemd/system/demo-browser@.service

step "A task in --task and in --browser fails, and so does one with its own unit"
fails run --task probe=minutely --browser probe=minutely
grep -qF "goes in one --task or --browser" "$work/error"
fails run --browser purge=daily
grep -qF "purge has its own unit" "$work/error"

step "--browser without chromium-headless-shell fails"
mv /usr/bin/chromium-headless-shell "$work/chromium"
fails run --browser probe=minutely
mv "$work/chromium" /usr/bin/chromium-headless-shell
grep -qF "chromium-headless-shell is not installed" "$work/error"

step "With --browser the timer runs on its calendar, and a round ends at its limit"
run --browser probe=minutely
systemctl is-active --quiet demo-browser@probe.timer
systemctl show --property=TimersCalendar --value demo-browser@probe.timer | grep -qF 'OnCalendar=*-*-* *:*:00 ;'
test "$(systemctl show --property=TimeoutStartUSec --value "$service")" = 1h

step "The task drives the Chromium of Debian with Playwright, as the server account"
# A version whose app.tasks opens a page that runs JavaScript.
server=/srv/demo/releases/v0.0.1/server
mkdir -p "$server/app"
uv venv --quiet --clear --python /usr/bin/python3 "$server/.venv"
uv pip install --quiet --offline --python "$server/.venv" playwright==1.65.1
: > "$server/app/__init__.py"
cat > "$server/app/tasks.py" << 'EOF'
"""A task that drives Chromium: python -m app.tasks probe."""

import asyncio
import getpass

from playwright.async_api import async_playwright

PAGE = "data:text/html,<script>document.title = String(6 * 7)</script>"


async def probe() -> None:
    """Open the page in the Chromium of Debian and write its title."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            executable_path="/usr/bin/chromium-headless-shell"
        )
        page = await browser.new_page()
        await page.goto(PAGE)
        print(f"title {await page.title()} as {getpass.getuser()}")
        await browser.close()


asyncio.run(probe())
EOF
ln -sfn /srv/demo/releases/v0.0.1 /srv/demo/current
test "$(probe)" = success
journalctl --unit="$service" --output=cat | grep -qx 'title 42 as demo'

step "Without each exception of its filter, or with MemoryDenyWriteExecute=, it dies"
mkdir -p "$drop_in"
for call in setpriority pkey_alloc capset; do
    # An empty SystemCallFilter= resets the filter, and the lines of the unit but one come back.
    { echo '[Service]'; echo 'SystemCallFilter='
      grep '^SystemCallFilter=' "$unit" | grep -vx "SystemCallFilter=$call"; } > "$drop_in/test.conf"
    systemctl daemon-reload
    result=$(probe)
    echo "without $call: $result"
    test "$result" != success
done
printf '[Service]\nMemoryDenyWriteExecute=yes\n' > "$drop_in/test.conf"
systemctl daemon-reload
result=$(probe)
echo "with MemoryDenyWriteExecute=: $result"
test "$result" != success
rm -r "$drop_in"
systemctl daemon-reload
test "$(probe)" = success

step "A reinstall without --browser takes the timer, and uninstall.py app the unit"
run
test ! -e /etc/systemd/system/demo-browser@probe.timer.d
test ! -e /etc/systemd/system/demo-browser@.service
test "$(systemctl is-active demo-browser@probe.timer)" != active
run --browser probe=minutely
python3 "$canone/plantilla/infra/uninstall.py" demo app
test ! -e /etc/systemd/system/demo-browser@.service
test ! -e /etc/systemd/system/demo-browser@probe.timer.d
test ! -e /etc/systemd/system/timers.target.wants/demo-browser@probe.timer
