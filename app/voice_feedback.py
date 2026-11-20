"""Offline speech feedback using the system espeak-ng executable."""
import shutil
import subprocess


def speak(message: str, enabled: bool = True) -> None:
    if not enabled or not message:
        return
    executable = shutil.which("espeak-ng") or shutil.which("espeak")
    if not executable:
        print(f"[assistant] {message}")
        return
    # espeak-ng is invoked with a fixed executable and argument list; no shell.
    try:
        subprocess.run(
            [executable, "-v", "ar", message],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=12,
        )
    except (OSError, subprocess.TimeoutExpired):
        print(f"[assistant] {message}")
