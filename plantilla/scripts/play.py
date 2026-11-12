# /// script
# requires-python = ">=3.13"
# dependencies = ["google-auth>=2.62.2", "requests>=2.34.2"]
#
# [tool.uv]
# required-version = "==0.13.7"
# ///
"""Upload a bundle to Google Play and download its universal APK.

The service account arrives by stdin:

    uv run scripts/play.py <package> <aab> <apk> < account.json

transversal.md, «Distribución»: Play signs the universal APK with
the key of the store, so both carry the same signature.
"""

import json
import sys
import time
from pathlib import Path

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

SCOPE = "https://www.googleapis.com/auth/androidpublisher"
API = "https://androidpublisher.googleapis.com/androidpublisher/v3/applications"
UPLOAD = "https://androidpublisher.googleapis.com/upload/androidpublisher/v3/applications"
TRACK = "internal"
# How long Play may take to build the APK, and how often to ask.
WAIT_SECONDS = 900
POLL_SECONDS = 15
TIMEOUT_SECONDS = 300


def checked(response):
    """Return response, or stop with what Play answered."""
    if not response.ok:
        raise SystemExit(
            f"{response.request.method} {response.url}: {response.status_code} {response.text}"
        )
    return response


def upload(session: AuthorizedSession, package: str, bundle: Path) -> int:
    """Upload bundle to the internal track; return its version."""
    edit = checked(session.post(f"{API}/{package}/edits", timeout=TIMEOUT_SECONDS)).json()["id"]
    with bundle.open("rb") as data:
        uploaded = session.post(
            f"{UPLOAD}/{package}/edits/{edit}/bundles",
            params={"uploadType": "media"},
            data=data,
            headers={"Content-Type": "application/octet-stream"},
            timeout=TIMEOUT_SECONDS,
        )
    version = checked(uploaded).json()["versionCode"]
    release = {
        "track": TRACK,
        "releases": [{"versionCodes": [str(version)], "status": "completed"}],
    }
    checked(
        session.put(
            f"{API}/{package}/edits/{edit}/tracks/{TRACK}", json=release, timeout=TIMEOUT_SECONDS
        )
    )
    checked(session.post(f"{API}/{package}/edits/{edit}:commit", timeout=TIMEOUT_SECONDS))
    return version


def universal(session: AuthorizedSession, package: str, version: int) -> str:
    """Return the download id of the universal APK, once built."""
    deadline = time.monotonic() + WAIT_SECONDS
    while True:
        listed = checked(
            session.get(f"{API}/{package}/generatedApks/{version}", timeout=TIMEOUT_SECONDS)
        )
        for apks in listed.json().get("generatedApks", []):
            if "generatedUniversalApk" in apks:
                return apks["generatedUniversalApk"]["downloadId"]
        if time.monotonic() > deadline:
            raise SystemExit(
                f"Play built no universal APK of {package} {version} in {WAIT_SECONDS} s"
            )
        time.sleep(POLL_SECONDS)


def download(session: AuthorizedSession, url: str, target: Path) -> None:
    """Write the file at url to target."""
    response = checked(
        session.get(url, params={"alt": "media"}, stream=True, timeout=TIMEOUT_SECONDS)
    )
    with target.open("wb") as out:
        for chunk in response.iter_content(1 << 20):
            out.write(chunk)


def main() -> None:
    package, bundle, target = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    account = service_account.Credentials.from_service_account_info(
        json.load(sys.stdin), scopes=[SCOPE]
    )
    session = AuthorizedSession(account)
    version = upload(session, package, bundle)
    apk = universal(session, package, version)
    download(session, f"{API}/{package}/generatedApks/{version}/downloads/{apk}:download", target)


if __name__ == "__main__":
    main()
