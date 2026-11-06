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
    # for editors: --list and --json, and --test to run one by its name
    listed="$(cd "$T" && "$LARIMARC" test --list --json 2>&1)"
    printf "%s\n" "$listed" | grep -qF '"event":"found","file":"tests/fixture_test.lar"' || missing="$missing\n  --list --json: no found event"
    printf "%s\n" "$listed" | grep -qF '"name":"skips","line":13' || missing="$missing\n  --list --json: skips is not at line 13"
    one="$(cd "$T" && CC="$CC" "$LARIMARC" test --json --test fails 2>&1)"
    printf "%s\n" "$one" | grep -qF '"name":"fails","line":9,"result":"failed","message":"check failed: expected 5 but got 4"' \
        || missing="$missing\n  --json --test fails: not reported as failed"
    printf "%s\n" "$one" | grep -qF '{"event":"summary","passed":0,"failed":1,"skipped":0}' || missing="$missing\n  --json --test fails: wrong summary"
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

# plugins ($LARIMAR_HOME/plugins/*.toml) and dependencies (deps/<name>/src, [c] of each, a missing one)
case "plugins-deps" in *"$FILTER"*)
    T="$(mktemp -d)"
    mkdir -p "$T/home/bin" "$T/home/plugins" "$T/app/src" "$T/app/deps/sql/src/sql"
    ln -s "$ROOT/std" "$T/home/std"
    printf '#!/bin/sh\necho "minero: $*"\nexit 7\n' > "$T/home/bin/minero"
    chmod +x "$T/home/bin/minero"
    printf '[plugin]\nname = "minero"\nprogram = "minero"\n\n[commands]\nadd = ["add"]\nbuild = ["x"]\n' > "$T/home/plugins/minero.toml"
    printf '[project]\nname = "app"\n\n[dependencies]\nsql = "github.com/zerh/sql@v1.0.0"\n' > "$T/app/larimar.toml"
    printf 'import sql.core;\nfunction main(): int32 { println(core.hello()); return 0; }\n' > "$T/app/src/main.lar"
    printf 'public function hello(): String { return "from deps"; }\n' > "$T/app/deps/sql/src/sql/core.lar"
    printf '[project]\nname = "sql"\n\n[c]\nlibraries = ["m"]\n' > "$T/app/deps/sql/larimar.toml"
    missing=""
    out="$(LARIMAR_HOME="$T/home" "$LARIMARC" add x@1 2>&1)"; code=$?
    printf "%s\n" "$out" | grep -qF "minero: add x@1" || missing="$missing\n  the plugin did not get its arguments: $out"
    printf "%s\n" "$out" | grep -qF "cannot take 'larimar build'" || missing="$missing\n  a plugin took a command of larimar"
    [ $code -eq 7 ] || missing="$missing\n  exit $code (the plugin's is 7)"
    out="$(cd "$T/app" && LARIMAR_HOME="$T/home" CC="$CC" "$LARIMARC" run 2>&1)"
    printf "%s\n" "$out" | grep -qF "from deps" || missing="$missing\n  a module of deps/ was not found: $out"
    mv "$T/app/deps/sql" "$T/app/deps/other"
    out="$(cd "$T/app" && LARIMAR_HOME="$T/home" "$LARIMARC" build 2>&1)"
    printf "%s\n" "$out" | grep -qF "'sql' is in [dependencies] but not in deps/" || missing="$missing\n  no error for a missing dependency: $out"
    rm -rf "$T"
    if [ -z "$missing" ]; then
        pass=$((pass + 1))
        echo "  ok    plugins-deps (plugins answer commands; modules and C of deps/)"
    else
        fail=$((fail + 1))
        failed="$failed plugins-deps"
        echo "  FAIL  plugins-deps"
        printf "%b\n" "$missing" | sed "s/^/        /"
    fi
    ;;
esac

# larimar new makes a project that builds; larimar file.lar runs a file with its arguments and its exit code
case "scripts-new" in *"$FILTER"*)
    T="$(mktemp -d)"
    missing=""
    out="$(cd "$T" && "$LARIMARC" new hello > /dev/null && cd hello && CC="$CC" "$LARIMARC" run 2>&1)"
    printf "%s\n" "$out" | grep -qF "Hello from hello!" || missing="$missing\n  a new project does not run: $out"
    printf 'import std.os;\nfunction main(args: String[]): int32 {\n    println("args: ${args.join(",")}");\n    return 5;\n}\n' > "$T/s.lar"
    out="$(CC="$CC" "$LARIMARC" "$T/s.lar" a b 2>&1)"; code=$?
    [ "$out" = "args: a,b" ] || missing="$missing\n  the script printed: $out"
    [ $code -eq 5 ] || missing="$missing\n  exit $code (the script's is 5)"
    rm -rf "$T"
    if [ -z "$missing" ]; then
        pass=$((pass + 1))
        echo "  ok    scripts-new (larimar new; larimar file.lar with arguments)"
    else
        fail=$((fail + 1))
        failed="$failed scripts-new"
        echo "  FAIL  scripts-new"
        printf "%b\n" "$missing" | sed "s/^/        /"
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
