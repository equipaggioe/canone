[app]
title = PRODUCTO
project_dir = src/app
input_file = src/app/main.py
exec_directory = dist
project_file =
icon = src/app/icon.png

[python]
python_path =
packages =

[qt]
qml_files =
excluded_qml_plugins =
modules =
plugins =

[nuitka]
macos.permissions =
mode = onefile
extra_args = --quiet --noinclude-qt-translations --assume-yes-for-downloads
