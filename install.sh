#!/usr/bin/env bash
set -euo pipefail

APP_NAME="craft"
BIN_DIR="$HOME/.local/bin"
REPO="CraftIntertech/craft-cli"
REPO_URL="https://github.com/$REPO.git"
GO_VERSION="1.21.13"

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

# --- Check curl & git ---
command -v curl &>/dev/null || fail "curl is required. Install: sudo apt install curl"
command -v git  &>/dev/null || fail "git is required. Install: sudo apt install git"

# --- Detect platform ---
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$OS" in
    linux)  GO_OS="linux" ;;
    darwin) GO_OS="darwin" ;;
    *)      fail "Unsupported OS: $OS" ;;
esac

case "$ARCH" in
    x86_64|amd64)   GO_ARCH="amd64" ;;
    aarch64|arm64)   GO_ARCH="arm64" ;;
    *)               fail "Unsupported architecture: $ARCH" ;;
esac

info "Detected platform: ${GO_OS}/${GO_ARCH}"

# --- Auto-install Go if not found ---
GO_CMD="go"
if ! command -v go &>/dev/null; then
    info "Go not found — installing Go ${GO_VERSION} automatically..."
    GO_TAR="go${GO_VERSION}.${GO_OS}-${GO_ARCH}.tar.gz"
    GO_URL="https://go.dev/dl/${GO_TAR}"
    GO_INSTALL_DIR="$HOME/.local/go"

    mkdir -p "$HOME/.local"
    curl -fsSL "$GO_URL" -o "/tmp/${GO_TAR}" || fail "Failed to download Go from ${GO_URL}"
    rm -rf "$GO_INSTALL_DIR"
    tar -C "$HOME/.local" -xzf "/tmp/${GO_TAR}" || fail "Failed to extract Go"
    rm -f "/tmp/${GO_TAR}"

    GO_CMD="$GO_INSTALL_DIR/bin/go"
    export PATH="$GO_INSTALL_DIR/bin:$PATH"

    if ! "$GO_CMD" version &>/dev/null; then
        fail "Go installation failed"
    fi
    ok "Go ${GO_VERSION} installed to ${GO_INSTALL_DIR}"
fi

# --- Clone and build ---
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

info "Cloning craft-cli..."
git clone -q --depth 1 "$REPO_URL" "$TMPDIR/craft-cli"

VERSION=$(cat "$TMPDIR/craft-cli/VERSION" 2>/dev/null || echo "dev")
info "Version: v${VERSION}"

info "Building..."
cd "$TMPDIR/craft-cli"
mkdir -p "$BIN_DIR"
TARGET="$BIN_DIR/$APP_NAME"
"$GO_CMD" build -ldflags "-s -w -X github.com/$REPO/cmd.Version=${VERSION}" -o "$TARGET" .
chmod +x "$TARGET"
ok "Built craft binary"

# --- Verify ---
"$TARGET" version &>/dev/null || fail "Binary does not run"

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
    printf "  Add to ~/.bashrc or ~/.zshrc:\n"
    printf "    ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}\n"
    printf "  Then: ${CYAN}source ~/.bashrc${NC}\n"
    echo ""
fi

# --- Done ---
echo ""
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "${GREEN}  craft-cli v${VERSION} installed!${NC}\n"
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
echo ""
printf "    ${CYAN}craft --help${NC}              # See all commands\n"
printf "    ${CYAN}craft login <token>${NC}      # Authenticate\n"
printf "    ${CYAN}craft vm list${NC}             # List your VMs\n"
printf "    ${CYAN}craft update${NC}              # Update to latest\n"
echo ""
