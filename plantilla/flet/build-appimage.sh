#!/usr/bin/env bash
# The Linux AppImage, from the script of Flet's "Packaging app for Linux". Run it after
# "flet build linux", with VERSION set: APP is the artifact of pyproject.toml, and ID, its
# bundle_id, which also names the desktop entry.
set -euo pipefail

BUNDLE=$PWD/build/linux
APP=PIEZA
ID=DOMINIO-INVERSO.PIEZA
OUT=$PWD/build/$APP.AppImage

APPDIR=$PWD/build/$APP.AppDir
ARCH=$(uname -m)
APPIMAGETOOL=$PWD/build/appimagetool-$ARCH.AppImage

# Pinned to a release, not the rolling "continuous" tag.
if [ ! -e "$APPIMAGETOOL" ]; then
  wget -O "$APPIMAGETOOL.part" \
    "https://github.com/AppImage/appimagetool/releases/download/1.9.1/appimagetool-$ARCH.AppImage"
  mv "$APPIMAGETOOL.part" "$APPIMAGETOOL"
fi
chmod +x "$APPIMAGETOOL"

test -d "$BUNDLE/share/applications" || { echo "no desktop entry in $BUNDLE"; exit 1; }

ICON_SRC=$(find "$BUNDLE/share/icons/hicolor" -type f -name "$ID.png" | head -n1)
ICON_SIZE=$(basename "$(dirname "$(dirname "$ICON_SRC")")")

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/$ICON_SIZE/apps"

# The whole bundle: the executable finds its libraries and Python next to itself.
cp -a "$BUNDLE"/. "$APPDIR/usr/bin/"
rm -rf "$APPDIR/usr/bin/share"

cp "$BUNDLE/share/applications/$ID.desktop" "$APPDIR/usr/share/applications/"
cp "$ICON_SRC" "$APPDIR/usr/share/icons/hicolor/$ICON_SIZE/apps/"

sed -i "s|^Exec=.*|Exec=$APP|" "$APPDIR/usr/share/applications/$ID.desktop"

ln -s "usr/share/applications/$ID.desktop" "$APPDIR/$ID.desktop"
ln -s "usr/share/icons/hicolor/$ICON_SIZE/apps/$ID.png" "$APPDIR/$ID.png"
ln -s "usr/share/icons/hicolor/$ICON_SIZE/apps/$ID.png" "$APPDIR/.DirIcon"

# Only exec: LD_LIBRARY_PATH would let system libraries shadow the bundled ones.
printf '#!/bin/sh\nHERE=$(dirname "$(readlink -f "$0")")\nexec "$HERE/usr/bin/%s" "$@"\n' "$APP" > "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"

VERSION=${VERSION:?set VERSION} "$APPIMAGETOOL" --no-appstream "$APPDIR" "$OUT"
