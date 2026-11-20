"""Ghadeer Voice Assistant - local wake phrase loop."""
import argparse
import json
import logging
import time
from pathlib import Path

from vosk import Model, KaldiRecognizer

from app.speech import SpeechInput
from app.command_processor import match_command
from app.action_executor import execute
from app.voice_feedback import speak

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "settings.json"

def load_settings():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

def main():
    parser = argparse.ArgumentParser(description="Ghadeer Voice Assistant")
    parser.add_argument("--test-mic", action="store_true", help="Recognize one short utterance")
    args = parser.parse_args()
    settings = load_settings()
    model_path = ROOT / settings["model_path"]
    if not model_path.is_dir():
        raise SystemExit(
            f"Vosk model not found: {model_path}\n"
            "Run scripts/install.sh or set model_path in config/settings.json."
        )
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print("Loading local Arabic speech model...")
    model = Model(str(model_path))
    audio = SpeechInput(model, settings.get("sample_rate", 16000), settings.get("input_device"))
    if args.test_mic:
        print("Speak now...")
        print("Recognized:", audio.listen_once(8))
        return

    wake_phrases = [p.strip().lower() for p in settings["wake_phrases"]]
    recognizer = KaldiRecognizer(model, settings.get("sample_rate", 16000))
    recognizer.SetWords(False)
    speak("أنا جاهز. قل يا مساعد.", settings.get("speak_responses", True))
    logging.info("Standby. Wake phrases: %s", wake_phrases)
    try:
        for chunk in audio.stream():
            if recognizer.AcceptWaveform(chunk):
                text = json.loads(recognizer.Result()).get("text", "").lower().strip()
                if not text:
                    continue
                logging.info("Heard: %s", text)
                if any(phrase in text for phrase in wake_phrases):
                    speak("تفضل، شو بدك؟", settings.get("speak_responses", True))
                    command = audio.listen_once(settings.get("command_timeout_seconds", 7))
                    logging.info("Command: %s", command)
                    if not command:
                        speak("ما سمعت الأمر، جرب مرة تانية.", settings.get("speak_responses", True))
                    else:
                        action = match_command(command)
                        if action == "lock":
                            speak("متأكد بدك تقفل الشاشة؟ قل نعم للتأكيد.", settings.get("speak_responses", True))
                            confirmation = audio.listen_once(4)
                            if "نعم" not in confirmation and "yes" not in confirmation.lower():
                                speak("ألغيت العملية.", settings.get("speak_responses", True))
                                continue
                        ok, message = execute(action)
                        speak(message, settings.get("speak_responses", True))
                    recognizer = KaldiRecognizer(model, settings.get("sample_rate", 16000))
                    recognizer.SetWords(False)
                    time.sleep(0.25)
    except KeyboardInterrupt:
        logging.info("Assistant stopped.")
    except Exception:
        logging.exception("Assistant crashed")
        raise

if __name__ == "__main__":
    main()
