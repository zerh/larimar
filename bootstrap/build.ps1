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
$ScriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition)   # the repository
Set-Location $ScriptDir

$CC = if ($env:CC) { $env:CC } else { "gcc" }
$CFLAGS = if ($env:CFLAGS) { $env:CFLAGS.Split(" ") } else { @("-std=c99", "-O2") }
$PREFIX = if ($env:LARIMAR_PREFIX) { $env:LARIMAR_PREFIX } else { "../out/larimar" }
$Output = "bin/larimarc.exe"

# Asegurar que exista el directorio bin
if (!(Test-Path "bin")) {
    New-Item -ItemType Directory -Path "bin" | Out-Null
}

# Validación adaptada para incluir larimar.cmd en lugar del script bash
$requiredFiles = @("bootstrap/larimarc.c", "std/lang.lar", "docs/manual.md", "bin/larimar.cmd")
foreach ($f in $requiredFiles) {
    if (!(Test-Path $f)) {
        Write-Error "ERROR: $f not found in $ScriptDir"
        exit 1
    }
}

$env:LARIMAR_HOME = $ScriptDir

Write-Host "=== Building the Larimar compiler ==="
Write-Host "C compiler: $CC $($CFLAGS -join ' ')"
Write-Host ""

$lines = (Get-Content "bootstrap/larimarc.c" | Measure-Object -Line).Lines
Write-Host "Step 1: compiling bootstrap/larimarc.c ($lines lines)..."

& $CC @CFLAGS bootstrap/larimarc.c -o $Output
Write-Host "  -> ./$Output"

if ($Verify) {
    Write-Host ""
    Write-Host "Step 2: checking that the compiler compiles itself..."
    if (!(Test-Path "build")) {
        New-Item -ItemType Directory -Path "build" | Out-Null
    }

    $stage1Exe = Join-Path $ScriptDir "build\larimarc_stage1.exe"
    $stage2Exe = Join-Path $ScriptDir "build\larimarc_stage2.exe"

    # Generar stage1.c
    & $Output "src/main.lar" -o "build/stage1.c"
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to generate stage1.c"; exit $LASTEXITCODE }

    # Compilar stage1.exe
    & $CC @CFLAGS "build/stage1.c" -o $stage1Exe
    if ($LASTEXITCODE -ne 0) { Write-Error "GCC failed compiling stage1.c"; exit $LASTEXITCODE }

    # Ejecutar stage1
    & $stage1Exe "src/main.lar" -o "build/stage2.c"
    if ($LASTEXITCODE -ne 0) { Write-Error "stage1.exe failed generating stage2.c"; exit $LASTEXITCODE }

    # Compilar stage2.exe
    & $CC @CFLAGS "build/stage2.c" -o $stage2Exe
    if ($LASTEXITCODE -ne 0) { Write-Error "GCC failed compiling stage2.c"; exit $LASTEXITCODE }

    # Ejecutar stage2
    & $stage2Exe "src/main.lar" -o "build/stage3.c"
    if ($LASTEXITCODE -ne 0) { Write-Error "stage2.exe failed generating stage3.c"; exit $LASTEXITCODE }

    $stage2Bytes = Get-FileHash "build/stage2.c" -Algorithm SHA256
    $stage3Bytes = Get-FileHash "build/stage3.c" -Algorithm SHA256

    if ($stage2Bytes.Hash -eq $stage3Bytes.Hash) {
        Write-Host "  OK: the compiler compiles itself (stage 2 and stage 3 are identical)"
    } else {
        Write-Error "  ERROR: stage 2 and stage 3 differ"
        exit 1
    }

    $bootstrapBytes = Get-FileHash "bootstrap/larimarc.c" -Algorithm SHA256
    if ($bootstrapBytes.Hash -eq $stage2Bytes.Hash) {
        Write-Host "  OK: bootstrap/larimarc.c is up to date with src/"
    } else {
        Write-Host "  NOTE: bootstrap/larimarc.c is older than src/; installing the compiler built from src/."
        Copy-Item $stage2Exe $Output -Force
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

    # Copiar el wrapper larimar.cmd a la carpeta de binarios destino
    if (Test-Path "bin/larimar.cmd") {
        Copy-Item "bin/larimar.cmd" "$binDir/larimar.cmd" -Force
    }

    if (Test-Path $stdDir) { Remove-Item $stdDir -Recurse -Force }
    Copy-Item "std" $stdDir -Recurse -Force

    $docDir = Join-Path $PREFIX "doc"
    if (Test-Path $docDir) { Remove-Item $docDir -Recurse -Force }
    if (Test-Path "$PREFIX/MANUAL.md") { Remove-Item "$PREFIX/MANUAL.md" -Force }
    New-Item -ItemType Directory -Force -Path $docDir | Out-Null
    Copy-Item "docs/*.md" $docDir -Force

    if (Test-Path $debugDir) { Remove-Item $debugDir -Recurse -Force }
    if (Test-Path "tools/debuggers") { Copy-Item "tools/debuggers" $debugDir -Recurse -Force }

    $PrefixAbs = (Resolve-Path $PREFIX).Path
    Write-Host "  -> $PrefixAbs"
    Write-Host ""
    Write-Host "Use it with:"
    Write-Host "  `$env:LARIMAR_HOME = `"$PrefixAbs`""
    Write-Host "  `$env:PATH = `"`$env:LARIMAR_HOME\bin;`$env:PATH`""
}

Write-Host ""
Write-Host "=== Done ==="