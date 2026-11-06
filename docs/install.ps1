# Installs Larimar on Windows:
#
#   powershell -c "irm https://zerh.github.io/larimar/install.ps1 | iex"
#
# It downloads the release from GitHub, checks its SHA-256, puts it in %USERPROFILE%\.larimar (no
# administrator) and adds its bin folder to your user Path. Plugins already in .larimar\plugins are kept.
#
#   $env:LARIMAR_VERSION = "v1.0.0"   a given version (default: the latest)
#   $env:LARIMAR_INSTALL = "folder"   another folder (default: %USERPROFILE%\.larimar)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'      # Invoke-WebRequest is much faster without its progress bar

$Repo = 'zerh/larimar'
$Dir = if ($env:LARIMAR_INSTALL) { $env:LARIMAR_INSTALL } else { Join-Path $env:USERPROFILE '.larimar' }
$Version = if ($env:LARIMAR_VERSION) { $env:LARIMAR_VERSION } else { 'latest' }

$asset = 'larimar-windows-x86_64.zip'
if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') {
    Write-Host 'There is no Windows ARM64 release yet: installing the x86_64 one (Windows runs it emulated).'
}
$base = if ($Version -eq 'latest') { "https://github.com/$Repo/releases/latest/download" } else { "https://github.com/$Repo/releases/download/$Version" }

$tmp = Join-Path ([IO.Path]::GetTempPath()) ('larimar-' + [guid]::NewGuid())
New-Item -ItemType Directory $tmp | Out-Null
try {
    Write-Host "Downloading $asset ($Version)..."
    Invoke-WebRequest "$base/$asset" -OutFile "$tmp\$asset" -UseBasicParsing

    # the release lists the SHA-256 of each file
    $sums = "$tmp\SHA256SUMS"
    try { Invoke-WebRequest "$base/SHA256SUMS" -OutFile $sums -UseBasicParsing } catch { $sums = $null }
    if ($sums) {
        $expected = ''
        foreach ($line in Get-Content $sums) {
            $parts = $line -split '\s+'
            if ($parts.Length -ge 2 -and $parts[1].TrimStart('*') -eq $asset) { $expected = $parts[0].ToLower() }
        }
        $actual = (Get-FileHash "$tmp\$asset" -Algorithm SHA256).Hash.ToLower()
        if ($expected -ne $actual) { throw 'the download does not match its SHA-256; nothing was installed' }
    } else {
        Write-Host '(this release has no SHA256SUMS: the download is not checked)'
    }

    Expand-Archive "$tmp\$asset" -DestinationPath $tmp -Force
    if (-not (Test-Path "$tmp\larimar\bin\larimarc.exe")) { throw 'the archive has no larimar\bin\larimarc.exe' }

    # a new version replaces the old one; the plugins stay
    if (Test-Path "$Dir\plugins") { Move-Item "$Dir\plugins" "$tmp\plugins.kept" }
    if (Test-Path $Dir) { Remove-Item $Dir -Recurse -Force }
    New-Item -ItemType Directory (Split-Path $Dir) -Force | Out-Null
    Move-Item "$tmp\larimar" $Dir
    if (Test-Path "$tmp\plugins.kept") { Move-Item "$tmp\plugins.kept" "$Dir\plugins" }

    # the user's Path (no administrator needed), and this window's
    $bin = Join-Path $Dir 'bin'
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if (-not $userPath) { $userPath = '' }
    if (-not (($userPath -split ';') -contains $bin)) {
        $newPath = if ($userPath) { $userPath.TrimEnd(';') + ';' + $bin } else { $bin }
        [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        Write-Host "Added to your Path: $bin (new terminals see it)"
    }
    $env:Path = "$bin;$env:Path"
    Write-Host "Installed in ${Dir}: $(& "$bin\larimar.cmd" --version)"

    # Larimar writes C: building programs needs a C compiler
    $cc = @('gcc', 'clang', 'cc') | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
    if (-not $cc) {
        Write-Host ''
        Write-Host 'To build programs, Larimar needs a C compiler. Install one with:'
        Write-Host '    winget install LLVM.LLVM'
    }
} finally {
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
