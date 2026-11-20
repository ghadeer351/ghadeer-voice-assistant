#!/usr/bin/env bash
set -euo pipefail
read -r -p "Remove the user service, virtual environment and downloaded model? [y/N] " answer
[[ "$answer" =~ ^[Yy]$ ]] || exit 0
systemctl --user disable --now ghadeer-voice-assistant.service 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/ghadeer-voice-assistant.service"
systemctl --user daemon-reload
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rm -rf "$ROOT/.venv" "$ROOT/models"
echo "Removed service, venv and model. Project source files were kept."
