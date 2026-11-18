"""Sign the Apple builds on a CI runner and ship them.

    python3 scripts/apple.py keychain                       # CERTIFICATE, CERTIFICATE_PASSWORD
    python3 scripts/apple.py profile                        # PROFILE
    python3 scripts/apple.py dmg <app> <dmg> [--sign-app]   # IDENTITY
    python3 scripts/apple.py upload <ipa>                   # APP_ID

CERTIFICATE is a .p12 and PROFILE a .mobileprovision, both in base64. dmg and upload read the App
Store Connect API key from API_KEY, API_KEY_ID and API_ISSUER.

transversal.md, «Distribución»: the macOS app goes in a DMG signed with Developer ID, notarized and
stapled, and the iOS app reaches App Store Connect signed for the App Store.
"""

import argparse
import base64
import json
import os
import plistlib
import secrets
import subprocess
import sys
from pathlib import Path


# The error names only the tool and its command: the arguments carry passwords.
def run(*args: str) -> str:
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"{args[0]} {args[1]} failed:\n{result.stdout}{result.stderr}")
    return result.stdout


def keychain() -> None:
    temp = Path(os.environ["RUNNER_TEMP"])
    chain = str(temp / "signing.keychain-db")
    password = secrets.token_hex(16)
    p12 = temp / "certificate.p12"
    p12.write_bytes(base64.b64decode(os.environ["CERTIFICATE"]))
    run("security", "create-keychain", "-p", password, chain)
    run("security", "set-keychain-settings", "-lut", "21600", chain)
    run("security", "unlock-keychain", "-p", password, chain)
    exported = os.environ["CERTIFICATE_PASSWORD"]
    run("security", "import", str(p12), "-P", exported, "-A", "-f", "pkcs12", "-k", chain)
    p12.unlink()
    # codesign then uses the key without a prompt, which nobody answers on a runner.
    partitions = "apple-tool:,apple:,codesign:"
    run("security", "set-key-partition-list", "-S", partitions, "-s", "-k", password, chain)
    listed = [line.strip().strip('"') for line in run("security", "list-keychains").splitlines()]
    run("security", "list-keychains", "-d", "user", "-s", chain, *listed)


def profile() -> None:
    temp = Path(os.environ["RUNNER_TEMP"]) / "profile.mobileprovision"
    temp.write_bytes(base64.b64decode(os.environ["PROFILE"]))
    uuid = plistlib.loads(run("security", "cms", "-D", "-i", str(temp)).encode())["UUID"]
    # Xcode finds a profile by its UUID, in this folder.
    folder = Path.home() / "Library/MobileDevice/Provisioning Profiles"
    folder.mkdir(parents=True, exist_ok=True)
    temp.replace(folder / f"{uuid}.mobileprovision")


def api_key() -> Path:
    # altool finds the key by this name, in this folder.
    folder = Path.home() / ".appstoreconnect/private_keys"
    folder.mkdir(parents=True, exist_ok=True)
    key = folder / f"AuthKey_{os.environ['API_KEY_ID']}.p8"
    key.write_text(os.environ["API_KEY"])
    return key


def notarize(path: str) -> None:
    command = ["xcrun", "notarytool", "submit", path, "--key", str(api_key())]
    command += ["--key-id", os.environ["API_KEY_ID"], "--issuer", os.environ["API_ISSUER"]]
    command += ["--wait", "--output-format", "json"]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    # A rejected submission can still exit with 0: its status says so.
    if result.returncode != 0 or json.loads(result.stdout)["status"] != "Accepted":
        sys.exit(f"notarytool did not accept {path}:\n{result.stdout}{result.stderr}")
    run("xcrun", "stapler", "staple", path)


def dmg(app: str, image: str, sign_app: bool) -> None:
    identity = os.environ["IDENTITY"]
    if sign_app:
        signing = ["--force", "--deep", "--options", "runtime", "--timestamp"]
        run("codesign", *signing, "--sign", identity, app)
    volume = Path(app).stem
    run(
        "hdiutil", "create", "-volname", volume, "-srcfolder", app, "-ov", "-format", "UDZO", image
    )
    run("codesign", "--force", "--timestamp", "--sign", identity, image)
    notarize(image)


def upload(ipa: str) -> None:
    api_key()
    credentials = ["--apiKey", os.environ["API_KEY_ID"], "--apiIssuer", os.environ["API_ISSUER"]]
    run(
        "xcrun",
        "altool",
        "--upload-package",
        ipa,
        "-t",
        "ios",
        *credentials,
        "--apple-id",
        os.environ["APP_ID"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("keychain")
    commands.add_parser("profile")
    image = commands.add_parser("dmg")
    image.add_argument("app")
    image.add_argument("dmg")
    image.add_argument("--sign-app", action="store_true")
    commands.add_parser("upload").add_argument("ipa")
    arguments = parser.parse_args()
    if arguments.command == "keychain":
        keychain()
    elif arguments.command == "profile":
        profile()
    elif arguments.command == "dmg":
        dmg(arguments.app, arguments.dmg, arguments.sign_app)
    else:
        upload(arguments.ipa)


if __name__ == "__main__":
    main()
