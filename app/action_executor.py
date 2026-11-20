"""Execute only explicitly registered desktop actions; never run recognized text as shell."""
import shutil
import subprocess
import webbrowser
from pathlib import Path

APP_CANDIDATES = {
    "open_firefox": ["firefox"],
    "open_chrome": ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"],
    "open_vscode": ["code"],
    "open_files": ["nautilus"],
    "open_terminal": ["gnome-terminal", "kgx", "x-terminal-emulator"],
}

URLS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
}

def _launch(candidates):
    for candidate in candidates:
        executable = shutil.which(candidate)
        if executable:
            subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    return False

def execute(action, argument=None):
    if isinstance(action, tuple) and action[0] == "open_url":
        return webbrowser.open(action[1]), "عم افتح الرابط."
    if action in APP_CANDIDATES:
        ok = _launch(APP_CANDIDATES[action])
        return ok, "تم." if ok else "ما لقيت التطبيق مثبت عندك."
    if action == "open_home":
        subprocess.Popen(["xdg-open", str(Path.home())])
        return True, "فتحت المجلد الشخصي."
    if action == "open_downloads":
        folder = Path.home() / "Downloads"
        folder.mkdir(exist_ok=True)
        subprocess.Popen(["xdg-open", str(folder)])
        return True, "فتحت التنزيلات."
    if action == "volume_up":
        return _run_wpctl(["set-volume", "@DEFAULT_AUDIO_SINK@", "5%+"])
    if action == "volume_down":
        return _run_wpctl(["set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"])
    if action == "mute":
        return _run_wpctl(["set-mute", "@DEFAULT_AUDIO_SINK@", "1"])
    if action == "unmute":
        return _run_wpctl(["set-mute", "@DEFAULT_AUDIO_SINK@", "0"])
    if action == "screenshot":
        return _run_named(["gnome-screenshot"])
    if action == "lock":
        return _run_named(["loginctl", "lock-session"])
    return False, "ما فهمت الأمر أو أنه غير مدعوم حالياً."

def _run_wpctl(args):
    if not shutil.which("wpctl"):
        return False, "أداة التحكم بالصوت wpctl غير متوفرة."
    subprocess.Popen(["wpctl", *args], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True, "تم."

def _run_named(args):
    if not shutil.which(args[0]):
        return False, f"الأداة {args[0]} غير مثبتة."
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True, "تم."
