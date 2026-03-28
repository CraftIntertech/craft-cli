#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/.local/share/craft-cli"
BIN_LINK="$HOME/.local/bin/craft"
CONFIG_DIR="$HOME/.config/craft"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
printf "${RED}Uninstall craft-cli${NC}\n"
echo ""
echo "This will remove:"
echo "  - $INSTALL_DIR"
echo "  - $BIN_LINK"
echo ""
read -rp "Continue? [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

[ -f "$BIN_LINK" ] && rm -f "$BIN_LINK" && echo "  Removed $BIN_LINK"
[ -d "$INSTALL_DIR" ] && rm -rf "$INSTALL_DIR" && echo "  Removed $INSTALL_DIR"

echo ""
if [ -d "$CONFIG_DIR" ]; then
    read -rp "Also remove config ($CONFIG_DIR)? [y/N] " rm_config
    if [[ "$rm_config" =~ ^[Yy]$ ]]; then
        rm -rf "$CONFIG_DIR"
        echo "  Removed $CONFIG_DIR"
    else
        printf "  ${YELLOW}Config kept at $CONFIG_DIR${NC}\n"
    fi
fi

echo ""
printf "${GREEN}craft-cli uninstalled.${NC}\n"
