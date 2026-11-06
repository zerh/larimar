#!/bin/sh
# Builds the tcc that comes with Larimar on Linux into <larimar>/toolchain/tcc (GitHub Actions runs it
# after build-bootstrap.sh). tcc is configured to use only what is next to it: its headers, and musl's
# headers and static library. Programs it builds are static: they need nothing from the system.
#
#   sudo apt-get install musl-dev
#   tools/build-tcc.sh ../out/larimar
#
# Larimar uses it for `larimar file.lar` (it starts fast) and when the system has no C compiler. Programs
# that use TLS need the system's compiler (std.net.tls loads the system's OpenSSL).
set -eu

TCC_COMMIT=2d3eea205cb6c0f796d01d7d0858eb6c6c1d993f     # github.com/TinyCC/tinycc (mob), tested with Larimar

[ $# -eq 1 ] || { echo "usage: tools/build-tcc.sh <larimar folder>"; exit 2; }
DEST="$(cd "$1" && pwd)/toolchain/tcc"
TRIPLE="$(gcc -dumpmachine | sed 's/-gnu$/-musl/')"     # x86_64-linux-musl, aarch64-linux-musl
MUSL_INC="/usr/include/$TRIPLE"
MUSL_LIB="/usr/lib/$TRIPLE"
[ -f "$MUSL_LIB/libc.a" ] && [ -f "$MUSL_INC/stdio.h" ] || { echo "musl is not in $MUSL_LIB: sudo apt-get install musl-dev"; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
git init -q "$WORK/tinycc"
cd "$WORK/tinycc"
git fetch -q --depth 1 https://github.com/TinyCC/tinycc "$TCC_COMMIT"
git checkout -q FETCH_HEAD

# on 64-bit ARM, musl's wchar_t is unsigned int (tcc says int: their headers would clash)
sed -i 's/^#elif defined __linux__$/#elif defined __linux__ \&\& (defined __aarch64__ || defined __arm__)\n    #define __WCHAR_TYPE__ unsigned int\n    #define __WINT_TYPE__ unsigned int\n#elif defined __linux__/' include/tccdefs.h
grep -q "__WCHAR_TYPE__ unsigned int" include/tccdefs.h || { echo "include/tccdefs.h changed: cannot set wchar_t for ARM"; exit 1; }

# {B} is the folder given with -B (larimar passes toolchain/tcc/lib)
./configure --config-musl \
    --sysincludepaths='{B}/include:{B}/musl/include' \
    --libpaths='{B}:{B}/musl/lib' \
    --crtprefix='{B}/musl/lib' > /dev/null
mkdir -p musl                         # where the new tcc looks while it builds its own library
ln -s "$MUSL_INC" musl/include
ln -s "$MUSL_LIB" musl/lib
make -j"$(nproc)" > /dev/null

rm -rf "$DEST"
mkdir -p "$DEST/lib/musl/lib"
cp tcc "$DEST/tcc"
strip "$DEST/tcc" 2> /dev/null || true
cp libtcc1.a "$DEST/lib/"
cp -r include "$DEST/lib/include"
cp -rL "$MUSL_INC" "$DEST/lib/musl/include"
for f in crt1.o crti.o crtn.o libc.a libm.a libpthread.a libdl.a librt.a libresolv.a libutil.a libxnet.a; do
    if [ -f "$MUSL_LIB/$f" ]; then cp "$MUSL_LIB/$f" "$DEST/lib/musl/lib/"; fi
done
cp COPYING "$DEST/COPYING-tcc"
cp /usr/share/doc/musl-dev/copyright "$DEST/lib/musl/COPYRIGHT"
cat > "$DEST/README.txt" << TEXT
tcc (Tiny C Compiler, LGPL 2.1: COPYING-tcc), commit $TCC_COMMIT of https://github.com/TinyCC/tinycc,
with the headers and the static library of musl (MIT: lib/musl/COPYRIGHT). Larimar uses it for
'larimar file.lar' and when the system has no C compiler. Its source: the link above.
TEXT

# it works: a static program with threads and math
cat > "$WORK/check.c" << 'C'
#include <stdio.h>
#include <math.h>
#include <pthread.h>
static void* run(void* p) { (void)p; return NULL; }
int main(void) { pthread_t t; pthread_create(&t, NULL, run, NULL); pthread_join(t, NULL); printf("%.3f\n", sqrt(2.0)); return 0; }
C
"$DEST/tcc" -B"$DEST/lib" -static "$WORK/check.c" -o "$WORK/check" -pthread -lm
[ "$("$WORK/check")" = "1.414" ] || { echo "the bundled tcc does not work"; exit 1; }
echo "tcc in $DEST"
