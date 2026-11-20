"""Microphone capture and local Vosk recognition."""
import json
import queue
import sounddevice as sd
from vosk import KaldiRecognizer


class SpeechInput:
    def __init__(self, model, sample_rate: int = 16000, device=None):
        self.model = model
        self.sample_rate = sample_rate
        self.device = device
        self.audio_queue = queue.Queue()

    def _callback(self, indata, frames, time_info, status):
        if status:
            print(f"[audio] {status}")
        self.audio_queue.put(bytes(indata))

    def listen_once(self, timeout: float = 7.0) -> str:
        recognizer = KaldiRecognizer(self.model, self.sample_rate)
        recognizer.SetWords(False)
        self.audio_queue = queue.Queue()
        import time
        started = time.monotonic()
        last_audio = started
        parts = []
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            device=self.device,
            dtype="int16",
            channels=1,
            callback=self._callback,
        ):
            while time.monotonic() - started < timeout:
                try:
                    data = self.audio_queue.get(timeout=0.35)
                except queue.Empty:
                    continue
                last_audio = time.monotonic()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result()).get("text", "")
                    if result:
                        parts.append(result)
                        break
            if not parts:
                final = json.loads(recognizer.FinalResult()).get("text", "")
                if final:
                    parts.append(final)
        return " ".join(parts).strip()

    def flush(self):
        """Discard queued audio, such as the assistant's own spoken prompt."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def stream(self):
        """Yield microphone chunks for always-on wake phrase detection."""
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=4000,
            device=self.device,
            dtype="int16",
            channels=1,
            callback=self._callback,
        ):
            while True:
                yield self.audio_queue.get()
