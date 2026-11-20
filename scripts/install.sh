#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Ghadeer Voice Assistant installer"
if ! command -v apt-get >/dev/null 2>&1; then
  echo "This installer currently supports Ubuntu/Debian with apt." >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y python3-venv python3-pip portaudio19-dev espeak-ng alsa-utils curl unzip

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

MODEL_DIR="$ROOT/models/vosk-model-ar-mgb2-0.4"
if [[ ! -d "$MODEL_DIR" ]]; then
  read -r -p "Download the Arabic Vosk model (~318 MB)? [y/N] " answer
  if [[ "$answer" =~ ^[Yy]$ ]]; then
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' EXIT
    curl -L --fail --retry 3 "https://alphacephei.com/vosk/models/vosk-model-ar-mgb2-0.4.zip" -o "$tmp/model.zip"
    unzip -q "$tmp/model.zip" -d "$ROOT/models"
    echo "Model installed at $MODEL_DIR"
  else
    echo "Model download skipped. Add it manually and update config/settings.json."
  fi
fi

mkdir -p "$HOME/.config/systemd/user"
mkdir -p "$HOME/.config/ghadeer-voice-assistant"
sed "s|@PROJECT_DIR@|$ROOT|g" systemd/ghadeer-voice-assistant.service > "$HOME/.config/systemd/user/ghadeer-voice-assistant.service"
systemctl --user daemon-reload
read -r -p "Enable assistant at login? [y/N] " enable
if [[ "$enable" =~ ^[Yy]$ ]]; then
  systemctl --user enable ghadeer-voice-assistant.service
  echo "Autostart enabled. Start now with: systemctl --user start ghadeer-voice-assistant.service"
fi

echo "Installation finished."
