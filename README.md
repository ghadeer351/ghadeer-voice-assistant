# Ghadeer Voice Assistant

A lightweight, local-first voice assistant for Ubuntu. The first milestone focuses on a safe, practical desktop assistant that waits for the Arabic wake phrase **"يا مساعد"**, listens for one command, performs an allowlisted action, speaks a short response, then returns to standby.

> **Status: early MVP / hardware testing required.** Arabic wake-word accuracy (especially Syrian colloquial speech), microphone compatibility, and CPU/battery impact must be tested on the target laptop. No battery percentage or recognition accuracy is promised.

## Design goals

- Local speech recognition with Vosk; no cloud API and no audio upload.
- Arabic wake phrase and Arabic/English command aliases.
- Low-complexity Python application suitable for older Ubuntu laptops.
- Explicit allowlist of actions. Recognized speech is **never** passed to a shell.
- User-level systemd service; no root daemon.
- No audio recordings saved by default.

## Current MVP commands

- Open Firefox, Chrome, VS Code, Files, or Terminal (when installed).
- Open YouTube, Google, GitHub, or a validated HTTPS/HTTP URL.
- Volume up/down, mute/unmute (requires `wpctl`).
- Open Home or Downloads.
- Take a screenshot (requires `gnome-screenshot`).
- Lock the screen (confirmation required).

Commands are intentionally limited. More actions can be added through the command registry.

## Requirements

- Ubuntu desktop session (GNOME recommended), Python 3.10+.
- Working microphone and speakers.
- About 350 MB free for the recommended Arabic Vosk model, plus Python dependencies.
- Packages: `python3-venv`, `python3-pip`, `portaudio19-dev`, `espeak-ng`, `alsa-utils`, `curl`, `unzip`.

The default Arabic model is `vosk-model-ar-mgb2-0.4` (approximately 318 MB). It is not a purpose-built wake-word model and may not reliably recognize every Syrian accent or the phrase in noisy rooms. If it performs poorly, use the manual trigger mode described below rather than assuming the wake word works.

## Install

Clone the repository, then run:

```bash
git clone https://github.com/ghadeer351/ghadeer-voice-assistant.git
cd ghadeer-voice-assistant
chmod +x scripts/install.sh
./scripts/install.sh
```

The installer creates a virtual environment, installs Python packages, downloads the Arabic model after confirmation, and asks whether to enable autostart. It does not use sudo to install a system service.

Then edit `config/settings.json` if needed and start:

```bash
systemctl --user start ghadeer-voice-assistant.service
journalctl --user -u ghadeer-voice-assistant.service -f
```

To stop it:

```bash
systemctl --user stop ghadeer-voice-assistant.service
```

## Microphone / model test

```bash
.venv/bin/python -m app.main --test-mic
```

Say a short sentence and check that the microphone level and speech recognition work. The first run may need microphone permission or a different input device. Use `arecord -l` to inspect audio devices.

## Battery and resource note

Continuous wake-word listening still consumes CPU and energy. This MVP uses one Vosk recognizer in standby and does not load a second large model after the wake phrase. Actual CPU/RAM/battery impact depends on the laptop, audio driver, model, and microphone. Measure it on your machine before enabling autostart permanently. A future low-power wake-word engine can replace the detector behind the same interface.

## Safety

- Only predefined actions can execute.
- No `os.system`, shell command construction, or arbitrary terminal command execution.
- URL opening accepts only HTTP/HTTPS URLs.
- Locking the screen requires a spoken confirmation.
- The assistant does not listen for commands until it detects the wake phrase.

## Configuration

Edit `config/settings.json` to change the wake phrase, model directory, input device, language, and command timeout. Keep the model directory outside Git; downloaded model files are ignored.

## Uninstall

```bash
./scripts/uninstall.sh
```

This removes the user service and local virtual environment/model only after asking for confirmation.

## License

MIT. See [LICENSE](LICENSE).

## Model information

Vosk model catalogue: https://alphacephei.com/vosk/models
