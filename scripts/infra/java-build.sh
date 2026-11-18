#!/bin/sh
# Builds a piece in Java with plantilla/scripts/java.py and the JDK of the PATH, the one of the CI,
# and runs it with the JRE of Debian 13: the jar runs with java -jar and finds its dependency in
# lib/; a dependency whose SHA-256 is another fails before it is written; a build replaces the one
# before it, also its dependencies; code without the format of google-java-format, until --format
# gives it, or with a warning fails; and an output that would delete the piece fails.
#
#     sh java-build.sh <canone>
set -eu
java_py=$1/plantilla/scripts/java.py
# The java of the unit, not the one of the PATH.
jre=/usr/bin/java
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
step() { printf '\n== %s\n' "$*"; }
fails() { if "$@" 2> "$work/error"; then exit 1; fi; }
cd "$work"
mkdir -p hello/src
cat > hello/src/Hello.java << 'EOF'
public class Hello {
  public static void main(String[] args) {
    System.out.println(org.slf4j.LoggerFactory.class.getSimpleName());
  }
}
EOF
good=0818930dc8d7debb403204611691da58e49d42c50b6ffcfdce02dadb7c3c2b6c
api="org.slf4j:slf4j-api:2.0.9 $good"

step "The jar runs on the JRE of Debian 13 and finds its dependency in lib/"
echo "$api" > hello/dependencies.txt
python3 "$java_py" hello Hello out
test "$("$jre" -jar out/hello/hello.jar)" = LoggerFactory

step "A dependency with another SHA-256 fails and is not written"
echo "org.slf4j:slf4j-api:2.0.9 $(echo "$good" | tr 0 1)" > hello/dependencies.txt
fails python3 "$java_py" hello Hello bad
grep -qF "slf4j-api-2.0.9.jar has the SHA-256" "$work/error"
test ! -e bad/hello/lib/slf4j-api-2.0.9.jar
test ! -e bad/hello/hello.jar

step "A build replaces the one before it, also its dependencies"
cat > hello/src/Hello.java << 'EOF'
public class Hello {
  public static void main(String[] args) {
    System.out.println("Hello");
  }
}
EOF
: > hello/dependencies.txt
python3 "$java_py" hello Hello out
test "$("$jre" -jar out/hello/hello.jar)" = Hello
test -z "$(ls -A out/hello/lib)"

step "Code without the format of google-java-format fails, until --format gives it"
cat > hello/src/Hello.java << 'EOF'
public class Hello {
    public static void main(String[] args) { System.out.println("Hello"); }
}
EOF
fails python3 "$java_py" hello Hello out
grep -qF "java.py --format" "$work/error"
python3 "$java_py" --format hello
python3 "$java_py" hello Hello out

step "A warning fails the build"
cat > hello/src/Hello.java << 'EOF'
import java.util.ArrayList;
import java.util.List;

public class Hello {
  @SuppressWarnings("rawtypes")
  static List names = new ArrayList();

  public static void main(String[] args) {
    names.add("Hello");
  }
}
EOF
fails python3 "$java_py" hello Hello out
grep -qF "[unchecked]" "$work/error"

step "An output that would delete the piece fails, and the piece stays"
fails python3 "$java_py" hello Hello .
grep -qF "would delete the piece itself" "$work/error"
test -f hello/src/Hello.java
