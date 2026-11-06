# Builds the tcc that comes with Larimar on Windows into <larimar>\toolchain\tcc (GitHub Actions runs it
# after build-bootstrap.ps1, with MinGW's gcc in the Path). tcc brings its own headers and uses the C
# library of Windows (msvcrt.dll): programs it builds need nothing else.
#
#   .\tools\build-tcc.ps1 ..\out\larimar
#
# Larimar uses it for `larimar file.lar` (it starts fast) and when the system has no C compiler. Programs
# that use TLS need another compiler (the SChannel headers are not in tcc's).
param([Parameter(Mandatory = $true)][string]$Larimar)
$ErrorActionPreference = 'Stop'

$commit = '2d3eea205cb6c0f796d01d7d0858eb6c6c1d993f'     # github.com/TinyCC/tinycc (mob), tested with Larimar
$dest = Join-Path (Resolve-Path $Larimar).Path 'toolchain\tcc'
$work = Join-Path ([IO.Path]::GetTempPath()) ('tinycc-' + [guid]::NewGuid())

function Run([string]$what, [scriptblock]$command) {
    & $command
    if ($LASTEXITCODE -ne 0) { throw "$what failed (exit $LASTEXITCODE)" }
}

Run 'git init' { git init -q $work }
Run 'git fetch' { git -C $work fetch -q --depth 1 https://github.com/TinyCC/tinycc $commit }
Run 'git checkout' { git -C $work checkout -q FETCH_HEAD }

if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Push-Location (Join-Path $work 'win32')
try {
    Run 'build-tcc.bat' { cmd /c "build-tcc.bat -c gcc -t x86_64 -i $dest" }
} finally {
    Pop-Location
}
if (-not (Test-Path (Join-Path $dest 'tcc.exe'))) { throw "build-tcc.bat did not put tcc.exe in $dest" }

# what the runtime uses of Windows newer than tcc's .def files (Vista: condition variables, slim locks)
$lib = Join-Path $dest 'lib'
$kernel32 = Join-Path $lib 'kernel32.def'
$lines = [System.Collections.Generic.List[string]]::new()
foreach ($line in Get-Content $kernel32) { $lines.Add($line.TrimEnd()) }
foreach ($name in 'AcquireSRWLockExclusive', 'ReleaseSRWLockExclusive', 'InitializeConditionVariable',
                  'SleepConditionVariableCS', 'WakeAllConditionVariable', 'WakeConditionVariable', 'GetTickCount64') {
    if (-not $lines.Contains($name)) { $lines.Add($name) }
}
Set-Content $kernel32 $lines -Encoding ascii
Set-Content (Join-Path $lib 'advapi32.def') @('LIBRARY advapi32.dll', '', 'EXPORTS', 'SystemFunction036') -Encoding ascii

Copy-Item (Join-Path $work 'COPYING') (Join-Path $dest 'COPYING-tcc')
Set-Content (Join-Path $dest 'README.txt') @(
    "tcc (Tiny C Compiler, LGPL 2.1: COPYING-tcc), commit $commit of https://github.com/TinyCC/tinycc.",
    "Larimar uses it for 'larimar file.lar' and when the system has no C compiler. Its source: the link above."
) -Encoding ascii
Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue

# it works: a program with threads (the Vista functions above) and the C library
$check = Join-Path ([IO.Path]::GetTempPath()) ('tcc-check-' + [guid]::NewGuid())
New-Item -ItemType Directory $check | Out-Null
Set-Content (Join-Path $check 'check.c') @(
    '#include <stdio.h>',
    '#include <windows.h>',
    'typedef struct { void* Ptr; } SRW;',
    '__declspec(dllimport) void __stdcall AcquireSRWLockExclusive(SRW* l);',
    '__declspec(dllimport) void __stdcall ReleaseSRWLockExclusive(SRW* l);',
    '__declspec(dllimport) unsigned long long __stdcall GetTickCount64(void);',
    'int main(void) { SRW l = {0}; AcquireSRWLockExclusive(&l); ReleaseSRWLockExclusive(&l); printf("ok %d\n", GetTickCount64() > 0); return 0; }'
) -Encoding ascii
Run 'the bundled tcc' { & (Join-Path $dest 'tcc.exe') (Join-Path $check 'check.c') -o (Join-Path $check 'check.exe') -ladvapi32 }
$out = & (Join-Path $check 'check.exe')
if ($out -ne 'ok 1') { throw "the bundled tcc does not work: $out" }
Remove-Item $check -Recurse -Force
Write-Host "tcc in $dest"
