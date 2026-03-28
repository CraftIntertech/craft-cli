#!/usr/bin/env bash
set -euo pipefail

APP_NAME="craft"
BIN_DIR="$HOME/.local/bin"
REPO="CraftIntertech/craft-cli"
API_URL="https://api.github.com/repos/$REPO/releases/latest"

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
    *)      fail "Unsupported OS: $OS. Download manually from https://github.com/$REPO/releases" ;;
esac

case "$ARCH" in
    x86_64|amd64)   ARCH="amd64" ;;
    aarch64|arm64)   ARCH="arm64" ;;
    *)               fail "Unsupported architecture: $ARCH" ;;
esac

BINARY="craft-${OS}-${ARCH}"
info "Detected platform: ${OS}/${ARCH}"

# --- Check for curl ---
if ! command -v curl &>/dev/null; then
    fail "curl is required. Install it with: sudo apt install curl"
fi

# --- Get latest release version ---
info "Checking latest version..."
VERSION=$(curl -fsSL "$API_URL" 2>/dev/null | grep '"tag_name"' | head -1 | sed 's/.*"tag_name": *"v\?\([^"]*\)".*/\1/')

if [ -z "$VERSION" ]; then
    # Fallback: use VERSION from repo
    VERSION=$(curl -fsSL "https://raw.githubusercontent.com/$REPO/main/VERSION" 2>/dev/null || echo "")
    if [ -z "$VERSION" ]; then
        fail "Could not determine latest version"
    fi
fi

DOWNLOAD_URL="https://github.com/$REPO/releases/download/v${VERSION}/${BINARY}"
info "Latest version: v${VERSION}"

# --- Download binary ---
mkdir -p "$BIN_DIR"
TARGET="$BIN_DIR/$APP_NAME"

info "Downloading ${BINARY}..."
if curl -fsSL "$DOWNLOAD_URL" -o "$TARGET" 2>/dev/null; then
    chmod +x "$TARGET"
    ok "Downloaded craft binary"
else
    # Release not yet available, fall back to building from source
    warn "Release binary not found, building from source..."

    if ! command -v go &>/dev/null; then
        fail "Go is required to build from source. Install from https://go.dev/dl/ or download binary from https://github.com/$REPO/releases"
    fi

    TMPDIR=$(mktemp -d)
    trap "rm -rf $TMPDIR" EXIT
    info "Cloning repository..."
    git clone -q --depth 1 "https://github.com/$REPO.git" "$TMPDIR/craft-cli"
    info "Building..."
    cd "$TMPDIR/craft-cli"
    go build -ldflags "-s -w -X github.com/$REPO/cmd.Version=${VERSION}" -o "$TARGET" .
    chmod +x "$TARGET"
    ok "Built from source"
fi

# --- Remove old Python installation if present ---
OLD_INSTALL="$HOME/.local/share/craft-cli"
if [ -d "$OLD_INSTALL/.venv" ]; then
    warn "Found old Python installation at $OLD_INSTALL"
    read -p "  Remove it? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$OLD_INSTALL"
        ok "Removed old Python installation"
    fi
fi

# --- Check PATH ---
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    warn "$BIN_DIR is not in your PATH"
    echo ""
    echo "  Add this line to your ~/.bashrc or ~/.zshrc:"
    echo ""
    printf "    ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}\n"
    echo ""
    echo "  Then reload your shell:"
    echo ""
    printf "    ${CYAN}source ~/.bashrc${NC}\n"
    echo ""
fi

# --- Verify ---
INSTALLED_VERSION=$("$TARGET" version 2>/dev/null | grep -oP '[\d.]+' | head -1 || echo "$VERSION")

# --- Done ---
echo ""
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "${GREEN}  craft-cli v${VERSION} installed!${NC}\n"
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
echo ""
echo "  No Python required — single binary!"
echo ""
echo "  Get started:"
echo ""
printf "    ${CYAN}craft --help${NC}              # See all commands\n"
printf "    ${CYAN}craft login <token>${NC}      # Authenticate\n"
printf "    ${CYAN}craft vm list${NC}             # List your VMs\n"
echo ""
echo "  Manage:"
echo ""
printf "    ${CYAN}craft version${NC}             # Check version\n"
printf "    ${CYAN}craft update${NC}              # Update to latest\n"
echo ""
