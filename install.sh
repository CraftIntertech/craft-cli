#!/usr/bin/env bash
set -euo pipefail

APP_NAME="craft"
BIN_DIR="$HOME/.local/bin"
REPO="CraftIntertech/craft-cli"
REPO_URL="https://github.com/$REPO.git"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { printf "${CYAN}[*]${NC} %s\n" "$1"; }
ok()    { printf "${GREEN}[✓]${NC} %s\n" "$1"; }
warn()  { printf "${YELLOW}[!]${NC} %s\n" "$1"; }
fail()  { printf "${RED}[✗]${NC} %s\n" "$1"; exit 1; }

# --- Detect platform ---
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$OS" in
    linux)  OS="linux" ;;
    darwin) OS="darwin" ;;
    *)      fail "Unsupported OS: $OS" ;;
esac

case "$ARCH" in
    x86_64|amd64)   ARCH="amd64" ;;
    aarch64|arm64)   ARCH="arm64" ;;
    *)               fail "Unsupported architecture: $ARCH" ;;
esac

BINARY="craft-${OS}-${ARCH}"
info "Detected platform: ${OS}/${ARCH}"

# --- Check tools ---
if ! command -v curl &>/dev/null; then
    fail "curl is required. Install: sudo apt install curl"
fi

# --- Get version ---
info "Checking latest version..."
VERSION=$(curl -fsSL "https://raw.githubusercontent.com/$REPO/main/VERSION" 2>/dev/null || echo "")
if [ -z "$VERSION" ]; then
    fail "Could not determine latest version"
fi
info "Latest version: v${VERSION}"

# --- Prepare ---
mkdir -p "$BIN_DIR"
TARGET="$BIN_DIR/$APP_NAME"
INSTALLED=false

# --- Try 1: Download pre-built binary from GitHub Release ---
DOWNLOAD_URL="https://github.com/$REPO/releases/download/v${VERSION}/${BINARY}"
info "Trying to download pre-built binary..."
if curl -fsSL "$DOWNLOAD_URL" -o "$TARGET" 2>/dev/null; then
    chmod +x "$TARGET"
    ok "Downloaded pre-built binary"
    INSTALLED=true
else
    warn "No pre-built binary available (release not published yet)"
fi

# --- Try 2: Build from source ---
if [ "$INSTALLED" = false ]; then
    if ! command -v go &>/dev/null; then
        if ! command -v git &>/dev/null; then
            fail "No pre-built binary available and neither Go nor git is installed.\nInstall Go from https://go.dev/dl/ or wait for a release at https://github.com/$REPO/releases"
        fi
        fail "No pre-built binary available. Install Go to build from source: https://go.dev/dl/"
    fi

    if ! command -v git &>/dev/null; then
        fail "git is required to build from source. Install: sudo apt install git"
    fi

    info "Building from source (requires Go)..."
    TMPDIR=$(mktemp -d)
    trap "rm -rf $TMPDIR" EXIT

    git clone -q --depth 1 "$REPO_URL" "$TMPDIR/craft-cli"
    info "Compiling..."
    cd "$TMPDIR/craft-cli"
    go build -ldflags "-s -w -X github.com/$REPO/cmd.Version=${VERSION}" -o "$TARGET" .
    chmod +x "$TARGET"
    ok "Built from source"
    INSTALLED=true
fi

if [ "$INSTALLED" = false ]; then
    fail "Installation failed"
fi

# --- Verify binary works ---
if ! "$TARGET" version &>/dev/null; then
    fail "Binary installed but does not execute. Check your platform."
fi

# --- Remove old Python installation if present ---
OLD_INSTALL="$HOME/.local/share/craft-cli"
if [ -d "$OLD_INSTALL/.venv" ]; then
    warn "Found old Python installation at $OLD_INSTALL"
    printf "  Remove it? [y/N] "
    read -r REPLY
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        rm -rf "$OLD_INSTALL"
        ok "Removed old Python installation"
    fi
fi

# --- Check PATH ---
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    warn "$BIN_DIR is not in your PATH"
    echo ""
    echo "  Add to ~/.bashrc or ~/.zshrc:"
    echo ""
    printf "    ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}\n"
    echo ""
    printf "  Then: ${CYAN}source ~/.bashrc${NC}\n"
    echo ""
fi

# --- Done ---
echo ""
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "${GREEN}  craft-cli v${VERSION} installed!${NC}\n"
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
echo ""
echo "  No Python required — single binary!"
echo ""
printf "    ${CYAN}craft --help${NC}              # See all commands\n"
printf "    ${CYAN}craft login <token>${NC}      # Authenticate\n"
printf "    ${CYAN}craft vm list${NC}             # List your VMs\n"
echo ""
printf "    ${CYAN}craft update${NC}              # Update to latest\n"
echo ""
