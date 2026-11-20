"""Small allowlisted Arabic/English command router."""
import re
from urllib.parse import urlparse

ALIASES = {
    "open_firefox": ["افتح فايرفوكس", "افتح المتصفح", "open firefox", "open browser"],
    "open_chrome": ["افتح كروم", "open chrome"],
    "open_vscode": ["افتح في اس كود", "افتح vscode", "open vscode", "open code"],
    "open_files": ["افتح الملفات", "افتح مدير الملفات", "open files", "open file manager"],
    "open_terminal": ["افتح الطرفية", "افتح التيرمنال", "open terminal"],
    "open_home": ["افتح المجلد الشخصي", "افتح الرئيسية", "open home folder"],
    "open_downloads": ["افتح التنزيلات", "افتح التحميلات", "open downloads"],
    "volume_up": ["ارفع الصوت", "علي الصوت", "volume up", "increase volume"],
    "volume_down": ["وطي الصوت", "خفض الصوت", "volume down", "decrease volume"],
    "mute": ["اكتم الصوت", "اسكت الصوت", "mute sound", "mute"],
    "unmute": ["شغل الصوت", "الغاء كتم الصوت", "unmute sound", "unmute"],
    "screenshot": ["خذ لقطة شاشة", "صور الشاشة", "screenshot", "take a screenshot"],
    "lock": ["اقفل الشاشة", "قفل الشاشة", "lock screen"],
    "help": ["شو بتعمل", "ساعدني", "help", "what can you do"],
}

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[ًٌٍَُِّْـ]", "", text)
    text = re.sub(r"[أإآ]", "ا", text)
    text = re.sub(r"\s+", " ", text)
    return text

def match_command(text: str):
    normalized = normalize(text)
    for command, phrases in ALIASES.items():
        if any(normalize(phrase) in normalized for phrase in phrases):
            return command
    if normalized.startswith(("افتح ", "open ")):
        candidate = normalized.split(" ", 1)[1].strip()
        if candidate.startswith(("http://", "https://")):
            parsed = urlparse(candidate)
            if parsed.scheme in ("http", "https") and parsed.netloc:
                return ("open_url", candidate)
    return None
