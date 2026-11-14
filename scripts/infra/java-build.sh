#!/bin/sh
# Builds a piece in Java with plantilla/scripts/java.py and the JDK of Debian 13: the jar runs
# with java -jar and finds its dependency in lib/, and a dependency whose SHA-256 is another fails
# before it is written.
#
#     sh java-build.sh <canone>
set -eu
java_py=$1/plantilla/scripts/java.py
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
step() { printf '\n== %s\n' "$*"; }
mkdir -p "$work/hello/src"
cat > "$work/hello/src/Hello.java" << 'EOF'
public class Hello {
    public static void main(String[] args) {
        System.out.println(org.slf4j.LoggerFactory.class.getSimpleName());
    }
}
EOF
good=0818930dc8d7debb403204611691da58e49d42c50b6ffcfdce02dadb7c3c2b6c

step "The jar runs and finds its dependency in lib/"
echo "org.slf4j:slf4j-api:2.0.9 $good" > "$work/hello/dependencies.txt"
python3 "$java_py" "$work/hello" Hello "$work/out"
test "$(java -jar "$work/out/hello/hello.jar")" = LoggerFactory

step "A dependency with another SHA-256 fails and is not written"
echo "org.slf4j:slf4j-api:2.0.9 $(echo "$good" | tr 0 1)" > "$work/hello/dependencies.txt"
if python3 "$java_py" "$work/hello" Hello "$work/bad" 2> "$work/error"; then exit 1; fi
grep -qF "slf4j-api-2.0.9.jar has the SHA-256" "$work/error"
test ! -e "$work/bad/hello/lib/slf4j-api-2.0.9.jar"
test ! -e "$work/bad/hello/hello.jar"
