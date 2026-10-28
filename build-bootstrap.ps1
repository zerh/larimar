<#
.SYNOPSIS
    Build the Larimar compiler from the C bootstrap and install it on Windows.
#>

[CmdletBinding()]
param(
    [switch]$Verify,
    [switch]$NoInstall,
    [switch]$Test
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

$CC = if ($env:CC) { $env:CC } else { "gcc" }
$CFLAGS = if ($env:CFLAGS) { $env:CFLAGS } else { "-std=c99 -O2" }
$PREFIX = if ($env:LARIMAR_PREFIX) { $env:LARIMAR_PREFIX } else { "../out/larimar" }
$Output = "bin/larimarc.exe"

# Asegurar que exista el directorio bin
if (!(Test-Path "bin")) {
    New-Item -ItemType Directory -Path "bin" | Out-Null
}

$requiredFiles = @("larimarc_bootstrap.c", "std/lang.lar", "MANUAL.md", "bin/larimar")
foreach ($f in $requiredFiles) {
    if (!(Test-Path $f)) {
        Write-Error "ERROR: $f not found in $ScriptDir"
        exit 1
    }
}

$env:LARIMAR_HOME = $ScriptDir

Write-Host "=== Building the Larimar compiler ==="
Write-Host "C compiler: $CC $CFLAGS"
Write-Host ""

$lines = (Get-Content "larimarc_bootstrap.c" | Measure-Object -Line).Lines
Write-Host "Step 1: compiling larimarc_bootstrap.c ($lines lines)..."

& $CC $CFLAGS larimarc_bootstrap.c -o $Output
Write-Host "  -> ./$Output"

if ($Verify) {
    Write-Host ""
    Write-Host "Step 2: checking that the compiler compiles itself..."
    if (!(Test-Path "build")) {
        New-Item -ItemType Directory -Path "build" | Out-Null
    }

    & $Output "src/main.lar" -o "build/stage1.c"
    & $CC $CFLAGS "build/stage1.c" -o "build/larimarc_stage1.exe"

    & "build/larimarc_stage1.exe" "src/main.lar" -o "build/stage2.c"
    & $CC $CFLAGS "build/stage2.c" -o "build/larimarc_stage2.exe"

    & "build/larimarc_stage2.exe" "src/main.lar" -o "build/stage3.c"

    $stage2Bytes = Get-FileHash "build/stage2.c" -Algorithm SHA256
    $stage3Bytes = Get-FileHash "build/stage3.c" -Algorithm SHA256

    if ($stage2Bytes.Hash -eq $stage3Bytes.Hash) {
        Write-Host "  OK: the compiler compiles itself (stage 2 and stage 3 are identical)"
    } else {
        Write-Error "  ERROR: stage 2 and stage 3 differ"
        exit 1
    }

    $bootstrapBytes = Get-FileHash "larimarc_bootstrap.c" -Algorithm SHA256
    if ($bootstrapBytes.Hash -eq $stage2Bytes.Hash) {
        Write-Host "  OK: larimarc_bootstrap.c is up to date with src/"
    } else {
        Write-Host "  NOTE: larimarc_bootstrap.c is older than src/; installing the compiler built from src/."
        Copy-Item "build/larimarc_stage2.exe" $Output -Force
    }
}

if ($Test) {
    Write-Host ""
    Write-Host "Tests:"
    $env:LARIMARC = Join-Path $ScriptDir $Output
    $env:CC = $CC
    & sh "tests/run-tests.sh"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if (-not $NoInstall) {
    Write-Host ""
    Write-Host "Step 3: installing into $PREFIX..."
    $binDir = Join-Path $PREFIX "bin"
    $stdDir = Join-Path $PREFIX "std"
    $debugDir = Join-Path $PREFIX "debug"

    if (!(Test-Path $binDir)) { New-Item -ItemType Directory -Path $binDir -Force | Out-Null }

    $sourcePath = (Resolve-Path $Output).Path
    $resolvedBinDir = (New-Item -ItemType Directory -Path $binDir -Force).FullName
    $destPath = Join-Path $resolvedBinDir "larimarc.exe"

    if ($sourcePath -ne $destPath) {
        Copy-Item $Output "$binDir/larimarc.exe" -Force
    } else {
        Write-Host "  (Source and destination are identical, skipping larimarc copy)"
    }

    if (Test-Path "bin/larimar") {
        Copy-Item "bin/larimar" "$binDir/larimar" -Force
    }

    if (Test-Path $stdDir) { Remove-Item $stdDir -Recurse -Force }
    Copy-Item "std" $stdDir -Recurse -Force

    Copy-Item "MANUAL.md" "$PREFIX/MANUAL.md" -Force

    if (Test-Path $debugDir) { Remove-Item $debugDir -Recurse -Force }
    if (Test-Path "debug") { Copy-Item "debug" $debugDir -Recurse -Force }

    $PrefixAbs = (Resolve-Path $PREFIX).Path
    Write-Host "  -> $PrefixAbs"
    Write-Host ""
    Write-Host "Use it with:"
    Write-Host "  `$env:LARIMAR_HOME = `"$PrefixAbs`""
    Write-Host "  `$env:PATH = `"`$env:LARIMAR_HOME\bin;`$env:PATH`""
}

Write-Host ""
Write-Host "=== Done ==="