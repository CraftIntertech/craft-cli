#!/usr/bin/env bash
set -euo pipefail

APP_NAME="craft"
INSTALL_DIR="$HOME/.local/share/craft-cli"
BIN_DIR="$HOME/.local/bin"
REPO_URL="https://github.com/CraftIntertech/craft-cli.git"
MIN_PYTHON="3.8"

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

# --- Check Python ---
find_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
            if [ -n "$ver" ]; then
                local major minor
                major=$(echo "$ver" | cut -d. -f1)
                minor=$(echo "$ver" | cut -d. -f2)
                if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
                    echo "$cmd"
                    return 0
                fi
            fi
        fi
    done
    return 1
}

PYTHON=$(find_python) || fail "Python >= $MIN_PYTHON is required. Please install Python first."
info "Using $PYTHON ($($PYTHON --version 2>&1))"

# --- Check pip ---
if ! $PYTHON -m pip --version &>/dev/null; then
    fail "pip is not installed. Run: $PYTHON -m ensurepip --upgrade"
fi

# --- Check git ---
if ! command -v git &>/dev/null; then
    fail "git is required. Install it with: sudo apt install git"
fi

# --- Clone or update ---
BRANCH="main"
if [ -d "$INSTALL_DIR" ]; then
    info "Updating existing installation..."
    git -C "$INSTALL_DIR" fetch origin "$BRANCH" 2>/dev/null && \
    git -C "$INSTALL_DIR" reset --hard "origin/$BRANCH" 2>/dev/null || \
    (warn "Update failed, re-cloning..." && rm -rf "$INSTALL_DIR" && git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR")
else
    info "Downloading craft-cli..."
    git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi
ok "Source ready at $INSTALL_DIR"

# --- Create venv ---
VENV_DIR="$INSTALL_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
fi
ok "Virtual environment ready"

# --- Install ---
info "Installing dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -e "$INSTALL_DIR" -q
ok "craft-cli installed"

# --- Create bin symlink ---
mkdir -p "$BIN_DIR"
WRAPPER="$BIN_DIR/craft"
cat > "$WRAPPER" <<SCRIPT
#!/usr/bin/env bash
exec "$VENV_DIR/bin/craft" "\$@"
SCRIPT
chmod +x "$WRAPPER"
ok "Created $WRAPPER"

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

# --- Read version ---
VERSION=$(cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo "unknown")

# --- Done ---
echo ""
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "${GREEN}  craft-cli v${VERSION} installed!${NC}\n"
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
echo ""
echo "  Get started:"
echo ""
printf "    ${CYAN}craft --help${NC}              # See all commands\n"
printf "    ${CYAN}craft login <token>${NC}      # Authenticate\n"
printf "    ${CYAN}craft vm list${NC}             # List your VMs\n"
echo ""
echo "  Manage:"
echo ""
printf "    ${CYAN}craft version${NC}             # Check version & updates\n"
printf "    ${CYAN}craft update${NC}              # Update to latest\n"
printf "    ${CYAN}craft uninstall${NC}           # Remove craft-cli\n"
echo ""
