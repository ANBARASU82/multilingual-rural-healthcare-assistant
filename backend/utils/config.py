from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CHECKPOINT_DIR = BASE_DIR / "model" / "checkpoints" / "distilbert-disease"
UPLOAD_DIR = BASE_DIR / "uploads"
AUDIO_DIR = BASE_DIR / "generated_audio"

SUPPORTED_LANGUAGES = {
    "en": "english",
    "hi": "hindi",
    "ta": "tamil",
}

UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
