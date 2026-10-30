#!/bin/sh
# Runs the tests in tests/<group>/*.lar. Each file says in its first lines what it expects:
#
#   // expect: run               it compiles and runs cleanly (AddressSanitizer, UBSan), exit 0
#   // output: some text         the output it must print (one line each, in order, all of them)
#   // expect: error some text   the compiler rejects it, and the message contains "some text"
#   // expect: panic some text   it compiles but stops at run time (exit 101) with "some text"
#   // expect: memory-error      it compiles, and the sanitizers report a memory error when it runs
#   // c-has: name               the generated C must contain this identifier (any number of lines)
#   // c-lacks: name             the generated C must not contain it (what is not used must not reach the C)
#
# tests/lsp/lsp_test.py checks larimar check and larimar lsp, tests/tls/tls_test.py https:// with the system's
# TLS, and tests/debug/debug_test.py larimar --debug with lldb or gdb (with python3, when there is one).
#
# Usage:
#   tests/run-tests.sh                   all the tests, with the larimarc build-bootstrap.sh made
#   tests/run-tests.sh memory            only the files whose path contains "memory"
#   LARIMARC=build/larimarc_stage2 tests/run-tests.sh
#
# Environment: CC (default cc), LARIMARC (the compiler to test).

cd "$(dirname "$0")/.." || exit 2
ROOT="$(pwd)"
export LARIMAR_HOME="$ROOT"
if [ -z "${LARIMARC:-}" ]; then              # where build-bootstrap.sh leaves it
    for c in "$ROOT/../out/larimar/bin/larimarc" "$ROOT/bin/larimarc" "$ROOT/larimarc"; do
        if [ -x "$c" ] || [ -x "$c.exe" ]; then LARIMARC="$c"; break; fi
    done
fi
LARIMARC="${LARIMARC:-$ROOT/larimarc}"
CC="${CC:-cc}"
FILTER="${1:-}"
CFLAGS="-std=c99 -g -O1 -fno-omit-frame-pointer -fsanitize=address,undefined -fno-sanitize-recover=undefined"
export ASAN_OPTIONS="detect_leaks=0"
export UBSAN_OPTIONS="print_stacktrace=1"

if [ ! -x "$LARIMARC" ]; then
    echo "No compiler at $LARIMARC: build it with ./build-bootstrap.sh, or set LARIMARC."
    exit 2
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
pass=0
fail=0
failed=""

libs() {     # libs <file.c>: what larimar build would add for std.net's TLS
    case "$(uname -s)" in
        Darwin) grep -q "#define LM_NET_TLS\b" "$1" && echo "-framework Network -framework Security" ;;
        MINGW*|MSYS*|CYGWIN*) grep -q "#define LM_NET_TLS\b" "$1" && echo "-lsecur32 -lws2_32" ;;
        *) grep -q "#define LM_NET_TLS" "$1" && echo "-ldl" ;;
    esac
}

header() {   # header <file> <key>: the text after "// <key>:" on its first such line
    sed -n "s#^// $2: \{0,1\}##p" "$1" | head -n 1
}

for t in tests/*/*.lar; do
    case "$t" in *"$FILTER"*) ;; *) continue ;; esac
    case "$t" in tests/tls/*) continue ;; esac          # the client of tests/tls/tls_test.py
    expect="$(header "$t" expect)"
    kind="${expect%% *}"
    want="${expect#* }"
    [ "$want" = "$expect" ] && want=""
    name="${t#tests/}"
    rm -rf "$TMP"/*                                     # also p.dSYM (macOS: a folder)
    "$LARIMARC" "$t" -o "$TMP/p.c" > "$TMP/compile.txt" 2>&1
    compiled=$?
    problem=""
    case "$kind" in
        error)
            if [ $compiled -eq 0 ]; then
                problem="expected a compile error containing: $want"
            elif ! grep -qF -- "$want" "$TMP/compile.txt"; then
                problem="the error does not contain: $want
$(cat "$TMP/compile.txt")"
            fi
            ;;
        run|panic|memory-error)
            if [ $compiled -ne 0 ]; then
                problem="did not compile:
$(cat "$TMP/compile.txt")"
            elif missing="$(sed -n 's#^// c-has: *##p' "$t" | while read -r n; do grep -qw -- "$n" "$TMP/p.c" || echo "$n"; done)"; [ -n "$missing" ]; then
                problem="the generated C should contain: $missing"
            elif extra="$(sed -n 's#^// c-lacks: *##p' "$t" | while read -r n; do grep -qw -- "$n" "$TMP/p.c" && echo "$n"; done)"; [ -n "$extra" ]; then
                problem="the generated C should not contain: $extra"
            elif ! $CC $CFLAGS "$TMP/p.c" -o "$TMP/p" -pthread -lm $(libs "$TMP/p.c") > "$TMP/cc.txt" 2>&1; then
                problem="the C compiler failed:
$(head -20 "$TMP/cc.txt")"
            else
                "$TMP/p" > "$TMP/out.txt" 2> "$TMP/err.txt"
                code=$?
                if [ "$kind" = memory-error ]; then
                    grep -qE "ERROR: AddressSanitizer|runtime error:" "$TMP/err.txt" || problem="expected the sanitizers to report a memory error (exit $code)"
                elif grep -qE "ERROR: AddressSanitizer|runtime error:" "$TMP/err.txt"; then
                    problem="memory error at run time:
$(grep -E "ERROR|SUMMARY|runtime error|#[0-3] " "$TMP/err.txt" | head -12)"
                elif [ "$kind" = run ] && [ $code -ne 0 ]; then
                    problem="exit $code:
$(head -10 "$TMP/err.txt")"
                elif [ "$kind" = panic ] && { [ $code -ne 101 ] || ! grep -qF -- "$want" "$TMP/err.txt"; }; then
                    problem="expected a panic containing: $want (exit $code)
$(head -5 "$TMP/err.txt")"
                elif grep -q "^// output:" "$t"; then
                    sed -n 's#^// output: \{0,1\}##p' "$t" > "$TMP/want.txt"
                    if ! diff "$TMP/want.txt" "$TMP/out.txt" > "$TMP/diff.txt"; then
                        problem="wrong output (< expected, > got):
$(head -20 "$TMP/diff.txt")"
                    fi
                fi
            fi
            ;;
        *)
            problem="no '// expect:' line (run, error or panic)"
            ;;
    esac
    if [ -z "$problem" ]; then
        pass=$((pass + 1))
        echo "  ok    $name"
    else
        fail=$((fail + 1))
        failed="$failed $name"
        echo "  FAIL  $name"
        printf "%s\n" "$problem" | sed "s/^/        /"
    fi
done

# every file of std, opened alone (as the editor does), has no errors
case "std-check" in *"$FILTER"*)
    bad=""
    for f in $(find std -name '*.lar' | sort); do
        out="$("$LARIMARC" check "$f" 2>&1)"
        [ "$out" = "no errors" ] || bad="$bad\n$f: $out"
    done
    if [ -z "$bad" ]; then
        pass=$((pass + 1))
        echo "  ok    std-check (every std file, opened alone)"
    else
        fail=$((fail + 1))
        failed="$failed std-check"
        echo "  FAIL  std-check"
        printf "%b\n" "$bad" | sed "s/^/        /"
    fi
    ;;
esac

# the editor's tools (larimar check, larimar lsp), when Python is there
case "lsp" in *"$FILTER"*)
    if command -v python3 > /dev/null 2>&1; then
        if python3 tests/lsp/lsp_test.py "$LARIMARC"; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
            failed="$failed lsp"
        fi
    else
        echo "  skip  lsp (no python3)"
    fi
    ;;
esac

# https:// with the system's TLS, against a local HTTPS server (when Python is there)
case "tls" in *"$FILTER"*)
    if command -v python3 > /dev/null 2>&1; then
        if python3 tests/tls/tls_test.py "$LARIMARC" "$CC"; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
            failed="$failed tls"
        fi
    else
        echo "  skip  tls (no python3)"
    fi
    ;;
esac

# the debugger: larimar --debug, lldb or gdb, and Larimar's formatters (when Python and a debugger are there)
case "debug" in *"$FILTER"*)
    if command -v python3 > /dev/null 2>&1; then
        if python3 tests/debug/debug_test.py "$LARIMARC" "$CC"; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
            failed="$failed debug"
        fi
    fi
    ;;
esac

echo ""
echo "$pass passed, $fail failed"
[ $fail -eq 0 ] || { echo "failed:$failed"; exit 1; }
