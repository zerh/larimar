#!/bin/sh
# Installs Larimar on macOS or Linux:
#
#   curl -fsSL https://zerh.github.io/larimar/install.sh | sh
#
# It downloads the release for this system from GitHub, checks its SHA-256, puts it in ~/.larimar (no sudo)
# and adds ~/.larimar/bin to the PATH of your shell. Plugins already in ~/.larimar/plugins are kept.
#
#   LARIMAR_VERSION=v1.0.0   a given version (default: the latest)
#   LARIMAR_INSTALL=folder   another folder (default: ~/.larimar)
set -eu

REPO="zerh/larimar"
DIR="${LARIMAR_INSTALL:-$HOME/.larimar}"
VERSION="${LARIMAR_VERSION:-latest}"

say() { printf '%s\n' "$*"; }
fail() { printf 'larimar install: %s\n' "$*" >&2; exit 1; }

case "$(uname -s)" in
    Darwin) os=macos ;;
    Linux) os=linux ;;
    *) fail "this script is for macOS and Linux; on Windows: powershell -c \"irm https://zerh.github.io/larimar/install.ps1 | iex\"" ;;
esac
case "$(uname -m)" in
    x86_64 | amd64) arch=x86_64 ;;
    arm64 | aarch64) arch=arm64 ;;
    *) fail "there is no release for this processor ($(uname -m)); build it from the source: https://github.com/$REPO" ;;
esac

asset="larimar-$os-$arch.tar.gz"
if [ "$VERSION" = latest ]; then
    base="https://github.com/$REPO/releases/latest/download"
else
    base="https://github.com/$REPO/releases/download/$VERSION"
fi
command -v curl > /dev/null || fail "curl is needed"
command -v tar > /dev/null || fail "tar is needed"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

say "Downloading $asset ($VERSION)..."
curl -fsSL "$base/$asset" -o "$tmp/$asset" || fail "could not download $base/$asset"

# the release lists the SHA-256 of each file
if curl -fsSL "$base/SHA256SUMS" -o "$tmp/SHA256SUMS" 2> /dev/null; then
    expected=$(awk -v f="$asset" '$2 == f || $2 == "*" f { print $1 }' "$tmp/SHA256SUMS")
    if command -v sha256sum > /dev/null; then
        actual=$(sha256sum "$tmp/$asset" | awk '{ print $1 }')
    else
        actual=$(shasum -a 256 "$tmp/$asset" | awk '{ print $1 }')
    fi
    [ -n "$expected" ] && [ "$expected" = "$actual" ] || fail "the download does not match its SHA-256; nothing was installed"
else
    say "(this release has no SHA256SUMS: the download is not checked)"
fi

tar -xzf "$tmp/$asset" -C "$tmp"
[ -x "$tmp/larimar/bin/larimar" ] || fail "the archive has no larimar/bin/larimar"

# a new version replaces the old one; the plugins stay
if [ -d "$DIR/plugins" ]; then mv "$DIR/plugins" "$tmp/plugins.kept"; fi
rm -rf "$DIR"
mkdir -p "$(dirname "$DIR")"
mv "$tmp/larimar" "$DIR"
if [ -d "$tmp/plugins.kept" ]; then mv "$tmp/plugins.kept" "$DIR/plugins"; fi
if [ "$os" = macos ]; then xattr -dr com.apple.quarantine "$DIR" 2> /dev/null || true; fi

say "Installed in $DIR: $("$DIR/bin/larimar" --version 2> /dev/null || echo larimar)"

# the PATH, in the file each shell reads when it starts
case ":$PATH:" in
    *":$DIR/bin:"*) ;;
    *)
        line="export PATH=\"$DIR/bin:\$PATH\""
        case "$(basename "${SHELL:-sh}")" in
            zsh) rc="$HOME/.zshrc" ;;
            bash) if [ "$os" = macos ]; then rc="$HOME/.bash_profile"; else rc="$HOME/.bashrc"; fi ;;
            fish) rc="$HOME/.config/fish/config.fish"; line="fish_add_path \"$DIR/bin\"" ;;
            *) rc="$HOME/.profile" ;;
        esac
        if ! grep -qsF "$DIR/bin" "$rc"; then
            mkdir -p "$(dirname "$rc")"
            printf '\n# Larimar\n%s\n' "$line" >> "$rc"
            say "Added to $rc: $line"
        fi
        say "Open a new terminal, or run now: $line"
        ;;
esac

# Larimar writes C: building programs needs a C compiler
if [ "$os" = macos ]; then
    if ! xcode-select -p > /dev/null 2>&1; then
        say ""
        say "To build programs, macOS needs Apple's Command Line Tools (a C compiler). Run once:"
        say "    xcode-select --install"
    fi
elif ! command -v cc > /dev/null && ! command -v gcc > /dev/null && ! command -v clang > /dev/null; then
    id=""
    if [ -r /etc/os-release ]; then id=$(. /etc/os-release; echo "${ID:-} ${ID_LIKE:-}"); fi
    case "$id" in
        *debian* | *ubuntu*) cmd="sudo apt install build-essential" ;;
        *fedora* | *rhel* | *centos*) cmd="sudo dnf install gcc" ;;
        *arch*) cmd="sudo pacman -S base-devel" ;;
        *alpine*) cmd="sudo apk add build-base" ;;
        *suse*) cmd="sudo zypper install gcc" ;;
        *) cmd="the gcc or clang package of your system" ;;
    esac
    say ""
    say "To build programs, Larimar needs a C compiler. Install one with:"
    say "    $cmd"
fi
