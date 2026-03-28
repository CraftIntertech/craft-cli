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

# --- Check required tools ---
command -v git &>/dev/null || fail "git is required. Install: sudo apt install git"
command -v go  &>/dev/null || fail "Go is required. Install from https://go.dev/dl/"

# --- Detect platform ---
info "Detected platform: $(uname -s)/$(uname -m)"

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
go build -ldflags "-s -w -X github.com/$REPO/cmd.Version=${VERSION}" -o "$TARGET" .
chmod +x "$TARGET"
ok "Built craft binary"

# --- Verify ---
"$TARGET" version &>/dev/null || fail "Binary does not run. Check your Go installation."

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
