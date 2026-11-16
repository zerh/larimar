#!/bin/sh
# Builds and runs the two programs of threads against processes, and prints their tables.
#   sh bench/concurrency/run.sh            (from the repository, with the compiler built)
set -e
here=$(cd "$(dirname "$0")" && pwd)
out=${TMPDIR:-/tmp}/larimar-bench
mkdir -p "$out"
for name in bench data; do
    ./bin/larimarc "$here/$name.lar" -o "$out/$name.c"
    libs="-lm -lpthread"
    [ "$(uname)" = "Linux" ] && libs="$libs -lrt"
    cc -std=c99 -O2 -w "$out/$name.c" -o "$out/$name" $libs
done
echo "$(uname -sm), $(getconf _NPROCESSORS_ONLN 2>/dev/null || sysctl -n hw.ncpu) cores"
echo
"$out/bench"
echo
"$out/data"
