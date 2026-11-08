#!/bin/sh
# Build the Larimar compiler from the C bootstrap and install it.
#
# Everything is edited here, in larimar-compiler/. The installation folder
# (../out/larimar by default) is a build result: this script fills it with
#
#   bin/larimarc    the compiler
#   bin/larimar     wrapper that sets LARIMAR_HOME
#   std/            copy of std/
#   doc/            the manuals and the specification
#   debug/          lldb and gdb formatters (from tools/debuggers) (larimar build --debug, VS Code)
#
# Requirements: a C99 compiler (cc, gcc, clang, tcc...).
#
# Usage:
#   ./bootstrap/build.sh                  # build ./larimarc and install it
#   ./bootstrap/build.sh --verify         # also check that it compiles itself
#   ./bootstrap/build.sh --no-install     # only build ./larimarc
#   ./bootstrap/build.sh --verify --test  # also run tests/run-tests.sh (needs AddressSanitizer)
#
# Environment:
#   CC              C compiler (default: cc)
#   CFLAGS          flags (default: -std=c99 -O2)
#   LARIMAR_PREFIX  installation folder (default: ../out/larimar)

set -e
cd "$(dirname "$0")/.."                 # the repository, whatever folder this is run from
HERE="$(pwd)"

CC="${CC:-cc}"
CFLAGS="${CFLAGS:--std=c99 -O2}"
PREFIX="${LARIMAR_PREFIX:-../out/larimar}"
OUTPUT="bin/larimarc"

VERIFY=0
INSTALL=1
TEST=0
for arg in "$@"; do
    case "$arg" in
        --verify) VERIFY=1 ;;
        --no-install) INSTALL=0 ;;
        --test) TEST=1 ;;
        *) echo "Unknown option: $arg"; exit 1 ;;
    esac
done

for f in bootstrap/larimarc.c std/lang.lar doc/manual.md bin/larimar; do
    if [ ! -e "$f" ]; then
        echo "ERROR: $f not found in $HERE"
        exit 1
    fi
done

# The compiler reads the standard library from LARIMAR_HOME/std:
# while building, that is this folder.
export LARIMAR_HOME="$HERE"

echo "=== Building the Larimar compiler ==="
echo "C compiler: $CC $CFLAGS"
echo ""
echo "Step 1: compiling bootstrap/larimarc.c ($(wc -l < bootstrap/larimarc.c | tr -d ' ') lines)..."
$CC $CFLAGS bootstrap/larimarc.c -o "$OUTPUT"
echo "  -> ./$OUTPUT"

if [ "$VERIFY" = 1 ]; then
    echo ""
    echo "Step 2: checking that the compiler compiles itself..."
    mkdir -p build
    # stage 1: src/ compiled by the bootstrap compiler (it may be older than src/)
    ./"$OUTPUT" src/main.lar -o build/stage1.c
    $CC $CFLAGS build/stage1.c -o build/larimarc_stage1
    # stage 2 and 3: src/ compiled by the compiler of src/ itself; they must be identical
    ./build/larimarc_stage1 src/main.lar -o build/stage2.c
    $CC $CFLAGS build/stage2.c -o build/larimarc_stage2
    ./build/larimarc_stage2 src/main.lar -o build/stage3.c
    if cmp -s build/stage2.c build/stage3.c; then
        echo "  OK: the compiler compiles itself (stage 2 and stage 3 are identical)"
    else
        echo "  ERROR: stage 2 and stage 3 differ"
        diff build/stage2.c build/stage3.c | head -20
        exit 1
    fi
    if cmp -s bootstrap/larimarc.c build/stage2.c; then
        echo "  OK: bootstrap/larimarc.c is up to date with src/"
    else
        echo "  NOTE: bootstrap/larimarc.c is older than src/; installing the compiler built from src/."
        echo "        To update it: cp build/stage2.c bootstrap/larimarc.c"
        rm -f "$OUTPUT"; cp build/larimarc_stage2 "$OUTPUT"     # a new file: macOS kills a signed binary changed in place
    fi
fi

if [ "$TEST" = 1 ]; then
    echo ""
    echo "Tests:"
    LARIMARC="$HERE/$OUTPUT" CC="$CC" sh tests/run-tests.sh || exit 1
fi

if [ "$INSTALL" = 1 ]; then
    echo ""
    echo "Step 3: installing into $PREFIX..."
    mkdir -p "$PREFIX/bin"
    
    # Comprobación de seguridad para evitar que cp falle si origen y destino coinciden exactamente
    if [ "$(cd bin && pwd -P)/larimarc" != "$(cd "$PREFIX/bin" 2>/dev/null && pwd -P || echo "")/larimarc" ]; then
        rm -f "$PREFIX/bin/larimarc"; cp "$OUTPUT" "$PREFIX/bin/larimarc"     # a new file (macOS: Killed: 9 otherwise)
    else
        echo "  (Source and destination are identical, skipping larimarc copy)"
    fi
    
    cp bin/larimar "$PREFIX/bin/larimar"
    chmod +x "$PREFIX/bin/larimarc" "$PREFIX/bin/larimar"
    rm -rf "$PREFIX/std"
    cp -R std "$PREFIX/std"
    rm -rf "$PREFIX/doc" "$PREFIX/MANUAL.md"
    cp -R doc "$PREFIX/doc"
    rm -rf "$PREFIX/debug"
    cp -R tools/debuggers "$PREFIX/debug"
    PREFIX_ABS="$(cd "$PREFIX" && pwd)"
    echo "  -> $PREFIX_ABS"
    echo ""
    echo "Use it with:"
    echo "  export LARIMAR_HOME=\"$PREFIX_ABS\""
    echo "  export PATH=\"\$LARIMAR_HOME/bin:\$PATH\""
fi

echo ""
echo "=== Done ==="