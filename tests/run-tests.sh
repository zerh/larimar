#!/bin/sh
# Runs all the tests: `larimarc test` on tests/ (see MANUAL, chapter "Tests"), which also covers the editor's
# tools (tests/lsp), https:// (tests/tls) and the debugger (tests/debug); then two checks of their own: how
# larimarc test reports failures, and every std file checked alone.
#
# Usage:
#   tests/run-tests.sh                   all the tests, with the larimarc build-bootstrap.sh made
#   tests/run-tests.sh memory            only the files (and tests) whose path or name contains "memory"
#   LARIMARC=build/larimarc_stage2 tests/run-tests.sh
#
# Environment: CC (default cc), LARIMARC (the compiler to test; the tests that run it as another program,
# like tests/lsp, get it from there too).

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
export LARIMARC CC
FILTER="${1:-}"

if [ ! -x "$LARIMARC" ]; then
    echo "No compiler at $LARIMARC: build it with ./build-bootstrap.sh, or set LARIMARC."
    exit 2
fi

pass=0
fail=0
failed=""

# the files of tests/: larimarc test runs them (and says how each went)
if [ -n "$FILTER" ]; then
    CC="$CC" "$LARIMARC" test tests --only "$FILTER"
else
    CC="$CC" "$LARIMARC" test tests
fi
tests_code=$?
echo ""

# larimarc test itself, on tests that fail on purpose: each failure is reported as what it is
case "runner" in *"$FILTER"*)
    T="$(mktemp -d)"
    mkdir -p "$T/tests"
    cat > "$T/tests/fixture_test.lar" <<'END'
import std.test { check, checkInt, fail, skip, TestSetup };
enum Oops { Bad }
class Broken implements TestSetup {
    function beforeEach(): void { fail("no database"); }
    function afterEach(): void { println("afterEach ran"); }
}
function boom(): void throws Oops { throw Oops.Bad; }
test function passes(): void { checkInt(4, 2 + 2); }
test function fails(): void { checkInt(5, 2 + 2); check(true, "fine"); }
test function panics(): void { let xs: int32[] = [1]; let i: int32 = 5; checkInt(0, xs[i]); }
test function setupFails(b: Broken): void { check(false, "should not run"); }
test function throwsOut(): void throws Oops { boom(); }
test function skips(): void { skip("no such tool"); }
END
    out="$(cd "$T" && CC="$CC" "$LARIMARC" test 2>&1)"
    code=$?
    missing=""
    for want in "ok    tests/fixture_test.lar: passes" "FAIL  tests/fixture_test.lar: fails" \
                "check failed: expected 5 but got 4" "FAIL  tests/fixture_test.lar: panics" "index 5 out of range" \
                "check failed: beforeEach() failed, so the test did not run" "afterEach ran" \
                "check failed: the test threw Oops" "skip  tests/fixture_test.lar: skips (no such tool)" \
                "1 passed, 4 failed, 1 skipped"; do
        printf "%s\n" "$out" | grep -qF -- "$want" || missing="$missing\n  missing: $want"
    done
    printf "%s\n" "$out" | grep -qF "should not run" && missing="$missing\n  a test ran after its setup failed"
    [ $code -eq 1 ] || missing="$missing\n  exit $code (expected 1)"
    rm -rf "$T"
    if [ -z "$missing" ]; then
        pass=$((pass + 1))
        echo "  ok    runner (larimarc test reports each kind of failure)"
    else
        fail=$((fail + 1))
        failed="$failed runner"
        echo "  FAIL  runner"
        printf "%b\n%s\n" "$missing" "$out" | sed "s/^/        /"
    fi
    ;;
esac

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

echo ""
echo "the rest: $pass passed, $fail failed"
[ $fail -eq 0 ] || echo "failed:$failed"
[ $fail -eq 0 ] && [ $tests_code -eq 0 ] || exit 1
