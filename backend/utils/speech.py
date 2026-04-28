from pathlib import Path
from uuid import uuid4

from gtts import gTTS

from utils.config import AUDIO_DIR


def text_to_speech(text: str, language: str = "en") -> Path:
    output_path = AUDIO_DIR / f"{uuid4().hex}.mp3"
    tts = gTTS(text=text, lang=language)
    tts.save(str(output_path))
    return output_path
