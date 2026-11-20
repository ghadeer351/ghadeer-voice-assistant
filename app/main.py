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


def capture_from_stream(chunks, model, timeout):
    """Capture one utterance from the already-open microphone stream."""
    recognizer = KaldiRecognizer(model, 16000)
    recognizer.SetWords(False)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            chunk = next(chunks)
        except StopIteration:
            return ""
        if recognizer.AcceptWaveform(chunk):
            text = json.loads(recognizer.Result()).get("text", "").strip()
            if text:
                return text
    return json.loads(recognizer.FinalResult()).get("text", "").strip()


def main():
    parser = argparse.ArgumentParser(description="Ghadeer Voice Assistant")
    parser.add_argument("--test-mic", action="store_true", help="Recognize one short utterance")
    args = parser.parse_args()
    settings = load_settings()
    sample_rate = settings.get("sample_rate", 16000)
    model_path = ROOT / settings["model_path"]
    if not model_path.is_dir():
        raise SystemExit(
            f"Vosk model not found: {model_path}\n"
            "Run scripts/install.sh or set model_path in config/settings.json."
        )
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print("Loading local Arabic speech model...")
    model = Model(str(model_path))
    audio = SpeechInput(model, sample_rate, settings.get("input_device"))

    if args.test_mic:
        print("Speak now...")
        print("Recognized:", audio.listen_once(8))
        return

    wake_phrases = [p.strip().lower() for p in settings["wake_phrases"]]
    wake_recognizer = KaldiRecognizer(model, sample_rate)
    wake_recognizer.SetWords(False)
    speak("أنا جاهز. قل يا مساعد.", settings.get("speak_responses", True))
    logging.info("Standby. Wake phrases: %s", wake_phrases)

    # Keep one microphone stream open. Opening a second stream while the
    # standby stream is active causes device-busy errors on many Linux drivers.
    chunks = iter(audio.stream())
    try:
        for chunk in chunks:
            if not wake_recognizer.AcceptWaveform(chunk):
                continue
            heard = json.loads(wake_recognizer.Result()).get("text", "").lower().strip()
            wake_recognizer = KaldiRecognizer(model, sample_rate)
            wake_recognizer.SetWords(False)
            if not heard:
                continue
            logging.info("Standby heard: %s", heard)
            if not any(phrase in heard for phrase in wake_phrases):
                continue

            speak("تفضل، شو بدك؟", settings.get("speak_responses", True))
            command = capture_from_stream(
                chunks, model, settings.get("command_timeout_seconds", 7)
            )
            logging.info("Command: %s", command)
            if not command:
                speak("ما سمعت الأمر، جرب مرة تانية.", settings.get("speak_responses", True))
                continue

            action = match_command(command)
            if action == "lock":
                speak("متأكد بدك تقفل الشاشة؟ قل نعم للتأكيد.", settings.get("speak_responses", True))
                confirmation = capture_from_stream(chunks, model, 4).lower()
                if "نعم" not in confirmation and "yes" not in confirmation:
                    speak("ألغيت العملية.", settings.get("speak_responses", True))
                    continue

            _, message = execute(action)
            speak(message, settings.get("speak_responses", True))
            time.sleep(0.2)
    except KeyboardInterrupt:
        logging.info("Assistant stopped.")
    except Exception:
        logging.exception("Assistant crashed")
        raise


if __name__ == "__main__":
    main()
